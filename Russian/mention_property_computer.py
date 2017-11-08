import spans
import nltk

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