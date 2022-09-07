import re
from typing import List

import nltk
import wikipedia
from PyQt6.QtWidgets import QComboBox, QMainWindow, QPushButton, QVBoxLayout, QDialog
from keybert import KeyBERT
from transformers import pipeline

from python_video_generator.utils import Sentence

nltk.download('punkt')


class WikipediaScraper(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Text Parser")
        self.selected_article = None
        self.central_widget = QDialog()

        # init keyword extractor model - all-mpnet-base-v2
        self.kw_model = KeyBERT('all-mpnet-base-v2')

        # init summarizer model - bart-large-cnn
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def article_finder(self, keyword: str, search_type: str, max_articles: int = 5) -> str:
        article_list = wikipedia.search(keyword, max_articles)
        return self.select_best_article(article_list)

    def preprocess_plain_text(self, x: str) -> str:
        x = re.sub(r"https*\S+", " ", x)  # url
        x = re.sub(r"@\S+", " ", x)  # mentions
        x = re.sub(r"#\S+", " ", x)  # hastags
        x = re.sub(r"\s{2,}", " ", x)  # over spaces
        x = re.sub("[^.,!?A-Za-z0-9]+", " ", x)  # special charachters except .,!?
        return x

    def parse_wikipedia_article(self, article) -> dict:
        if article != self.selected_article:
            raise ValueError('Something went wrong')
        full_page = wikipedia.page(f"'{article}'").content
        sentences = full_page.split("\n")
        sentences = [sentence for sentence in sentences if len(sentence) != 0]

        # separate by markdown generating a dict of sentences
        wikipedia_page = dict()
        title = "abstract"

        for sentence in sentences:
            if sentence.startswith("="):
                title = sentence.replace("=", "").strip()
            else:
                sentence = self.preprocess_plain_text(sentence)
                split_sentence = nltk.sent_tokenize(sentence)
                wikipedia_page.setdefault(title, []).extend(split_sentence)
        wikipedia_page.pop('Further reading', None)
        wikipedia_page.pop('See also', None)
        wikipedia_page.pop('People', None)
        wikipedia_page.pop('References', None)
        wikipedia_page.pop('External Links', None)
        print(wikipedia_page.keys())

        return wikipedia_page

    def init_sentences(self, sentences):
        sentences_dict = dict()
        [sentences_dict.setdefault(sub_title, []).extend([Sentence(sentence) for sentence in nltk.sent_tokenize(text)])
         for sub_title, text in sentences.items()]
        return sentences_dict

    def summarize_article(self, article: dict, max_tokens: int = 1024):
        for sub_title, sentences in article.items():
            print(f"\nStarting Summarization of {sub_title}")
            text = ' '.join(sentences)
            while len(self.summarizer.tokenizer.tokenize(text)) >= max_tokens:
                text = ' '.join(text.split(" ")[:-5])
            print(text)
            summary = self.summarize_text(text)
            print(summary)
            article[sub_title] = summary[-1]['summary_text']

    def summarize_text(self, text: str) -> str:
        return self.summarizer(text, max_length=250, min_length=50, do_sample=False)

    def retrieve_keywords(self, query: str, text: str) -> List[str]:
        keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3))
        print(keywords)
        keywords = [keyword[0] for keyword in keywords]

        # add query at the beginning of the keyword if is not in the keyword already
        tokens = nltk.word_tokenize(query)
        for i, keyword in enumerate(keywords):
            for token in reversed(tokens):
                if token.lower() not in keyword.lower():
                    keyword = token + " " + keyword
            keywords[i] = keyword
        return keywords

    def select_best_article(self, article_list: list) -> str:
        article_selector = QComboBox()
        article_selector.addItems(article_list)

        article_processor = QPushButton()

        # Sends the current index (position) of the selected item.
        self.selected_article = article_list[0]
        article_selector.currentTextChanged.connect(self.index_changed)
        article_processor.clicked.connect(self.close_event)
        article_processor.setText("Parse Wikipedia Article")

        layout = QVBoxLayout()
        layout.addWidget(article_selector)
        layout.addWidget(article_processor)

        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.show()
        self.central_widget.exec()

        # waiting for button to close
        return self.selected_article

    def index_changed(self, article: str):
        self.selected_article = article

    def close_event(self):
        self.central_widget.close()
        self.close()
