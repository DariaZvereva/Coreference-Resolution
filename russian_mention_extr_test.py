from natasha import NamesExtractor, DatesExtractor, MoneyExtractor
import codecs
import bisect
from Russian import documents
from Russian import corpora
import spans
import logging
from Russian import mention_extractor

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

names = mention_extractor.extract_system_mentions_names(doc)
pronouns = mention_extractor.extract_system_pronoun_mentions(doc)
np = mention_extractor.extract_system_np_mentions(doc)

print("Names")
for men in names:
    print([a["Text"] if "Text" in a else "" for a in men.document.tokens_properties[men.span.begin:men.span.end+1]])
print("Pronouns")
for men in pronouns:
    print([a["Text"] for a in men.document.tokens_properties[men.span.begin:men.span.end + 1]])
print("NP")
for men in np:
    print([a["Text"] for a in men.document.tokens_properties[men.span.begin:men.span.end+1]])


print("Success")

