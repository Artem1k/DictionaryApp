import subprocess
import re

def list_tracks(mkv_file):
    # Get track info using mkvmerge
    result = subprocess.run(['mkvmerge', '-i', mkv_file], capture_output=True, text=True)
    tracks = []
    for line in result.stdout.splitlines():
        match = re.match(r'Track ID (\d+): subtitles \((.*?)\)', line)
        if match:
            tracks.append((int(match.group(1)), match.group(2)))
    return tracks

def extract_subtitle(mkv_file, track_id, output_file):
    # Extract the subtitle track
    subprocess.run(['mkvextract', 'tracks', mkv_file, f'{track_id}:{output_file}'])

# Example usage:
mkv_file = 'yourfile.mkv'
tracks = list_tracks(mkv_file)
print("Subtitle tracks found:", tracks)
if tracks:
    # Extract the first subtitle track
    extract_subtitle(mkv_file, tracks[0][0], 'subtitle.srt')