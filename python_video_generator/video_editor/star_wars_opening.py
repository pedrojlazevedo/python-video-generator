import numpy as np
from moviepy.video.VideoClip import TextClip, ImageClip, VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.drawing import color_gradient

from skimage import transform as tf


def make_star_wars_video(text: str = None, title: str = "ADD_ME"):
    w = 1920
    h = 1080  # 16/9 screen
    moviesize = w, h

    # THE RAW TEXT
    if text is None:
        text = "\n".join(
            [
                "Hello viewer,",
                "",
                "I am glad you are watching me!",
                "I was designed to create fully automated videos,",
                "to present information",
                "about a topic or theme.",
                "",
                "In this video, I will talk about:",
                f"{title}",
                "",
                "This video is part of a series called:",
                "The history about each AoE Unique Unit.",
                "",
                "If you find this information helpful",
                "Please leave a like and subscribe!",
                "If you have any ideas about the next video topic",
                "Please leave a comment!",
                "",
                "Have fun :)",
            ]
        )
    # This video was made by an AI.
    # Every content was extracted from
    # Add blanks
    text = 10 * "\n" + text + 10 * "\n"

    # CREATE THE TEXT IMAGE

    clip_txt = TextClip(
        text, color='yellow', align='center', fontsize=65, font='Xolonium-Bold', method='label'
    ).add_mask()

    # SCROLL THE TEXT IMAGE BY CROPPING A MOVING AREA
    txt_speed = 100
    fl = lambda gf, t: gf(t)[int(txt_speed * t) : int(txt_speed * t) + h, :]
    moving_txt = clip_txt.fl(fl, apply_to=['mask'])

    # ADD A VANISHING EFFECT ON THE TEXT WITH A GRADIENT MASK
    grad = color_gradient(moving_txt.size, p1=(0, 3 * h / 4), p2=(0, 1 * h / 6), col1=0.0, col2=1.0)
    gradmask = ImageClip(grad, ismask=True)
    fl = lambda pic: np.minimum(pic, gradmask.img)
    moving_txt.mask = moving_txt.mask.fl_image(fl)

    # WARP THE TEXT INTO A TRAPEZOID (PERSPECTIVE EFFECT)
    def trapz_warp(pic, cx, cy, ismask=False):
        Y, X = pic.shape[:2]
        src = np.array([[0, 0], [X, 0], [X, Y], [0, Y]])
        dst = np.array([[cx * X, cy * Y], [(1 - cx) * X, cy * Y], [X, Y], [0, Y]])
        tform = tf.ProjectiveTransform()
        tform.estimate(src, dst)
        im = tf.warp(pic, tform.inverse, output_shape=(Y, X))
        return im if ismask else (im * 255).astype('uint8')

    fl_im = lambda pic: trapz_warp(pic, 0.0, 0.0)
    fl_mask = lambda pic: trapz_warp(pic, 0.0, 0.0, ismask=True)
    warped_txt = moving_txt.fl_image(fl_im)
    warped_txt.mask = warped_txt.mask.fl_image(fl_mask)

    # BACKGROUND IMAGE, DARKENED AT 60%
    stars = ImageClip('stars.png')
    stars_darkened = stars.fl_image(lambda pic: (0.6 * pic).astype('int16'))

    # COMPOSE THE MOVIE
    final = CompositeVideoClip([stars_darkened, warped_txt.set_position(('center', 'bottom'))], size=moviesize)
    final = final.set_duration(16)
    return final


if __name__ == '__main__':
    make_star_wars_video()
