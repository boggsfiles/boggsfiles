#!/usr/bin/env python3
"""Ingest scanned X-Files location-scout folders into the archive.

usage: process.py <slug> "<Folder label>" <scan files...>

For each scan (PDF or image):
  - copies the original into  <slug>/scans/
  - renders/loads it, auto-rotates (see ROTATE), trims the white scanner bed
  - writes a full-res JPEG to   <slug>/full/
  - writes a web JPEG (2000px)  <slug>/web/
"""
import sys, os, shutil, subprocess, tempfile
from PIL import Image, ImageOps
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# per-file rotation override, degrees counter-clockwise; default is auto
ROTATE = {"img056.pdf": 0, "img064.pdf": 0}  # genuine portrait pages (Norton p.22, Sierra Madre parking form)

def render(path):
    if path.lower().endswith('.pdf'):
        tmp = tempfile.mkdtemp()
        subprocess.run(['pdftoppm', '-r', '300', '-png', path, os.path.join(tmp, 'p')], check=True)
        pages = sorted(os.listdir(tmp))
        return [Image.open(os.path.join(tmp, p)).convert('RGB') for p in pages]
    return [ImageOps.exif_transpose(Image.open(path)).convert('RGB')]

def trim_scanner_bed(im, thresh=235):
    """Crop away near-white scanner background around the folder/photos."""
    a = np.asarray(im.convert('L'))
    mask = a < thresh
    rows = np.where(mask.mean(axis=1) > 0.02)[0]
    cols = np.where(mask.mean(axis=0) > 0.02)[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    pad = 12
    box = (max(cols[0]-pad, 0), max(rows[0]-pad, 0),
           min(cols[-1]+pad, im.width), min(rows[-1]+pad, im.height))
    return im.crop(box)

def auto_rotate(im, name):
    """Scans of landscape folders come in portrait; rotate 90° CCW so the
    handwritten tab label reads left-to-right. Override with ROTATE."""
    deg = ROTATE.get(name)
    if deg is None:
        deg = 90 if im.height > im.width else 0
    return im.rotate(deg, expand=True) if deg else im

def main():
    slug, label, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    base = os.path.join(ROOT, slug)
    for d in ('scans', 'full', 'web'):
        os.makedirs(os.path.join(base, d), exist_ok=True)
    n = len([f for f in os.listdir(os.path.join(base, 'full')) if f.endswith('.jpg')])
    for f in files:
        shutil.copy2(f, os.path.join(base, 'scans', os.path.basename(f)))
        for page in render(f):
            n += 1
            name = f'{slug}-{n:02d}'
            im = trim_scanner_bed(auto_rotate(page, os.path.basename(f)))
            im.save(os.path.join(base, 'full', name + '.jpg'), quality=92)
            w = im.copy(); w.thumbnail((2000, 2000))
            w.save(os.path.join(base, 'web', name + '.jpg'), quality=85, optimize=True)
            print(f'{name}.jpg  {im.width}x{im.height}')
    with open(os.path.join(base, 'LABEL.txt'), 'w') as fh:
        fh.write(label + '\n')

if __name__ == '__main__':
    main()
