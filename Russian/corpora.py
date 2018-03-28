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
        self.doc_map = {} #сопоставляет документ его идентификатору
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

        paths = {}
        # texts
        for root, dirs, files in os.walk(path+"/texts"):
            for name in files:
                i = int(name.split("_")[1])
                paths[i] = [join(root, name)]
        # morph information from pymorphy
        for root, dirs, files in os.walk(path + "/corpus/morph"):
            for name in files:
                i = int(splitext(name)[0].split("_")[1])
                if i in paths.keys():
                    paths[i].append(join(root, name))
        # compreno information
        for root, dirs, files in os.walk(path + "/corpus/sem_synt_po"):
            for name in files:
                i = int(splitext(name)[0].split("_")[1])
                if i in paths.keys():
                    paths[i].append(join(root, name))
        corpus_documents = []
        for i in paths:
            if len(paths[i]) < 3:
                continue
            file = open(paths[i][0], mode="r", encoding="utf-8")
            text = file.read()
            file.close()
            file = open(paths[i][1], mode="r", encoding="utf-8")
            morph_inf = file.readlines()
            file.close()
            file = open(paths[i][2], mode="r", encoding="utf-8")
            compreno_inf = file.readlines()
            file.close()
            # information about document
            inf = []
            j = 0
            sent_num = 0
            for morph in morph_inf:
                # в корпусе пустые строки между предложениями
                if morph.strip() == '':
                    sent_num += 1
                else:
                    number, offset, length, token, lemma, pymorph, chain, mention = morph.strip().split("\t")
                    compr_offset, parent_offset, sem_class, synt_par = "-", "-", "-", "-"
                    if pymorph != "PNCT" and j < len(compreno_inf) and compreno_inf[j].strip().split("\t")[0] == offset:
                        while j < len(compreno_inf) and compreno_inf[j].strip().split("\t")[0] == offset:
                            if not len(compreno_inf[j].strip().split("\t")) == 5:
                                compreno_inf[j] = compreno_inf[j].strip()+"\tNA"
                            compr_offset, compr_token, p_o, sem_class, synt_par = \
                                compreno_inf[j].strip().split("\t")
                            if p_o == "NA" or int(p_o) < int(offset) or int(p_o) > int(offset) + int(length):
                                parent_offset = p_o
                            j += 1
                    inf.append("\t".join([number, offset, str(sent_num), length, token, lemma, parent_offset,
                                          pymorph, sem_class, synt_par, chain, mention]))
            doc = documents.Document(i, inf, None, text)
            corpus_documents.append(doc)
            dummy_counter += 1
            if dummy_counter % 100 == 99:
                logger.info("\tReading: " + str(dummy_counter))

        logger.info("\tWe are done reading\n")
        return Corpus(description, corpus_documents)

