from natasha import NamesExtractor
from Russian import documents
import bisect
from Russian import mentions
from spans import Span


def extract_system_mentions(document, filter_mentions=True):
    system_mentions = []
    names = extract_system_mentions_names(document)
    system_mentions.extend(names)
    np = extract_system_np_mentions(document)
    system_mentions.extend(np)
    pro = extract_system_pronoun_mentions(document)
    system_mentions.extend(pro)
    return system_mentions


def extract_system_mentions_names(document):
    if document is None:
        return []
    extractor = NamesExtractor()
    matches = extractor(document.text)
    name_mentions = []
    for match in matches:
        start, stop = match.span
        begin_span = document.span_by_offset[start]
        end_span = document.span_by_offset[document.offsets[bisect.bisect_right(document.offsets, stop)]]

        attributes = {}
        first = match.fact.first
        if first is not None:
            attributes["head"] = first
        name_mentions.append(mentions.Mention(document, Span(begin_span, end_span-1), attributes))
    return name_mentions


def extract_system_np_mentions(document):
    if document is None:
        return []
    np_mentions = []
    for span in range(len(document.tokens_properties)):
        if "SyntParadigm" in document.tokens_properties[span]:
            if document.tokens_properties[span]["SyntParadigm"] == document.SP_NOUN and span in document.children:
                visited = [False for i in range(len(document.offsets))]
                np = document.get_subtree_span(span, Span(span, span), visited)
                attributes = {"head_span_in_document": span, "span_in_mention": span - np.begin}
                np_mentions.append(mentions.Mention(document, np, attributes))
    return np_mentions


def extract_system_pronoun_mentions(document):
    if document is None:
        return []
    pro_mentions = []
    for span in range(len(document.tokens_properties)):
        if "SyntParadigm" in document.tokens_properties[span] and \
                        document.tokens_properties[span]["SyntParadigm"] == document.SP_PRONOUN:
            pro_mentions.append(mentions.Mention(document, Span(span, span), {}))
    return pro_mentions




