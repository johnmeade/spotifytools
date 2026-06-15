"""Convert a playlist JSON artifact (from save_playlist.py) to a CSV.

Usage:
    python -m spotifytools.scripts.to_csv .artifacts/playlist_variety.json
    python -m spotifytools.scripts.to_csv .artifacts/playlist_variety.json -o out.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path


def convert(src: Path, dst: Path):
    tracks = json.loads(src.read_text())
    with dst.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'label'])
        for track in tracks:
            tid = track['id']
            artists = ', '.join(a['name'] for a in track['artists'])
            label = f"{track['name']} {artists}"
            writer.writerow([tid, label])
    return len(tracks)


def main():
    parser = argparse.ArgumentParser(description='Convert playlist JSON to CSV')
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path, default=None)
    args = parser.parse_args()

    out = args.output or args.input.with_suffix('.csv')
    n = convert(args.input, out)
    print(f'Wrote {n} rows to {out}')


if __name__ == '__main__':
    main()
