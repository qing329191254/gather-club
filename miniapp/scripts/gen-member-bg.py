# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math, os, random, numpy as np

out_dir = r'D:\demo\gather-club\miniapp\static\member'
os.makedirs(out_dir, exist_ok=True)


def make_noise(w, h, seed=1):
	rnd = random.Random(seed)
	nw, nh = max(1, w // 10), max(1, h // 10)
	arr = np.array([[rnd.randint(0, 255) for _ in range(nw)] for _ in range(nh)], dtype=np.uint8)
	base = Image.fromarray(arr, mode='L').resize((w, h), Image.BICUBIC)
	return base.filter(ImageFilter.GaussianBlur(radius=22))


def contour_overlay(w, h, line_rgb, seed, density=18, alpha=80):
	field = np.array(make_noise(w, h, seed), dtype=np.float32)
	# approximate contours via gradient magnitude of quantized field
	q = np.floor(field / (255.0 / density))
	gy = np.abs(np.diff(q, axis=0, prepend=q[:1]))
	gx = np.abs(np.diff(q, axis=1, prepend=q[:, :1]))
	edge = np.clip(gx + gy, 0, 1)
	# fade bottom a bit
	fade = np.linspace(1.0, 0.65, h, dtype=np.float32)[:, None]
	a = (edge * alpha * fade).astype(np.uint8)
	r = np.full((h, w), line_rgb[0], dtype=np.uint8)
	g = np.full((h, w), line_rgb[1], dtype=np.uint8)
	b = np.full((h, w), line_rgb[2], dtype=np.uint8)
	rgba = np.dstack([r, g, b, a])
	img = Image.fromarray(rgba, 'RGBA')
	return img.filter(ImageFilter.GaussianBlur(radius=0.8))


def radial_glow(w, h, color, cy=0.14, strength=0.5):
	ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
	xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
	dx = (xs - 0.5) / 0.75
	dy = (ys - cy) / 0.55
	d = np.sqrt(dx * dx + dy * dy)
	t = np.clip(1.0 - d, 0, 1) ** 2
	a = (t * 255 * strength).astype(np.uint8)
	r = np.full((h, w), color[0], dtype=np.uint8)
	g = np.full((h, w), color[1], dtype=np.uint8)
	b = np.full((h, w), color[2], dtype=np.uint8)
	return Image.fromarray(np.dstack([r, g, b, a]), 'RGBA').filter(ImageFilter.GaussianBlur(20))


def make_bg(name, base_top, base_bot, line_rgb, seed, glow_rgb, card=False):
	w, h = (750, 1624) if not card else (680, 280)
	ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
	t = ys ** 0.85
	rgb = np.zeros((h, w, 3), dtype=np.uint8)
	for i in range(3):
		rgb[:, :, i] = (base_top[i] + (base_bot[i] - base_top[i]) * t).astype(np.uint8)
	rgba = Image.fromarray(rgb, 'RGB').convert('RGBA')
	rgba = Image.alpha_composite(
		rgba,
		radial_glow(w, h, glow_rgb, cy=0.12 if not card else 0.45, strength=0.45 if not card else 0.28),
	)
	rgba = Image.alpha_composite(
		rgba,
		contour_overlay(w, h, line_rgb, seed, density=18 if not card else 12, alpha=70 if not card else 48),
	)
	# vignette
	xs = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
	ys2 = np.linspace(0, 1, h, dtype=np.float32)[:, None]
	vig_a = (np.clip(xs * xs, 0, 1) * (0.25 + 0.75 * ys2) * 100).astype(np.uint8)
	vig = Image.fromarray(np.dstack([np.zeros_like(vig_a), np.zeros_like(vig_a), np.zeros_like(vig_a), vig_a]), 'RGBA')
	vig = vig.filter(ImageFilter.GaussianBlur(14))
	rgba = Image.alpha_composite(rgba, vig)
	out = rgba.convert('RGB')
	path = os.path.join(out_dir, name)
	out.save(path, quality=88, optimize=True)
	print('wrote', path, out.size)


make_bg('bg-v0.jpg', (11, 20, 40), (6, 10, 20), (150, 180, 220), 10, (90, 130, 190))
make_bg('card-v0.jpg', (236, 242, 252), (196, 210, 232), (170, 190, 220), 11, (200, 210, 240), card=True)

make_bg('bg-v1.jpg', (8, 22, 48), (5, 12, 28), (120, 175, 235), 20, (70, 140, 220))
make_bg('card-v1.jpg', (220, 236, 255), (170, 205, 245), (140, 180, 230), 21, (180, 210, 250), card=True)

make_bg('bg-v2.jpg', (22, 14, 36), (10, 8, 20), (190, 155, 230), 30, (140, 100, 200))
make_bg('card-v2.jpg', (236, 228, 250), (200, 180, 235), (180, 150, 220), 31, (210, 190, 240), card=True)

make_bg('bg-v3.jpg', (30, 18, 10), (12, 8, 5), (210, 168, 95), 40, (190, 140, 65))
make_bg('card-v3.jpg', (247, 234, 202), (222, 196, 148), (195, 162, 100), 41, (235, 205, 145), card=True)

print('done')
