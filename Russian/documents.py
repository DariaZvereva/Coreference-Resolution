import spans
from Russian import mentions

class Document(object):
    """Represents a document.

    Attributes:
        identifier (str): A unique identifier for the document.
        tokens (list(str)): All tokens.
        morph_tags (list(str)): All morphological tags.
        ner (list(str)): All named entity tags (if a token does not have a
            tag, the tag is set to NONE).
        coref (dict(span, int)): A mapping of mention spans to their
            coreference set id.
        annotated_mentions list(Mention): All annotated mentions.
        system_mentions list(Mention): The system mentions (initially empty).
    """
    def __init__(self, identifier, tokens_information, coref, text=""):
        """ Construct a document from tokens and coreference information.

        Args:
            identifier (str): A unique identifier for the document.
            tokens_information(list(str)): A list of tokens information. The ith item
                contains information about the ith token. We assume that
                each ``tokens_information[i]`` is a 6-tuple
                ``offset, token, morph_tags, id_sem_class, syntpar, id_mention (if exists)``, where

                * tokens (list(str)): All tokens in the sentence.
                * offsets (list): All offsets in the documents.
                * morph_tags
                *
            coref (dict(span, int)): A mapping of mention spans to their
            coreference set id.
        """
        self.identifier = identifier
        self.offsets = []
        self.tokens = []
        self.morph_tags = []
        self.sem_class_ids = []
        self.syntpar = []
        self.mentions_ids = []
        self.coref = coref
        self.span_by_offset = {} #сопоставляет каждому offset span соответствующий токену
        self.text = text

        for inf in tokens_information:

            offset, token, morph_tag, id_sem_class, syntpar, id_mention = inf.split("\t")

            self.tokens.append(token)
            self.offsets.append(int(offset))
            self.morph_tags.append(morph_tag.split(","))
            self.sem_class_ids.append(id_sem_class)
            self.syntpar.append(syntpar)
            self.mentions_ids.append(id_mention)
            self.span_by_offset[int(offset)] = len(self.tokens) - 1

        #self.annotated_mentions = self.__get_annotated_mentions()
        self.system_mentions = []


    def __get_annotated_mentions(self):
        mention_spans = sorted(list(self.coref.keys()))

        seen = set()

        annotated_mentions = []

        for span in mention_spans:
            set_id = self.coref[span]
            annotated_mentions.append(
                mentions.Mention.from_document(
                    span, self, first_in_gold_entity=set_id not in seen
                )
            )
            seen.add(set_id)

        return annotated_mentions



class Document_from_NLC(object):
    """Represents a document.

    Attributes:
        identifier (str): A unique identifier for the document.
        tokens (list(str)): All tokens.
        morph_tags (list(str)): All morphological tags.
        ner (list(str)): All named entity tags (if a token does not have a
            tag, the tag is set to NONE).
        coref (dict(span, int)): A mapping of mention spans to their
            coreference set id.
        annotated_mentions list(Mention): All annotated mentions.
        system_mentions list(Mention): The system mentions (initially empty).
    """

    SP_NOUN = "Noun(7)"
    SP_PRONOUN = "Pronoun(106178)"
    SP_CONJ = "Conjunction(805)"
    SP_INV = "Invariable(1600)"
    SP_PREP = "Preposition(772)"
    SP_ADV = "Adverb(40)"
    SP_ADJPRO = "AdjectivePronoun(851)"
    SP_POSESSPRO = "PossessivePronoun(2075)"
    SP_ADVPRO = "AdverbialPronoun(1887)"

    SERVICE_POS = {SP_CONJ, SP_INV, SP_PREP, SP_ADV, SP_ADVPRO}

    def __init__(self, identifier, tokens_information, coref, text=""):
        """ Construct a document from tokens and coreference information.

        Args:
            identifier (str): A unique identifier for the document.
            tokens_information(list(str)): A list of tokens information. The ith item
                contains information about the ith token. We assume that
                each ``tokens_information[i]`` is a 6-tuple
                ``offset, token, morph_tags, id_sem_class, syntpar, id_mention (if exists)``, where

                * tokens (list(str)): All tokens in the sentence.
                * offsets (list): All offsets in the documents.
                * morph_tags
                *
            coref (dict(span, int)): A mapping of mention spans to their
            coreference set id.
        """
        self.identifier = identifier
        self.tokens_properties = []
        self.span_by_offset = {} #сопоставляет каждому offset span соответствующий токену
        self.text = text
        self.offsets = []
        self.children = {}  # for every noun write their children (spans)

        for inf in tokens_information:
            info = inf.split()
            d = {}
            for prop in info:
                d[prop.split("=")[0]] = prop.split("=")[-1]
            self.tokens_properties.append(d)

            if "Offset" in self.tokens_properties[-1]:
                self.span_by_offset[int(self.tokens_properties[-1]["Offset"])] = len(self.tokens_properties) - 1
                self.offsets.append(int(self.tokens_properties[-1]["Offset"]))
            else:
                self.offsets.append(int(self.tokens_properties[-2]["Offset"]))

        for prop in self.tokens_properties:
            if "ParentOffset" in prop and prop["ParentOffset"] is not None and "Offset" in prop and \
                            prop["Offset"] is not None:
                if self.span_by_offset[int(prop["ParentOffset"])] not in self.children:
                    self.children[self.span_by_offset[int(prop["ParentOffset"])]] = \
                        [self.span_by_offset[int(prop["Offset"])]]
                else:
                    self.children[self.span_by_offset[int(prop["ParentOffset"])]].append(
                        self.span_by_offset[int(prop["Offset"])])
            if "Offset" in prop and prop["Offset"] is not None and \
                            self.span_by_offset[int(prop["Offset"])] not in self.children:
                self.children[self.span_by_offset[int(prop["Offset"])]] = []

        self.system_mentions = []

    def get_subtree_span(self, subtree_root, span, without_serv=True):
        if subtree_root not in self.children or len(self.children[subtree_root]) == 0:
            sp1 = spans.Span(subtree_root, subtree_root)
            span = span.unite(sp1)
            return span
        for child in self.children[subtree_root]:
            if not (without_serv and self.tokens_properties[child]["SP"] in self.SERVICE_POS):
                sp2 = self.get_subtree_span(child, span, without_serv=False)
                span = span.unite(sp2)
        return span