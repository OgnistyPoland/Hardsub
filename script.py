import os
import subprocess
import json

for root, directories, files in os.walk("."):
    for file in files:
        if file.endswith(".mkv"):
            print(file)
            filepath = os.path.join(root, file)
            ffprobe_cmd = f'ffprobe -v quiet -print_format json -show_streams -select_streams a "{filepath}"'
            ffprobe_output = subprocess.check_output(ffprobe_cmd, shell=True)
            ffprobe_data = json.loads(ffprobe_output)
            audio_channels = int(ffprobe_data['streams'][0]['channels'])
            audio_codec = ffprobe_data['streams'][0]['codec_name']
            abs_filepath = os.path.abspath(filepath)
            abs_output_path = os.path.abspath(os.path.splitext(filepath)[0] + '.mp4')
            os.rename(abs_filepath, 'processing.mkv')
            if audio_channels == 2 and audio_codec != 'eac3':
                command = f'ffmpeg -i "processing.mkv" -vf "format=yuv420p,subtitles=processing.mkv" -map_metadata -1 -movflags faststart -c:v libx264 -profile:v main -level:v 4.0 -preset veryfast -crf 17 -x264-params colormatrix=bt709 -c:a copy "{abs_output_path}"'
            elif audio_channels == 6 or audio_codec == 'eac3':
                command = f'ffmpeg -i "processing.mkv" -vf "format=yuv420p,subtitles=processing.mkv" -map_metadata -1 -movflags faststart -c:v libx264 -profile:v main -level:v 4.0 -preset veryfast -crf 17 -x264-params colormatrix=bt709 -c:a libfdk_aac -b:a 256k -ac 2 "{abs_output_path}"'
            else:
                print(f"{file} - incorrect channel count ({audio_channels})")
                continue
            subprocess.call(command, shell=True)
            os.rename('processing.mkv', abs_filepath)