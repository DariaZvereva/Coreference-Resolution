import os
from os.path import join, splitext
from Russian import documents
import logging

logger = logging.getLogger(__name__)

class Corpus:
    """Represents a text collection (a corpus) as a list of documents.

    Such a text collection can also be read from data, and be supplemented with
    antecedent information.

    Attributes:
        description(str): A human-readable description of the corpus.
        documents (list(Document)): A list of CoNLL documents.
    """

    def __init__(self, description, corpus_documents):
        """Construct a Corpus from a description and a list of documents.

        Args:
            description (str): A human-readable description of the corpus.
            documents (list(Document)): A list of documents.
        """
        self.description = description
        self.documents = corpus_documents
        self.doc_map = {}
        self.path = ""
        for doc in self.documents:
            self.doc_map[doc.identifier] = doc

    def __iter__(self):
        """Return an iterator over documents in the corpus.

        Returns:
            An iterator over CoNLLDocuments.
        """
        return iter(self.documents)

    @staticmethod
    def by_path(description, path):
        """Construct a Corpus from a path to directory with documents.

        Args:
            path (str): path to the directory.
        """

        if path is None:
            return []

        """
        Dummy counter
        Writes a line every 100 documents
        """

        dummy_counter = 0

        paths_to_texts = {}
        paths_to_corp = {}
        for root, dirs, files in os.walk(path+"/texts"):
            for name in files:
                i = int(name.split("_")[1])
                paths_to_texts[i] = join(root, name)
        for root, dirs, files in os.walk(path + "/corpus"):
            for name in files:
                i = int(splitext(name)[0].split("_")[1])
                paths_to_corp[i] = join(root, name)
                if i not in paths_to_texts:
                    print("Text with identifier", i, "is not found.")
        assert len(paths_to_texts) == len(paths_to_corp)

        corpus_documents = []
        for i in paths_to_corp:
            if i not in paths_to_texts:
                print("Information about text with identifier", i, "is not found.")
            file = open(paths_to_corp[i], mode="r", encoding="utf-8")
            inf = file.readlines()
            file.close()
            file = open(paths_to_texts[i], mode="r", encoding="utf-8")
            text = file.read()
            file.close()
            doc = documents.Document(i, inf, None, text)
            corpus_documents.append(doc)
            dummy_counter += 1
            if dummy_counter % 100 == 99:
                logger.info("\tReading: " + str(dummy_counter))

        logger.info("\tWe are done reading\n")
        return Corpus(description, corpus_documents)

