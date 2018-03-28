import logging
import codecs

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(''message)s')

from English import corpora
from English import mention_extractor

print("Start!")

logging.info("Reading in data.")
training_corpus = corpora.Corpus.from_file("training", codecs.open("E:\\buML\\cort\\data\\sets\\short_new_train_compreno.gold", "r", "utf-8"))
print("Read")
logging.info("Extracting system mentions.")
dummy_counter_for_train = 0
for doc in training_corpus:
    if dummy_counter_for_train % 100 == 99:
        logging.info("We are extracting doc " + str(dummy_counter_for_train) + ": " + doc.identifier)
    dummy_counter_for_train += 1
    doc.system_mentions = mention_extractor.extract_system_mentions(doc)