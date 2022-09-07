from typing import List


class Sentence:
    def __init__(self, text: str = None, images=None, keywords=None):
        if keywords is None:
            keywords = []
        if images is None:
            images = []
        self.text = text
        self.images = images
        self.keywords = keywords
        self.voice_file = None
        self.video_file = None

        self.best_keyword = None
        self.best_image = None

    @property
    def best_keyword(self):
        return self._best_keyword

    @best_keyword.setter
    def best_keyword(self, keyword: str):
        if keyword in self.keywords or keyword is None:
            self._best_keyword = keyword
        else:
            raise ValueError("Keyword is not a valid one")

    @property
    def best_image(self):
        return self._best_image

    @best_image.setter
    def best_image(self, image):
        if image in self.images or image is None:
            self._best_image = image
        else:
            raise ValueError("Image is not a valid one")

    def __str__(self):
        print(f"{self.text} - {self.best_keyword} - {self.best_image}")


class Document:
    def __init__(self, query: str, sentences=None):
        if sentences is None:
            sentences = []
        self.query = query
        self.sentences = sentences

    def add_sentence(self, sentence: Sentence):
        self.sentences.append(sentence)
