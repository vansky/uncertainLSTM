import os
import torch
import dill
import gzip

from nltk import sent_tokenize

class convertvocab(object):
    def __init__(self, load_from, save_to):
        self.dictionary = Dictionary()
        self.loadme = self.load_dict(load_from)
        self.save_to = self.save_dict(save_to)

    def save_dict(self, path):
        with open(path, 'wb') as f:
            torch.save(self.dictionary, f, pickle_module=dill)

    def load_dict(self, path):
        assert os.path.exists(path)
        with open(path, 'r') as f:
            for line in f:
                self.dictionary.add_word(line.strip())

class Dictionary(object):
    def __init__(self):
        self.word2idx = {}
        self.idx2word = []

    def add_word(self, word):
        if word not in self.word2idx:
            self.idx2word.append(word)
            self.word2idx[word] = len(self.idx2word) - 1
        return self.word2idx[word]

    def __len__(self):
        return len(self.idx2word)

class SentenceCorpus(object):
    def __init__(self, path, save_to, testflag=False,
                 trainfname='train.txt',
                 validfname='valid.txt',
                 testfname='test.txt'):
        if not testflag:
            self.dictionary = Dictionary()
            self.train = self.tokenize(os.path.join(path, trainfname))
            self.valid = self.tokenize_with_unks(os.path.join(path, validfname))
            self.save_to = self.save_dict(save_to)
        else:
            self.dictionary = self.load_dict(save_to)
            self.test = self.sent_tokenize_with_unks(os.path.join(path, testfname))

    def save_dict(self, path):
        with open(path, 'wb') as f:
            torch.save(self.dictionary, f, pickle_module=dill)

    def load_dict(self, path):
        assert os.path.exists(path)
        with open(path, 'rb') as f:
            fdata = torch.load(f, pickle_module=dill)
            if type(fdata) == type(()):
                # compatibility with old pytorch LM saving
                return(fdata[3])
            return(fdata)

    def tokenize(self, path):
        """Tokenizes a text file."""
        assert os.path.exists(path)
        # Add words to the dictionary
        if path[-2:] == 'gz':
            with gzip.open(path, 'rb') as f:
                tokens = 0
                FIRST = True
                for fchunk in f.readlines():
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        tokens += len(words)
                        for word in words:
                            self.dictionary.add_word(word)

            # Tokenize file content
            with gzip.open(path, 'rb') as f:
                ids = torch.LongTensor(tokens)
                token = 0
                FIRST = True
                for fchunk in f.readlines():
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        for word in words:
                            ids[token] = self.dictionary.word2idx[word]
                            token += 1
        else:
            with open(path, 'r') as f:
                tokens = 0
                FIRST = True
                for fchunk in f:
                    #print fchunk
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        tokens += len(words)
                        for word in words:
                            self.dictionary.add_word(word)

            # Tokenize file content
            with open(path, 'r') as f:
                ids = torch.LongTensor(tokens)
                token = 0
                FIRST = True
                for fchunk in f:
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        for word in words:
                            ids[token] = self.dictionary.word2idx[word]
                            token += 1
        return ids

    def tokenize_with_unks(self, path):
        """Tokenizes a text file, adding unks if needed."""
        assert os.path.exists(path)
        if path[-2:] == 'gz':
            # Add words to the dictionary
            with gzip.open(path, 'rb') as f:
                tokens = 0
                FIRST = True
                for fchunk in f.readlines():
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        tokens += len(words)

            # Tokenize file content
            with gzip.open(path, 'rb') as f:
                ids = torch.LongTensor(tokens)
                token = 0
                FIRST = True
                for fchunk in f.readlines():
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        for word in words:
                            if word not in self.dictionary.word2idx:
                                ids[token] = self.dictionary.add_word("<unk>")
                            else:
                                ids[token] = self.dictionary.word2idx[word]
                            token += 1
        else:
            # Add words to the dictionary
            with open(path, 'r') as f:
                tokens = 0
                FIRST = True
                for fchunk in f:
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        tokens += len(words)

            # Tokenize file content
            with open(path, 'r') as f:
                ids = torch.LongTensor(tokens)
                token = 0
                FIRST = True
                for fchunk in f:
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        if FIRST:
                            words = ['<eos>'] + line.split() + ['<eos>']
                            FIRST = False
                        else:
                            words = line.split() + ['<eos>']
                        for word in words:
                            if word not in self.dictionary.word2idx:
                                ids[token] = self.dictionary.add_word("<unk>")
                            else:
                                ids[token] = self.dictionary.word2idx[word]
                            token += 1
        return ids

    def sent_tokenize_with_unks(self, path):
        """Tokenizes a text file into sentences, adding unks if needed."""
        assert os.path.exists(path)
        all_ids = []
        sents = []
        if path [-2:] == 'gz':
            with gzip.open(path, 'rb') as f:
                for fchunk in f.readlines():
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        sents.append(line.strip())
                        words = ['<eos>'] + line.split() + ['<eos>']
                        tokens = len(words)

                        # tokenize file content
                        ids = torch.LongTensor(tokens)
                        token = 0
                        for word in words:
                            if word not in self.dictionary.word2idx:
                                ids[token] = self.dictionary.add_word("<unk>")
                            else:
                                ids[token] = self.dictionary.word2idx[word]
                            token += 1
                        all_ids.append(ids)
        else:
            with open(path, 'r') as f:
                for fchunk in f:
                    for line in sent_tokenize(fchunk):
                        if line.strip() == '':
                            #ignore blank lines
                            continue
                        sents.append(line.strip())
                        words = ['<eos>'] + line.split() + ['<eos>']
                        tokens = len(words)

                        # tokenize file content
                        ids = torch.LongTensor(tokens)
                        token = 0
                        for word in words:
                            if word not in self.dictionary.word2idx:
                                ids[token] = self.dictionary.add_word("<unk>")
                            else:
                                ids[token] = self.dictionary.word2idx[word]
                            token += 1
                        all_ids.append(ids)
        return (sents, all_ids)
