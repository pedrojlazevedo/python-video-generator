import sys

from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QPushButton

from python_video_generator.image_parser.bing_image_retrieval import BingImageRetrieval
from python_video_generator.text_2_speech.speech_generator import generate_tts_from_text
from python_video_generator.text_parser.wikipedia import WikipediaScraper
from python_video_generator.utils import Document, Sentence
from python_video_generator.video_editor.generate_video import resize_image, add_text_to_image, compose_video


class UIForm(QMainWindow):
    def __init__(self, x=400, y=300):
        # create window
        super().__init__()

        self.x = x
        self.y = y

        self.widgets = {}

        # modules
        self.text_parser = WikipediaScraper()
        self.image_parser = BingImageRetrieval()

    def set_main_window(self):
        self.resize(self.x, self.y)
        self.setWindowTitle("Python Video Generator")

        # add keyword text box
        video_name_label = QLabel("Video Name:", self)
        video_name_label.move(int(self.x / 6), int(self.y / 6))
        video_name_input = QLineEdit(self)
        video_name_input.move(int(2 * self.x / 6) + 10, int(self.y / 6))
        self.widgets['video_name_input'] = video_name_input

        # add type of search
        search_type_label = QLabel("W-question:", self)
        search_type_label.move(int(self.x / 6), int(2 * self.y / 6))
        search_type_input = QLineEdit(self)
        search_type_input.move(int(2 * self.x / 6) + 10, int(2 * self.y / 6))
        self.widgets['search_type_input'] = search_type_input

        # add generation button
        generate_video_button = QPushButton("Generate Video", self)
        generate_video_button.setGeometry(int(self.x / 3), int(self.y / 2), 150, 80)
        generate_video_button.clicked.connect(self.generate_video)

        # add window to the application
        self.show()

    def generate_video(self):
        keyword = self.widgets['video_name_input'].text()
        search_type = self.widgets['search_type_input'].text()

        # select best article and parse wikipedia information
        article = self.text_parser.article_finder(keyword, search_type)
        sentences_dict = self.text_parser.parse_wikipedia_article(article)
        self.text_parser.summarize_article(sentences_dict)

        # init sentences
        sentences = self.text_parser.init_sentences(sentences_dict)

        # init document
        document = Document(query=keyword, sentences=sentences)

        for sub_title, sentences in document.sentences.items():
            for sentence in sentences:
                # extract keywords from each sentence
                sentence.keywords = self.text_parser.retrieve_keywords(document.query, sentence.text)

                # retrieve images
                self.image_parser.retrieve_best_image(sentence)

                # resize images
                resize_image(sentence)
                add_text_to_image(sentence, title=sub_title)

                generate_tts_from_text(sentence)

        compose_video(document)


def main():
    app = QApplication(sys.argv)

    main_form = UIForm()
    main_form.set_main_window()

    app.exec()


if __name__ == '__main__':
    main()
