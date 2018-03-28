from Russian import documents
from Russian import corpora
import logging
from Russian import mention_extractor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(''message)s')
logger = logging.getLogger(__name__)


logger.info("Reading in data.")

path = "C:/Users/dzvereva/Desktop/Article/data"

training_corpus = corpora.Corpus.by_path("training", path)
logging.info("Corpus is ready")

logging.info("Extracting system mentions.")
dummy_counter_for_train = 0

# print children
# print("\n".join(list(map(str, [str(a)+":"+str(training_corpus.documents[0].children[a])
# for a in sorted(training_corpus.documents[0].children.keys())]))))

for doc in training_corpus.documents:
    #if dummy_counter_for_train % 100 == 99:
    logging.info("We are extracting doc " + str(dummy_counter_for_train) + ": " + str(doc.identifier))
    dummy_counter_for_train += 1
    doc.system_mentions = mention_extractor.extract_system_mentions(doc)

doc = training_corpus.documents[0]
doc.system_mentions = mention_extractor.extract_system_mentions(doc)
for line in doc.system_mentions:
    print(line)

'''
doc = training_corpus.doc_map[2]
text = doc.text
print(text)

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
'''
#print(doc.)

print("Success")

