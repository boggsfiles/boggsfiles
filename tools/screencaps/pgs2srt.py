"""pgs2srt.py <in.sup> <out.srt> [workers]
Minimal PGS (Blu-ray bitmap subtitle) decoder + tesseract OCR -> SRT.
"""
import sys, struct, subprocess, tempfile, os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np

def read_segments(data):
    i = 0
    while i + 13 <= len(data):
        if data[i:i+2] != b'PG':
            i += 1; continue
        pts = struct.unpack('>I', data[i+2:i+6])[0]
        typ = data[i+10]; size = struct.unpack('>H', data[i+11:i+13])[0]
        yield pts, typ, data[i+13:i+13+size]
        i += 13 + size

def decode_rle(rle, w, h):
    img = np.zeros((h, w), np.uint8); x = y = 0; i = 0; n = len(rle)
    while i < n and y < h:
        b = rle[i]; i += 1
        if b:
            img[y, x] = b; x += 1; continue
        if i >= n: break
        f = rle[i]; i += 1
        if f == 0:
            x = 0; y += 1; continue
        if f & 0xC0 == 0x40:      # 00 01xxxxxx yyyyyyyy : run of zeros, 14-bit length
            L = ((f & 0x3F) << 8) | rle[i]; i += 1; c = 0
        elif f & 0xC0 == 0x80:    # 00 10xxxxxx cccccccc : run of colour c, 6-bit length
            L = f & 0x3F; c = rle[i]; i += 1
        elif f & 0xC0 == 0xC0:    # 00 11xxxxxx yyyyyyyy cccccccc
            L = ((f & 0x3F) << 8) | rle[i]; c = rle[i+1]; i += 2
        else:                     # 00 00xxxxxx : run of zeros
            L = f & 0x3F; c = 0
        L = min(L, w - x); img[y, x:x+L] = c; x += L
    return img

def parse(path):
    data = open(path, 'rb').read()
    palettes = {}; cues = []; cur = None; objbuf = {}
    for pts, typ, seg in read_segments(data):
        t = pts / 90000.0
        if typ == 0x16:  # PCS
            num_objs = seg[10] if len(seg) > 10 else 0
            if cur is not None:
                cur['end'] = t; cues.append(cur); cur = None
            if num_objs:
                cur = {'start': t, 'end': None, 'pal': seg[9], 'objs': []}
            objbuf = {}
        elif typ == 0x14:  # PDS
            pid = seg[0]; pal = {}
            for j in range(2, len(seg) - 4, 5):
                e, y, cr, cb, a = seg[j:j+5]; pal[e] = (y, a)
            palettes[pid] = pal
        elif typ == 0x15 and cur is not None:  # ODS
            oid = struct.unpack('>H', seg[0:2])[0]; flag = seg[3]
            if flag & 0x80:  # first in sequence
                w, h = struct.unpack('>HH', seg[7:11]); objbuf[oid] = [w, h, bytearray(seg[11:])]
            elif oid in objbuf:
                objbuf[oid][2] += seg[4:]
            if flag & 0x40 and oid in objbuf:  # last
                w, h, rle = objbuf.pop(oid); cur['objs'].append((w, h, bytes(rle), palettes.get(cur['pal'], {})))
    if cur is not None and cur['end'] is None:
        cur['end'] = cur['start'] + 3; cues.append(cur)
    return [c for c in cues if c['objs']]

def render(cue):
    tiles = []
    for w, h, rle, pal in cue['objs']:
        idx = decode_rle(rle, w, h)
        lum = np.zeros(256, np.uint8); alpha = np.zeros(256, np.uint8)
        for e, (y, a) in pal.items(): lum[e] = y; alpha[e] = a
        Y = lum[idx].astype(np.int32); A = alpha[idx].astype(np.int32)
        text = (A > 128) & (Y > 140)
        out = np.full((h, w), 255, np.uint8); out[text] = 0
        tiles.append(out)
    H = sum(t.shape[0] for t in tiles) + 20 * (len(tiles) + 1); W = max(t.shape[1] for t in tiles) + 40
    canvas = np.full((H, W), 255, np.uint8); y = 20
    for t in tiles:
        canvas[y:y+t.shape[0], 20:20+t.shape[1]] = t; y += t.shape[0] + 20
    return Image.fromarray(canvas)

def ocr(im):
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        im.save(f.name); p = f.name
    r = subprocess.run(['tesseract', p, '-', '-l', 'eng', '--psm', '6'], capture_output=True, text=True)
    os.unlink(p)
    return '\n'.join(line.strip() for line in r.stdout.splitlines() if line.strip())

def tc(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; workers = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    cues = parse(src); print("cues:", len(cues), flush=True)
    imgs = [render(c) for c in cues]
    with ThreadPoolExecutor(workers) as ex:
        texts = list(ex.map(ocr, imgs))
    n = 0
    with open(dst, 'w') as f:
        for c, txt in zip(cues, texts):
            if not txt: continue
            n += 1; f.write(f"{n}\n{tc(c['start'])} --> {tc(c['end'])}\n{txt}\n\n")
    print("written:", n, "->", dst)
