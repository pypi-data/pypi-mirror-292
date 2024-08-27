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
