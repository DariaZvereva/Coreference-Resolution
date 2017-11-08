from natasha import NamesExtractor, DatesExtractor, MoneyExtractor
import codecs
import bisect
from Russian import documents
from Russian import corpora
import spans
import logging

logger = logging.getLogger(__name__)


logger.info("Reading in data.")

path = "C:/Users/DZvereva/Documents/Article/data"

training_corpus = corpora.Corpus.by_path("training", path)
print("Corpus is ready")


doc = training_corpus.doc_map[2]
text = doc.text

f = open("C:/Users/DZvereva/Desktop/book_2_from_open_corpora_2.csv", "r", encoding="utf-8")
doc = documents.Document_from_NLC("NLC doc", f.readlines(), None, text)
f.close()

"""
for prop in properties:
    if "Offset" in prop:
        if not (prop["Text"] == doc.tokens[doc.span_by_offset[int(prop["Offset"])]]):
            print(prop["Text"], "!=", doc.tokens[doc.span_by_offset[int(prop["Offset"])]])

"""

for i in range(len(doc.tokens_properties)):
    if "SP" in doc.tokens_properties[i]:
        if doc.tokens_properties[i]["SP"] == doc.SP_NOUN and i in doc.children:
            print(i, "=============")#, doc.tokens_properties[i], doc.tokens_properties[
                #doc.span_by_offset[int(doc.tokens_properties[i]["Offset"])]])
            np = doc.get_subtree_span(i, spans.Span(i, i))
            print(np)
            print([a["Text"] for a in doc.tokens_properties[np.begin:np.end+1]])
            print("-------------------")
"""
for i in range(131, 163):
    #print(i)
    if int(doc.tokens_properties[i]["Offset"]) == 1048:
        print(doc.tokens_properties[i]["ParentOffset"])
        print(doc.tokens_properties[i]["Offset"])
print(doc.tokens_properties[int(doc.span_by_offset[1117])])
print(doc.tokens_properties[int(doc.span_by_offset[1048])])
print(doc.tokens_properties[int(doc.span_by_offset[1150])])
#np = doc.get_np_span(144, spans.Span(144, 144))
#print(doc.span_by_offset[1117])
#print(doc.tokens_properties[154])
print(doc.text[949: 1180])"""

print("Success")

