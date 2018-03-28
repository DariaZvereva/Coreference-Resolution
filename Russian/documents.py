import spans
from Russian import mentions
from bisect import bisect_left

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
    SP_NOUN = 7
    SP_PRONOUN = 106178
    SP_CONJ = 805
    SP_INV = 1600
    SP_PREP = 772
    SP_ADV = 40
    SP_ADJPRO = 851
    SP_POSESSPRO = 2075
    SP_ADVPRO = 1887

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
        self.span_by_offset = {}  # сопоставляет каждому offset span соответствующий токену
        self.text = text
        self.offsets = []
        self.children = {}  # for every noun write their children (spans)
        self.system_mentions = [] #содержит номера mention-ов в массиве tokens_properties

        for inf in tokens_information:

           # print(inf.split("\t"))
            number, offset, sent_num, length, token, lemma, parent_offset, morph_tags, id_sem_class, id_syntpar, id_chain, \
                id_mention = inf.split("\t")
            prop = {}
            prop["NumberInCorpora"] = number
            prop["Offset"] = int(offset)
            prop["Sentence"] = int(sent_num)
            prop["Token"] = token
            prop["Length"] = length
            prop["Lemma"] = lemma
            if parent_offset not in {"-", "NA"}:
                prop["ParentOffset"] = int(parent_offset)
            if id_sem_class not in {"-", "NA", ""}:
                prop["SemClass"] = int(id_sem_class)
            if id_syntpar not in {"-", "NA"}:
                prop["SyntParadigm"] = int(id_syntpar)
            if not id_chain == "-":
                prop["Chain"] = id_chain

            if not id_mention == "-":
                prop["Mention"] = id_mention
                self.system_mentions.append(len(self.tokens_properties))
            prop["Morph"] = morph_tags
            # выкинем из рассмотрения пунктуацию
            if prop["Morph"] != 'PNCT':
                self.tokens_properties.append(prop)
                # оффсет - это посимвольный сдвиг
                self.offsets.append(int(offset))
                # span по сути - номер токена в документе
                self.span_by_offset[int(offset)] = len(self.tokens_properties) - 1

        # проверка на то, что данные из корпуса собираются хорошо
        '''if str(identifier) == '2':
            print("\n".join(tokens_information))
            print("\n".join([str(a)+":"+str(self.span_by_offset[a]) for a in sorted(self.span_by_offset.keys())]))
        '''

        for prop in self.tokens_properties:
            if "ParentOffset" in prop:
                if not prop["ParentOffset"] in self.offsets:

                    #if not (prop["ParentOffset"] == self.offsets[bisect_left(self.offsets, int(prop["ParentOffset"])) - 1]):
                    #    print("!", prop["ParentOffset"], self.offsets[bisect_left(self.offsets, int(prop["ParentOffset"])) - 1])
                    #    print(prop)

                    prop["ParentOffset"] = self.offsets[bisect_left(self.offsets, int(prop["ParentOffset"])) - 1]
                if self.span_by_offset[int(prop["ParentOffset"])] not in self.children:
                    self.children[self.span_by_offset[int(prop["ParentOffset"])]] = \
                        [self.span_by_offset[int(prop["Offset"])]]
                else:
                    self.children[self.span_by_offset[int(prop["ParentOffset"])]].append(
                        self.span_by_offset[int(prop["Offset"])])
            if self.span_by_offset[int(prop["Offset"])] not in self.children:
                self.children[self.span_by_offset[int(prop["Offset"])]] = []

        #self.annotated_mentions = self.__get_annotated_mentions()


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

    def get_subtree_span(self, subtree_root, span, visited, without_serv=True):
        #включаем последний флаг, если хотим убрать служебные части речи на первом уровне поддерева
        if subtree_root not in self.children or len(self.children[subtree_root]) == 0 or visited[subtree_root]:
            sp1 = spans.Span(subtree_root, subtree_root)
            span = span.unite(sp1)
            return span
        #print(subtree_root, self.children[subtree_root])
        visited[subtree_root] = True
        for child in self.children[subtree_root]:
            if not (without_serv and self.tokens_properties[child]["SyntParadigm"] in self.SERVICE_POS):
                #print(child)
                sp2 = self.get_subtree_span(child, span, visited, without_serv=False)
                span = span.unite(sp2)
        return span


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

    def get_subtree_span(self, subtree_root, span, visited, without_serv=True):
        if subtree_root not in self.children or len(self.children[subtree_root]) == 0 or visited[subtree_root]:
            sp1 = spans.Span(subtree_root, subtree_root)
            span = span.unite(sp1)
            return span
        visited[subtree_root] = True
        for child in self.children[subtree_root]:
            if not (without_serv and self.tokens_properties[child]["SP"] in self.SERVICE_POS):
                sp2 = self.get_subtree_span(child, span, visited, without_serv=False)
                span = span.unite(sp2)
        return span