import spans
import nltk

class OpenCorporaTags(object):

    POST = {"NOUN", "ADJF", "ADJS", "COMP", "VERB", "INFN", "PRTF", "PRTS", "GRND", "NUMR", "ADVB", "NPRO", "PRED",
            "PREP", "CONJ", "PRCL", "INTJ"} #часть речи
    ANim = {"anim", "inan"} #одушевленнсть
    GNdr = {"masc", "femn", "neut", "ms-f"} #пол
    NMbr = {"sing", "plur"} #число
    CAse = {"nomn", "gent", "datv", "accs", "ablt", "loct", "voct", "gen1", "gen2", "acc2", "loc1", "loc2"} #падеж
    ASpc = {"perf", "impf"} #категория вида (совершенный/несовершенный)
    TRns = {"tran", "intr"} #категория переходности
    PErs = {"1per", "2per", "3per"} #лицо
    TEns = {"pres", "past", "futr"} #время
    properties = {"POS": POST, "Anim": ANim, "Gndr": GNdr, "Nmbr": NMbr, "Case": CAse, "Aspc": ASpc, "Trns": TRns, "Pers": PErs, "Tens": TEns}
    tags = []

    def __init__(self, morph_tags):
        self.tags = list(morph_tags.strip().split(","))

    def get_properties(self):
        morph_prop = {}
        for tag in self.tags:
            for key in self.properties.keys():
                if tag in self.properties[key]:
                    morph_prop[key] = tag
        return morph_prop

def get_relevant_parented_subtree(span, document):
    """ Get the parented fragment of the parse tree and the input span.

    Args:
        span (Span): A span in a document.
        document (CoNLLDocument): A document.

    Returns:
        nltk.ParentedTree: The parented fragment of the parse tree at the span in the
        document.
    """
    in_sentence_ids = document.in_sentence_ids[span.begin:span.end + 1]
    in_sentence_span = spans.Span(in_sentence_ids[0], in_sentence_ids[-1])

    sentence_id, sentence_span = document.get_sentence_id_and_span(span)

    sentence_tree = nltk.ParentedTree.fromstring(str(document.parse[sentence_id]))

    spanning_leaves = sentence_tree.treeposition_spanning_leaves(
        in_sentence_span.begin, in_sentence_span.end + 1)
    mention_subtree = sentence_tree[spanning_leaves]

    if mention_subtree in sentence_tree.leaves():
        mention_subtree = sentence_tree[spanning_leaves[:-2]]

    return mention_subtree