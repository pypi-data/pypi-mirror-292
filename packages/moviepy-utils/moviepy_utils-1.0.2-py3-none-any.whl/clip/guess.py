# -*- coding: utf-8 -*-
# @Time        : 2024/8/27 10:42
# @Author      : bai.<byscut2010@foxmail.com>
# @File        : guss.py
# @Description :
import cv2
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize


def generate_gaussian_clip(image_clip, target_size):
    gauss_clip = resize(image_clip, height=target_size[1])
    if gauss_clip.size[0] < target_size[0]:
        gauss_clip = gauss_clip.resize(width=target_size[0])
        y = (gauss_clip.size[1] - target_size[1]) / 2
        print("gauss y = ", y)
        gauss_clip = crop(gauss_clip, y1=y, height=target_size[1])
    elif gauss_clip.size[0] > target_size[0]:
        x = (gauss_clip.size[0] - target_size[0]) / 2
        print("gauss x = ", x)
        gauss_clip = crop(gauss_clip, x1=x, width=target_size[0])
    gauss_clip = gauss_clip.image_transform(lambda img: cv2.blur(img, (30, 30)))
    return gauss_clip
