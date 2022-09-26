import os
from glob import glob

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QDialog, QComboBox, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QRadioButton
from bing_images import bing

from python_video_generator.utils import Sentence


class BingImageRetrieval(QMainWindow):
    def __init__(self, images_dir: str = 'images'):
        super().__init__()

        self.images_dir = images_dir
        self.keyword = ""
        self.image_selected = None

        self.setWindowTitle("Image Parser")
        self.central_widget = QDialog()

        self.label_width = 180
        self.label_height = 200

    def _index_changed(self, keyword: str):
        self.keyword = keyword

    def _close_event(self):
        self.central_widget.close()
        self.close()

    def _on_selected(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            self.image_selected = int(radio_button.text())

    def download_images(self, sentence: Sentence, n: int = 5):
        for text in sentence.keywords:
            clean_text = text.encode("ascii", "ignore")
            clean_text = clean_text.decode()
            image_dir = os.path.join(self.images_dir, clean_text)
            bing.download_images(clean_text,
                                 limit=n,
                                 output_dir=image_dir,
                                 pool_size=20,
                                 force_replace=True,
                                 filters='+filterui:license-L2_L3&FORM=IRFLTR')

            # save download images path
            sentence.images = glob(os.path.join(image_dir, "*"))
            if len(sentence.images) > 0:
                sentence.best_keyword = text
                break
        # fall back
        if len(sentence.images) == 0:
            text = sentence.best_keyword
            clean_text = text.encode("ascii", "ignore")
            clean_text = clean_text.decode()
            image_dir = os.path.join(self.images_dir, clean_text)
            bing.download_images(clean_text,
                                 limit=n,
                                 output_dir=image_dir,
                                 pool_size=20,
                                 force_replace=True,)
            sentence.images = glob(os.path.join(image_dir, "*"))

    def retrieve_best_image(self, sentence: Sentence):
        self.select_best_keyword(sentence)
        self.download_images(sentence)
        self.select_best_image(sentence)

    def select_best_keyword(self, sentence: Sentence):
        keyword_selector = QComboBox()
        keyword_selector.addItems(sentence.keywords)
        keyword_selector.currentTextChanged.connect(self._index_changed)
        self.keyword = sentence.keywords[0]

        label = QLabel()
        label.setText(sentence.text)

        extract_images = QPushButton("Retrieve Images")
        extract_images.clicked.connect(self._close_event)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(keyword_selector)
        layout.addWidget(extract_images)

        self.central_widget = QDialog()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        #self.show()
        #self.central_widget.exec()

        sentence.best_keyword = self.keyword

    def select_best_image(self, sentence: Sentence):
        layout = QVBoxLayout()

        label = QLabel()
        label.setText(sentence.text)
        layout.addWidget(label)

        self.image_selected = 1
        for i, image in enumerate(sentence.images):
            image_layout = QHBoxLayout()
            b1 = QRadioButton()
            b1.setText(str(i))
            b1.toggled.connect(self._on_selected)

            label = QLabel()
            pixmap = QPixmap(image)
            pixmap = pixmap.scaledToWidth(256)
            label.setPixmap(pixmap)

            image_layout.addWidget(b1)
            image_layout.addWidget(label)

            layout.addLayout(image_layout)

        select_image = QPushButton("Select Image")
        select_image.clicked.connect(self._close_event)
        layout.addWidget(select_image)

        self.central_widget = QDialog()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        #self.show()
        #self.central_widget.exec()

        print(self.image_selected)
        sentence.best_image = sentence.images[self.image_selected - 1]
