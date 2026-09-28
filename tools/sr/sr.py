"""Real-ESRGAN inference without basicsr: RRDBNet (x4plus) and SRVGGNetCompact (general-x4v3)."""
import sys, os, torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
class RDB(nn.Module):
    def __init__(s, nf=64, gc=32):
        super().__init__()
        s.conv1 = nn.Conv2d(nf, gc, 3, 1, 1); s.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1); s.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        s.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1); s.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1); s.l = nn.LeakyReLU(0.2, True)
    def forward(s, x):
        x1 = s.l(s.conv1(x)); x2 = s.l(s.conv2(torch.cat((x, x1), 1))); x3 = s.l(s.conv3(torch.cat((x, x1, x2), 1)))
        x4 = s.l(s.conv4(torch.cat((x, x1, x2, x3), 1))); x5 = s.conv5(torch.cat((x, x1, x2, x3, x4), 1)); return x5 * 0.2 + x
class RRDB(nn.Module):
    def __init__(s, nf, gc=32):
        super().__init__(); s.rdb1 = RDB(nf, gc); s.rdb2 = RDB(nf, gc); s.rdb3 = RDB(nf, gc)
    def forward(s, x): return s.rdb3(s.rdb2(s.rdb1(x))) * 0.2 + x
class RRDBNet(nn.Module):
    def __init__(s, nf=64, nb=23, gc=32):
        super().__init__()
        s.conv_first = nn.Conv2d(3, nf, 3, 1, 1); s.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)]); s.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        s.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1); s.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1); s.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1); s.conv_last = nn.Conv2d(nf, 3, 3, 1, 1); s.l = nn.LeakyReLU(0.2, True)
    def forward(s, x):
        f = s.conv_first(x); f = s.conv_body(s.body(f)) + f
        f = s.l(s.conv_up1(F.interpolate(f, scale_factor=2, mode='nearest'))); f = s.l(s.conv_up2(F.interpolate(f, scale_factor=2, mode='nearest')))
        return s.conv_last(s.l(s.conv_hr(f)))
class Compact(nn.Module):
    def __init__(s, nf=64, nc=32, up=4):
        super().__init__(); s.up = up; L = [nn.Conv2d(3, nf, 3, 1, 1), nn.PReLU(nf)]
        for _ in range(nc): L += [nn.Conv2d(nf, nf, 3, 1, 1), nn.PReLU(nf)]
        L += [nn.Conv2d(nf, 3 * up * up, 3, 1, 1)]; s.body = nn.Sequential(*L); s.ps = nn.PixelShuffle(up)
    def forward(s, x): return s.ps(s.body(x)) + F.interpolate(x, scale_factor=s.up, mode='nearest')
def load(name):
    sd = torch.load(os.path.join(D, name + '.pth'), map_location='cpu', weights_only=True); sd = sd.get('params_ema', sd.get('params', sd))
    m = RRDBNet() if 'x4plus' in name else Compact(); m.load_state_dict(sd, strict=True); return m.eval()
def run(m, im, dev, tile=256, pad=16):
    x = torch.from_numpy(np.asarray(im.convert('RGB'), dtype=np.float32) / 255).permute(2, 0, 1)[None].to(dev)
    _, _, H, W = x.shape; out = torch.zeros(1, 3, H * 4, W * 4, device=dev)
    with torch.no_grad():
        for y in range(0, H, tile):
            for xx in range(0, W, tile):
                y0, y1 = max(0, y - pad), min(H, y + tile + pad); x0, x1 = max(0, xx - pad), min(W, xx + tile + pad)
                o = m(x[:, :, y0:y1, x0:x1]); oy, ox = (y - y0) * 4, (xx - x0) * 4
                out[:, :, y * 4:min(H, y + tile) * 4, xx * 4:min(W, xx + tile) * 4] = o[:, :, oy:oy + min(tile, H - y) * 4, ox:ox + min(tile, W - xx) * 4]
    a = (out[0].clamp(0, 1).permute(1, 2, 0).cpu().numpy() * 255).round().astype(np.uint8); return Image.fromarray(a)
if __name__ == '__main__':
    name, src, dst = sys.argv[1:4]; dev = 'mps' if torch.backends.mps.is_available() else 'cpu'
    m = load(name).to(dev); run(m, Image.open(src), dev).save(dst, quality=95); print('wrote', dst)
