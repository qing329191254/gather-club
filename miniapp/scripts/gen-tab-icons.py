# -*- coding: utf-8 -*-
"""Rebuild tabBar icons from the reference screenshots.

The reference icons are not from a public icon set, so instead of redrawing them
by hand each glyph is lifted out of the screenshot, smoothed back into a clean
high-resolution mask, and re-rendered at the size the tabBar needs.

Normal state  : black glyph on transparent background.
Selected state: white glyph on a filled red disc.
"""

import os

from PIL import Image, ImageDraw, ImageFilter

REF_DIR = os.path.join(
    os.path.expanduser('~'),
    '.cursor', 'projects', 'd-demo-gather-club', 'assets'
)
REF_PREFIX = ('c__Users_19428_AppData_Roaming_Cursor_User_workspaceStorage_'
              'e05877021f6c98c2e312637ee09d41fc_images_')
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'tab')

# Reference screenshots, one per selected tab.
SHOTS = {
    'mine_sel': 'image-a797a9f2-798f-4c2a-8d4e-17675b691079',
    'video_sel': 'image-76f15b55-c2d0-411e-ab51-2b14f4d116f2',
    'gather_sel': 'image-f00b6213-a2c4-4294-a832-cc872cd84c61',
    'home_sel': 'image-141ccd3a-a02c-4154-8665-068144524440',
}

# Source crop of every unselected glyph: (screenshot, left, top, right, bottom).
GLYPHS = {
    'home': ('gather_sel', 82, 69, 124, 106),
    'gather': ('home_sel', 230, 55, 276, 92),
    'video': ('home_sel', 407, 53, 453, 90),
    'mine': ('home_sel', 580, 51, 621, 94),
}

BOX = 160                 # canvas = the 64rpx icon box
DISC = 160                # selected disc fills the box (58px of 58px in the reference)
REF_DISC_PX = 58.0        # measured disc diameter in the screenshots
RED = (230, 71, 80, 255)
INK = (26, 28, 32, 255)


def reference(name):
    return Image.open(os.path.join(REF_DIR, REF_PREFIX + SHOTS[name] + '.png')).convert('L')


def clean_mask(img, target_w, target_h, supersample=8):
    """Turn a small screenshot crop into a smooth mask at the requested size."""
    mask = Image.eval(img, lambda v: 255 - v)
    lo, hi = mask.getextrema()
    if hi > lo:
        mask = Image.eval(mask, lambda v: max(0, min(255, int((v - lo) * 255.0 / (hi - lo)))))
    big = mask.resize((mask.width * supersample, mask.height * supersample), Image.Resampling.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(supersample * 0.55))
    big = Image.eval(big, lambda v: 255 if v >= 128 else 0)
    return big.resize((target_w, target_h), Image.Resampling.LANCZOS)


def compose(mask, selected):
    canvas = Image.new('RGBA', (BOX, BOX), (0, 0, 0, 0))
    if selected:
        disc = Image.new('RGBA', (BOX * 4, BOX * 4), (0, 0, 0, 0))
        ImageDraw.Draw(disc).ellipse([0, 0, DISC * 4 - 1, DISC * 4 - 1], fill=RED)
        canvas.alpha_composite(disc.resize((BOX, BOX), Image.Resampling.LANCZOS),
                               ((BOX - DISC) // 2, (BOX - DISC) // 2))
    glyph = Image.new('RGBA', mask.size, (255, 255, 255, 255) if selected else INK)
    glyph.putalpha(mask)
    canvas.alpha_composite(glyph, ((BOX - mask.width) // 2, (BOX - mask.height) // 2))
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shots = {}
    for key, (shot, x0, y0, x1, y1) in GLYPHS.items():
        if shot not in shots:
            shots[shot] = reference(shot)
        crop = shots[shot].crop((x0, y0, x1 + 1, y1 + 1))
        scale = BOX / REF_DISC_PX
        mask = clean_mask(crop, int(round(crop.width * scale)), int(round(crop.height * scale)))
        compose(mask, False).save(os.path.join(OUT_DIR, key + '-v2.png'))
        compose(mask, True).save(os.path.join(OUT_DIR, key + '-v2-active.png'))
        print(key, crop.size, '->', mask.size)


if __name__ == '__main__':
    main()
