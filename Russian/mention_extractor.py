from natasha import NamesExtractor
from Russian import documents
import bisect
from Russian import mentions
from spans import Span


def extract_system_mentions_names(document):
    if document is None:
        return []
    extractor = NamesExtractor()
    matches = extractor(document.text)
    name_mentions = []
    for match in matches:
        start, stop = match.span
        assert start in document.offsets
        begin_span = document.span_by_offset[start]
        end_span = document.span_by_offset[document.offsets[bisect.bisect_right(document.offsets, stop)]]
        attributes = {}
        first = match.fact.first
        if first is not None:
            attributes["head"] = first
        name_mentions.append(mentions.Mention(document, Span(begin_span, end_span-1)))
    return name_mentions


def extract_system_np_mentions(document):
    if document is None:
        return []
    np_mentions = []

'''
def get_subtree_span(subtree_root, span, visited):
    visited[subtree_root] = True
    if subtree_root not in self.children or len(self.children[subtree_root]) == 0:
        sp1 = spans.Span(subtree_root, subtree_root)
        print("[", subtree_root, "]")
        # print(sp1, span)
        span = span.unite(sp1)
        return span
    print(subtree_root, self.children[subtree_root])
    for child in self.children[subtree_root]:
        if not visited[child]:
            sp2 = self.get_np_span(child, span, visited)
        # print(sp2, span)
        span = span.unite(sp2)
    return span
'''


def extract_system_pronoun_mentions(document):
    if document is None:
        return []
    pro_mentions = []
    for i in range(len(document.tokens)):
        if document.syntpar[i] == "Pronoun(106178)":
            pro_mentions.append(mentions.Mention(document, Span(i, i)))
    return pro_mentions




