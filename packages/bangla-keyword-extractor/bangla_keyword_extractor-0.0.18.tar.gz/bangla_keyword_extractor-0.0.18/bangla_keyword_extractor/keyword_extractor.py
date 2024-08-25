import re
from .custom_rake import BanglaRake
from rake_nltk import Rake
from collections import defaultdict, Counter
import numpy as np
import networkx as nx
from tqdm.auto import tqdm
import os
import nltk
nltk.download("punkt")
nltk.download("stopwords")
from nltk.corpus import stopwords

class KeywordExtractor:
    def __init__(self, input_text_list, stop_words = None, max_keywords = 10, language = "bn"):
        self.text_list = input_text_list
        self.language = language
        if stop_words is None:
            if self.language == "bn":
                with open(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stopwords.txt")), "r") as f:
                    self.stopwords = f.read().split("\n")
            elif self.language == "en":
                self.stopwords = stopwords.words("english")
        else:
            if self.language == "bn":
                with open(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stopwords.txt")), "a") as f:
                    for w in stop_words:
                        f.write(w)
                        f.write("\n")
            elif self.language == "en":
                self.stopwords = stopwords.words("english")
                for w in stop_words:
                    self.stopwords.append(w)

        if isinstance(self.text_list, str):
            self.corpus = self.text_list
        elif isinstance(self.text_list, list):
            self.corpus = " ".join(self.text_list)
        else:
            raise TypeError("The inputs must be string or list of strings.")
        if not (self.language == "bn" or self.language == "en"):
            raise Exception("Bangla keyword extractor doesn't support this language.")
        # if self.language == "bn":
        #     self.word_tokenizer = wordTokenizer()
        #     self.sentence_tokenizer = sentenceTokenizer()
        self.max_keywords = max_keywords
        if self.language == "bn":
            self.rake = BanglaRake(
                stopwords=self.stopwords,
                max_length=3,
                include_repeated_phrases=False,
                # sentence_tokenizer=self.sentence_tokenizer,
                # word_tokenizer=self.word_tokenizer
            )
        elif self.language == "en":
            self.rake = Rake(
                max_length=3,
                include_repeated_phrases=False,
            )

    def clean_bn_data(self, text):
        clean_text = re.sub(r"[^\u0980-\u09FF\u09E6-\u09EF\s]", "", text)
        clean_text = re.sub(r"[০-৯]", "", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text
    
    def clean_en_data(self, text):
        text = text.lower()
        clean_text = re.sub(r"(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})(\.[a-zA-Z0-9]{2,})?\/[a-zA-Z0-9]{2,}", " ", text)
        clean_text = re.sub(r"[^\w\s]", " ", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text
    
    def get_keywords_using_rake(self):
        self.rake.extract_keywords_from_text(self.corpus)
        ranks = self.rake.get_word_degrees()
        pairs = []
        for key, value in ranks.items():
            pairs.append((key, value))
        sorted_pairs = sorted(pairs, key = lambda x:x[1], reverse=True)
        return sorted_pairs[:self.max_keywords]
    
    def get_keywords_using_pagerank(self):
        if self.language == "bn":
            clean_corpus = self.clean_bn_data(self.corpus)
        elif self.language == "en":
            clean_corpus = self.clean_en_data(self.corpus)
        words = self.rake._tokenize_sentence_to_words(clean_corpus)
        words = [word for word in words if not word in self.stopwords]
        unique_words = list(set(words))
        co_occurrences = self.build_co_occurances(window_size=3, words=words)
        co_occurrences_matrix = self.build_co_occurrences_matrix(unique_words=unique_words, co_occurrences=co_occurrences)
        pagerank_scores = self.get_pagerank_scores(unique_words=unique_words, co_occurrences_matrix=co_occurrences_matrix)
        return pagerank_scores[:self.max_keywords]

    def build_co_occurances(self, window_size, words):
        window_size = window_size

        co_occurrences = defaultdict(Counter)

        for i, word in enumerate(words):
            for j in range(max(0, i - window_size), min(len(words), i + window_size + 1)):
                if i != j:
                    co_occurrences[word][words[j]] += 1
        return co_occurrences
    
    def build_co_occurrences_matrix(self, unique_words, co_occurrences):
        co_matrix = np.zeros((len(unique_words), len(unique_words)), dtype=int)

        word_index = {word: idx for idx, word in enumerate(unique_words)}
        for word, neighbors in tqdm(co_occurrences.items(), total = len(co_occurrences),disable=True):
            for neighbor, count in neighbors.items():
                co_matrix[word_index[word]][word_index[neighbor]] = count
        return co_matrix
    
    def get_pagerank_scores(self, unique_words, co_occurrences_matrix):
        G = nx.Graph()
        for word in unique_words:
            G.add_node(word)
        for i in tqdm(range(len(unique_words)), total = len(unique_words),disable=True): 
            for j in range(len(unique_words)): 
                if co_occurrences_matrix[i][j]>0:
                    G.add_edge(unique_words[i], unique_words[j], weight = co_occurrences_matrix[i][j])
        pagerank_scores = nx.pagerank(G, weight='weight')
        sorted_pagerank = sorted(pagerank_scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_pagerank