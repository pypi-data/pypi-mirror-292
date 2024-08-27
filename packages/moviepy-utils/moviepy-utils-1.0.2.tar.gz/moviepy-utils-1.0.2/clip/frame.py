# -*- coding: utf-8 -*-
# @Time        : 2024/8/27 10:44
# @Author      : bai.<byscut2010@foxmail.com>
# @File        : frame.py
# @Description :
from moviepy.editor import VideoFileClip, ImageClip


def get_last_frame_clip(video_clip: VideoFileClip) -> ImageClip:
    clip_actual_duration = video_clip.duration
    end_clip = None
    minus = 0
    while clip_actual_duration - minus >= 0:
        try:
            end_clip = video_clip.to_ImageClip(t=clip_actual_duration - 0.1 - minus)
            break
        except OSError:
            minus += 0.1
    if not end_clip:
        raise Exception("Can't get last frame clip!")
    return end_clip
