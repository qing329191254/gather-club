# -*- coding: utf-8 -*-
"""Generate homepage static assets for 天天俱乐部."""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC = os.path.join(ROOT, "static")
DIRS = [
    os.path.join(STATIC, "tab"),
    os.path.join(STATIC, "icons"),
    os.path.join(STATIC, "banners"),
    os.path.join(STATIC, "stores"),
]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BD = "C:/Windows/Fonts/msyhbd.ttc"


def font(size, bold=False):
    path = FONT_BD if bold and os.path.exists(FONT_BD) else FONT
    return ImageFont.truetype(path, size, index=0)


def save(im, path):
    im.save(path, "PNG")
    print("saved", path)


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def draw_icon_bg(size=180, radius=48, color=(247, 236, 224, 255)):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=color)
    return im


def gen_chat_icon():
    im = draw_icon_bg()
    d = ImageDraw.Draw(im)
    # decorative gold swirl
    d.arc((108, 18, 168, 78), 200, 40, fill=(232, 196, 150, 220), width=8)
    d.ellipse((138, 22, 154, 38), fill=(232, 196, 150, 180))
    # red bubble
    d.rounded_rectangle((36, 42, 132, 122), radius=36, fill=(226, 54, 54, 255))
    d.polygon([(58, 118), (48, 148), (86, 122)], fill=(226, 54, 54, 255))
    for x in (62, 84, 106):
        d.ellipse((x, 72, x + 14, 86), fill=(255, 255, 255, 255))
    save(im, os.path.join(STATIC, "icons", "chat.png"))


def gen_shop_icon():
    im = draw_icon_bg()
    d = ImageDraw.Draw(im)
    d.arc((12, 22, 78, 88), 220, 10, fill=(232, 196, 150, 220), width=8)
    d.ellipse((18, 28, 34, 44), fill=(232, 196, 150, 180))
    # store
    d.rectangle((52, 86, 128, 132), fill=(226, 54, 54, 255))
    d.polygon([(44, 86), (90, 48), (136, 86)], fill=(226, 54, 54, 255))
    d.rectangle((78, 100, 102, 132), fill=(255, 255, 255, 255))
    save(im, os.path.join(STATIC, "icons", "shop.png"))


def stroke_icon(draw_fn, path, color=(40, 40, 40, 255), size=120, width=8):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_fn(d, color, width)
    save(im, path)


def gen_order_icon():
    def draw(d, c, w):
        d.rounded_rectangle((22, 28, 98, 100), radius=10, outline=c, width=w)
        d.arc((40, 14, 80, 54), 200, 340, fill=c, width=w)
        d.line((40, 56, 80, 56), fill=c, width=w - 1)
        d.line((40, 72, 72, 72), fill=c, width=w - 1)
    stroke_icon(draw, os.path.join(STATIC, "icons", "order.png"))


def gen_checkin_icon():
    def draw(d, c, w):
        d.rounded_rectangle((20, 28, 100, 104), radius=12, outline=c, width=w)
        d.line((20, 48, 100, 48), fill=c, width=w - 1)
        d.line((40, 18, 40, 40), fill=c, width=w)
        d.line((80, 18, 80, 40), fill=c, width=w)
        d.ellipse((70, 62, 94, 86), outline=c, width=w - 1)
        d.line((76, 74, 84, 82), fill=c, width=w - 1)
        d.line((84, 82, 96, 66), fill=c, width=w - 1)
    stroke_icon(draw, os.path.join(STATIC, "icons", "checkin.png"))


def gen_phone_icon():
    """iOS-style handset: two parallel caps + connecting curve."""
    gold = (168, 120, 88, 255)
    canvas = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    sw = 30
    ang = math.radians(-18)
    clen = 96

    def _line(p1, p2):
        d.line([p1, p2], fill=gold, width=sw)
        r = sw / 2.0
        for p in (p1, p2):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=gold)

    ex, ey = 150, 148
    e1 = (ex - math.cos(ang) * clen / 2, ey - math.sin(ang) * clen / 2)
    e2 = (ex + math.cos(ang) * clen / 2, ey + math.sin(ang) * clen / 2)
    _line(e1, e2)
    mx, my = 228, 246
    m1 = (mx - math.cos(ang) * clen / 2, my - math.sin(ang) * clen / 2)
    m2 = (mx + math.cos(ang) * clen / 2, my + math.sin(ang) * clen / 2)
    _line(m1, m2)
    cpx, cpy = 258, 158
    pts = []
    for i in range(40):
        t = i / 39.0
        x = (1 - t) * (1 - t) * e2[0] + 2 * (1 - t) * t * cpx + t * t * m1[0]
        y = (1 - t) * (1 - t) * e2[1] + 2 * (1 - t) * t * cpy + t * t * m1[1]
        pts.append((x, y))
    d.line(pts, fill=gold, width=sw, joint="curve")
    r = sw / 2.0
    for p in (pts[0], pts[-1]):
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=gold)
    bb = canvas.getbbox()
    im = canvas.crop(bb)
    w, h = im.size
    side = max(w, h) + 24
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - w) // 2, (side - h) // 2), im)
    save(sq.resize((160, 160), Image.Resampling.LANCZOS), os.path.join(STATIC, "icons", "phone.png"))


def gen_pin_icon():
    """Filled near_me arrow pointing northeast."""
    pin_c = (232, 168, 74, 255)
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(100, 12), (148, 188), (100, 132), (52, 188)], fill=pin_c)
    im = im.rotate(-45, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    bb = im.getbbox()
    im = im.crop(bb)
    w, h = im.size
    side = max(w, h) + 12
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - w) // 2, (side - h) // 2), im)
    save(sq.resize((160, 160), Image.Resampling.LANCZOS), os.path.join(STATIC, "icons", "pin.png"))


def gen_tab_icons():
    """Line icons on 160 canvas; custom tabBar displays them at 72rpx."""
    from PIL import ImageChops

    ink = (34, 34, 34, 255)
    red = (230, 71, 80, 255)
    size = 160
    tab_dir = os.path.join(STATIC, "tab")

    def colorize(mask, color):
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        im.paste(color, (0, 0), mask)
        return im

    def heart_mask(scale=1.0, dy=0):
        m = Image.new("L", (size, size), 0)
        d = ImageDraw.Draw(m)
        cx, cy = 80, 74 + dy
        s = 62 * scale
        d.ellipse((cx - s, cy - s * 0.78, cx + 4, cy + s * 0.38), fill=255)
        d.ellipse((cx - 4, cy - s * 0.78, cx + s, cy + s * 0.38), fill=255)
        d.polygon(
            [(cx - s + 1, cy + s * 0.02), (cx + s - 1, cy + s * 0.02), (cx, cy + s * 1.18)],
            fill=255,
        )
        return m

    def caps(d, pts, color, sw):
        d.line(pts, fill=color, width=sw, joint="curve")
        r = sw / 2.0
        for p in (pts[0], pts[-1]):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)

    save(colorize(ImageChops.subtract(heart_mask(1.0), heart_mask(0.68, 3)), ink), os.path.join(tab_dir, "home.png"))
    save(colorize(heart_mask(1.0), red), os.path.join(tab_dir, "home-active.png"))

    def people(color):
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        sw = 13
        d.ellipse((22, 22, 70, 70), outline=color, width=sw)
        d.ellipse((90, 22, 138, 70), outline=color, width=sw)
        left = [(46 + 40 * math.cos(math.radians(205 + 145 * i / 21)), 100 + 36 * math.sin(math.radians(205 + 145 * i / 21))) for i in range(22)]
        right = [(114 + 40 * math.cos(math.radians(205 + 145 * i / 21)), 100 + 36 * math.sin(math.radians(205 + 145 * i / 21))) for i in range(22)]
        caps(d, left, color, sw)
        caps(d, right, color, sw)
        return im

    save(people(ink), os.path.join(tab_dir, "gather.png"))
    save(people(red), os.path.join(tab_dir, "gather-active.png"))

    def video(color):
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        sw = 13
        d.rounded_rectangle((16, 36, 144, 124), radius=30, outline=color, width=sw)
        tri = [(58, 54), (58, 106), (114, 80)]
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            d.line([a, b], fill=color, width=12)
            r = 6
            d.ellipse((a[0] - r, a[1] - r, a[0] + r, a[1] + r), fill=color)
            d.ellipse((b[0] - r, b[1] - r, b[0] + r, b[1] + r), fill=color)
        return im

    save(video(ink), os.path.join(tab_dir, "video.png"))
    save(video(red), os.path.join(tab_dir, "video-active.png"))

    def mine(color):
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        sw = 13
        d.ellipse((46, 16, 114, 84), outline=color, width=sw)
        body = [(80 + 56 * math.cos(math.radians(205 + 145 * i / 23)), 128 + 38 * math.sin(math.radians(205 + 145 * i / 23))) for i in range(24)]
        caps(d, body, color, sw)
        return im

    save(mine(ink), os.path.join(tab_dir, "mine.png"))
    save(mine(red), os.path.join(tab_dir, "mine-active.png"))


def gen_hotel_banner():
    w, h = 1125, 780
    im = Image.new("RGB", (w, h), (244, 201, 165))
    d = ImageDraw.Draw(im)
    # title
    d.text((56, 48), "上海出发2小时即达·周末不加价", font=font(42, True), fill=(32, 32, 32))
    d.text((56, 112), "周边精选酒店推荐", font=font(30), fill=(130, 120, 112))
    # car
    d.rounded_rectangle((860, 150, 1040, 198), radius=24, fill=(255, 246, 236))
    d.ellipse((880, 188, 918, 226), fill=(255, 246, 236))
    d.ellipse((980, 188, 1018, 226), fill=(255, 246, 236))
    d.ellipse((1008, 132, 1048, 172), fill=(255, 246, 236))
    # map pin card
    d.rounded_rectangle((70, 220, 320, 470), radius=130, fill=(255, 246, 236))
    d.polygon([(195, 520), (130, 430), (260, 430)], fill=(255, 246, 236))
    d.line((120, 300, 270, 300), fill=(230, 210, 190), width=6)
    d.line((195, 250, 195, 400), fill=(230, 210, 190), width=6)
    d.ellipse((176, 282, 214, 320), outline=(180, 170, 160), width=6)
    d.text((86, 318), "上海", font=font(22), fill=(160, 150, 140))
    # train
    d.ellipse((430, 250, 1120, 620), fill=(255, 246, 236))
    d.rectangle((620, 300, 1125, 560), fill=(255, 246, 236))
    d.ellipse((700, 360, 820, 420), fill=(244, 201, 165))
    # slider
    d.rounded_rectangle((70, 600, 820, 636), radius=18, fill=(255, 246, 236))
    d.ellipse((800, 592, 852, 644), fill=(255, 246, 236))
    d.text((870, 592), "2小时", font=font(40, True), fill=(32, 32, 32))
    d.text((780, 680), "周末通用·无需加价", font=font(26), fill=(150, 140, 132))
    save(im.convert("RGBA"), os.path.join(STATIC, "banners", "hotel.png"))


def gen_nye_banner():
    w, h = 1125, 780
    im = Image.new("RGB", (w, h), (226, 32, 36))
    d = ImageDraw.Draw(im)
    # lanterns
    for x in (70, 980):
        d.line((x + 30, 20, x + 30, 70), fill=(40, 10, 10), width=6)
        d.ellipse((x, 70, x + 60, 150), fill=(40, 10, 10))
        d.rectangle((x + 22, 150, x + 38, 190), fill=(40, 10, 10))
        d.ellipse((x + 18, 186, x + 42, 208), fill=(40, 10, 10))
    # knots
    for x, y in ((160, 90), (960, 90), (80, 260), (1040, 260)):
        d.line((x - 16, y, x + 16, y + 16), fill=(40, 10, 10), width=5)
        d.line((x + 16, y, x - 16, y + 16), fill=(40, 10, 10), width=5)
        d.line((x, y - 10, x, y + 26), fill=(40, 10, 10), width=5)
    # brand pill
    d.rounded_rectangle((300, 70, 825, 168), radius=50, outline=(255, 230, 160), width=8)
    for i in range(14):
        ang = i / 14 * math.pi
        px = 300 + 20 + i * 38
        d.ellipse((px, 62, px + 16, 78), fill=(255, 230, 160))
        d.ellipse((px, 160, px + 16, 176), fill=(255, 230, 160))
    d.text((360, 88), "天天俱乐部", font=font(52, True), fill=(255, 230, 160))
    d.text((430, 196), "2027", font=font(72, True), fill=(255, 220, 130))
    # sheep
    d.ellipse((760, 210, 900, 310), fill=(255, 214, 120))
    d.ellipse((820, 170, 880, 230), fill=(255, 214, 120))
    d.polygon([(868, 176), (900, 150), (880, 196)], fill=(255, 214, 120))
    d.polygon([(832, 176), (800, 150), (820, 196)], fill=(255, 214, 120))
    d.ellipse((900, 400, 1080, 560), fill=(255, 214, 120))
    d.ellipse((980, 340, 1060, 420), fill=(255, 214, 120))
    d.text((160, 320), "年夜饭", font=font(150, True), fill=(255, 232, 170))
    d.text((200, 520), "开卖啦", font=font(140, True), fill=(255, 232, 170))
    save(im.convert("RGBA"), os.path.join(STATIC, "banners", "nye.png"))


def gen_store_cover(name, filename):
    w, h = 1080, 520
    im = Image.new("RGB", (w, h), (18, 10, 6))
    px = im.load()
    cx, cy = w // 2, int(h * 0.58)
    for y in range(h):
        for x in range(0, w, 2):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            glow = max(0, 1 - dist / 520)
            r = int(18 + 90 * glow)
            g = int(10 + 55 * glow)
            b = int(6 + 12 * glow)
            px[x, y] = (r, g, b)
            if x + 1 < w:
                px[x + 1, y] = (r, g, b)
    d = ImageDraw.Draw(im)
    # plaque
    box = (150, 70, 930, 280)
    d.rounded_rectangle(box, radius=90, fill=(196, 42, 46))
    d.rounded_rectangle((142, 62, 938, 288), radius=96, outline=(255, 228, 160), width=10)
    # lights
    for i in range(18):
        x = 170 + i * 42
        d.ellipse((x, 52, x + 18, 70), fill=(255, 236, 180))
        d.ellipse((x, 280, x + 18, 298), fill=(255, 236, 180))
    for i in range(5):
        y = 90 + i * 38
        d.ellipse((138, y, 156, y + 18), fill=(255, 236, 180))
        d.ellipse((924, y, 942, y + 18), fill=(255, 236, 180))
    d.text((230, 120), "天天俱乐部", font=font(86, True), fill=(255, 236, 200))
    # store name
    tw = d.textlength(name, font=font(78, True))
    d.text(((w - tw) / 2, 340), name, font=font(78, True), fill=(255, 236, 200))
    # floor glow
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((180, 400, 900, 520), fill=(90, 55, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    im = Image.blend(im, glow, 0.35)
    save(im.convert("RGBA"), os.path.join(STATIC, "stores", filename))


def main():
    gen_chat_icon()
    gen_shop_icon()
    gen_order_icon()
    gen_checkin_icon()
    # phone/pin come from the original screenshot crop — do not overwrite
    # tabBar icons are rebuilt from the reference shots by gen-tab-icons.py
    gen_hotel_banner()
    gen_nye_banner()
    stores = [
        ("上海世博店", "shibo.png"),
        ("上海莘庄店", "xinzhuang.png"),
        ("上海亚新店", "yaxin.png"),
        ("上海共康店", "gongkang.png"),
        ("宁波天一店", "ningbo.png"),
    ]
    for name, fn in stores:
        gen_store_cover(name, fn)
    print("done")


if __name__ == "__main__":
    main()
