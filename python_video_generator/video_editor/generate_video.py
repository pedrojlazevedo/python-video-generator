import math

import cv2
import matplotlib.pyplot as plt
import moviepy.video.fx.all as vfx
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.segmenting import findObjects

from python_video_generator.utils import Sentence, Document
from python_video_generator.video_editor.star_wars_opening import make_star_wars_video


def resize_image(sentence: Sentence):
    image = cv2.imread(sentence.best_image)
    if image is None:
        image = plt.imread(sentence.best_image)
    ideal_height = 1080
    ideal_width = 1920

    r_w = ideal_height / image.shape[0]
    r_h = ideal_width / image.shape[1]
    ratio_central = min(r_w, r_h)
    ratio_background = max(r_w, r_h)

    dim_central = (int(image.shape[1] * ratio_central), int(image.shape[0] * ratio_central))
    dim_background = (int(image.shape[1] * ratio_background), int(image.shape[0] * ratio_background))

    image_central = cv2.resize(image, dim_central)
    image_blured = cv2.resize(image, dim_background)
    image_blured = cv2.blur(src=image_blured, ksize=(100, 100))

    # add blured image to the back
    yoff = round((image_blured.shape[0] - image_central.shape[0]) / 2)
    xoff = round((image_blured.shape[1] - image_central.shape[1]) / 2)

    image_final = image_blured.copy()
    image_final[yoff: yoff + image_central.shape[0], xoff: xoff + image_central.shape[1]] = image_central

    # crop image
    center = image_final.shape / np.array(2)
    x = center[1] - ideal_width / 2
    y = center[0] - ideal_height / 2

    image_final = image_final[int(y): int(y + ideal_height), int(x): int(x + ideal_width)]

    filename = sentence.best_image.split(".")
    filename = filename[0] + '_resized.' + filename[1]
    cv2.imwrite(filename, image_final)

    sentence.images.append(filename)
    sentence.best_image = filename


def add_text_to_image(sentence: Sentence, title=None, default_font_size=45, max_tokens=8):
    text = sentence.text
    num_batch = math.ceil(len(text.split(" ")) / max_tokens)

    _, _, text_width, text_height = ImageFont.truetype(r'C:\Windows\Fonts\CALIBRIL.TTF').getbbox(text)
    img = Image.open(sentence.best_image)
    img_width, img_height = img.size  # 1920, 1080
    scaler = img_width / 3 / text_width

    scale_text_font = default_font_size

    TINT_COLOR = (0, 0, 0)  # Black
    TRANSPARENCY = .4  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)

    for i in range(num_batch):
        line = " ".join(text.split(" ")[max_tokens * i: max_tokens * (i + 1)])

        font = ImageFont.truetype(r'C:\Windows\Fonts\CALIBRIL.TTF', size=scale_text_font)
        draw = ImageDraw.Draw(img, 'RGBA')
        start_x = img_width - (font.getbbox(line)[2] / 2) - (img_width / 2)
        line_height = 42
        start_y = img_height - (line_height / 2) - (line_height * (num_batch - i + 1))

        draw.rectangle(
            (start_x, start_y, start_x + font.getbbox(line)[2], start_y + font.getbbox(line)[3]),
            fill=TINT_COLOR + (OPACITY,)
        )
        draw.text((start_x, start_y), text=line, font=font, fill=(255, 255, 255))

        # if title is not None:
        #     title = str(title).upper()
        #     start_x = 40
        #     start_y = 40
        #     font = ImageFont.truetype(r'C:\Windows\Fonts\CALIBRIL.TTF', size=scale_text_font + 5)
        #     draw.rectangle(
        #         (start_x, start_y, start_x + font.getbbox(title)[2], start_y + font.getbbox(title)[3]),
        #         fill=(0, 255, 0) + (OPACITY,)
        #     )
        #     draw.text((start_x, start_y), text=title, font=font, fill=(255, 255, 255))

    filename = sentence.best_image.split(".")
    filename = filename[0] + '_text.' + filename[1]
    img.save(filename)

    sentence.images.append(filename)
    sentence.best_image = filename


def compose_video(document: Document):
    images = [make_star_wars_video(title=document.query)]
    for sub_title, sentences in document.sentences.items():

        screen_size = (1920, 1080)
        title_duration = 3

        # magick -list color
        if sub_title == 'abstract':
            sub_title = document.query
        sub_title = sub_title.upper()

        tokens = sub_title.split(" ")
        char_count = 0
        max_char_per_line = 17
        parsed_title = ""
        for token in tokens:
            if char_count > max_char_per_line:
                parsed_title += "\n"
                char_count = 0
            char_count += len(token)
            parsed_title += token + " "
        parsed_title = parsed_title.strip()

        text_clip = TextClip(txt=parsed_title, color='yellow', font="Verdana",
                             kerning=title_duration, fontsize=100)
        cvc = CompositeVideoClip([text_clip.set_position('center')],
                                 size=screen_size)
        letters = findObjects(cvc)

        title_video = CompositeVideoClip(move_letters(letters, arrive),
                                         size=screen_size).subclip(0, title_duration)

        # set background
        image_file = ImageClip(sentences[0].best_image.replace("_text", "")).fx(vfx.colorx, .3)

        title_video = (CompositeVideoClip([image_file, title_video], size=image_file.size)
                       .set_duration(title_duration)
                       .fx(vfx.fadein, 1)
                       )
        images.append(title_video)

        is_first = True
        for sentence in sentences:
            audio_file = AudioFileClip(sentence.voice_file)
            image_file = (ImageClip(sentence.best_image).set_duration(audio_file.duration + 0.33))
            image_file = image_file.set_audio(audio_file)
            video = CompositeVideoClip([image_file], size=image_file.size).add_mask()
            if is_first:
                video = video.fx(vfx.mask_color, color=(0, 0, 0), thr=1, s=2)
                is_first = False
            images.append(video)
    concat_clip = concatenate_videoclips(images, method="compose")
    concat_clip.write_videofile("test.mp4", fps=24)


def move_letters(letters, func_pos):
    return [letter.set_pos(func_pos(letter.screenpos, i, len(letters)))
            for i, letter in enumerate(letters)]


# helper function
rotMatrix = lambda a: np.array([[np.cos(a), np.sin(a)],
                                [-np.sin(a), np.cos(a)]])


def arrive(screen_pos, i, n_letters):
    d = lambda t: 1.0 / (0.3 + t ** 8)  # damping
    a = i * np.pi / n_letters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2: v[1] = -v[1]
    return lambda t: screen_pos + 400 * d(t) * rotMatrix(0.5 * d(t) * a).dot(v)


if __name__ == '__main__':
    sentence = Sentence(
        "Age of Empires III is a real-time strategy video game developed by Microsoft Corporation's "
        "Ensemble Studios and published by Microsoft Game Studios"
    )
    sentence.images = [
        "C:\\Users\\PedroAzevedo\\PycharmProjects\\python_video_generator\\images\\Conquistador americas dominion "
        "spain\\Conquistador americas dominion spain_2_resized_text.jpg "
    ]
    sentence.best_image = sentence.images[-1]
    sentence.voice_file = "C:\\Users\\PedroAzevedo\\PycharmProjects\\python_video_generator\\tts" \
                          "\\Conquistador_americas_dominion_spain.wav "
    # resize_image(sentence)
    # add_text_to_image(sentence)

    sentence_dict = {'abstract': [sentence, sentence, sentence], 'another_title': [sentence, sentence]}
    document = Document('Conquistador', sentence_dict)
    compose_video(document)
