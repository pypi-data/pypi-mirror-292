import json


def ffprobe_get_video_info(video_file):
    import subprocess
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_file]
        cmd_result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        video_info = json.loads(cmd_result)
    except Exception as exc:
        print("ERROR: get video info error:{}".format(exc))
        return None

    return video_info


def get_side_data_rotate(video_file):
    video_info = ffprobe_get_video_info(video_file)
    if video_info is None:
        return False
    try:
        video_stream = None
        for stream in video_info.get('streams'):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        if video_stream:
            side_data_list = video_stream.get('side_data_list')
            if side_data_list and len(side_data_list) > 0:
                if side_data_list[0].get('side_data_type') == 'Display Matrix' and \
                        side_data_list[0].get('rotation') in [90, -90]:
                    return True
    except Exception as exc:
        log_api.error("ERROR: get side data rotate error:{}".format(exc))
    return False
