from pathlib import Path
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
# np.fromfile + imdecode는 Windows 한글 경로에서도 사용할 수 있다.
bgr = cv2.imdecode(np.fromfile(ASSETS / "Lenna.png", dtype=np.uint8), cv2.IMREAD_COLOR)
if bgr is None:
    raise FileNotFoundError("assets/Lenna.png를 확인하세요.")
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

def panels(filename, items, cols=3):
    rows = (len(items) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(3.6 * cols, 3.6 * rows), squeeze=False)
    for ax, (title, data, limits) in zip(axes.flat, items):
        if data.ndim == 2:
            ax.imshow(data, cmap="gray", vmin=limits[0], vmax=limits[1])
        else:
            ax.imshow(data)
        ax.set_title(title, fontsize=12)
        ax.axis("off")
    for ax in list(axes.flat)[len(items):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(ASSETS / filename, dpi=150)
    plt.close(fig)


# ===== 1 =====
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)
panels("01_colors.png", [
    ("RGB display", rgb, None), ("Grayscale", gray, (0, 255)),
    ("H: hue (0-179)", h, (0, 179)), ("S: saturation", s, (0, 255)),
    ("V: value", v, (0, 255)), ("BGR shown as RGB: WRONG", bgr, None)
])
print("shape:", bgr.shape, "dtype:", bgr.dtype)
print("pixel (x=125, y=125), RGB:", rgb[125, 125].tolist())
print("gray:", int(gray[125, 125]), "HSV:", hsv[125, 125].tolist())

# ===== 2 =====
b, g, r = cv2.split(bgr)
zero = np.zeros_like(r)
red_only = cv2.merge([r, zero, zero])  # RGB 배열: Matplotlib 표시용
green_only = cv2.merge([zero, g, zero])
blue_only = cv2.merge([zero, zero, b])
panels("02_channels.png", [
    ("R values", r, (0, 255)), ("G values", g, (0, 255)), ("B values", b, (0, 255)),
    ("Red only (RGB)", red_only, None), ("Green only (RGB)", green_only, None),
    ("Blue only (RGB)", blue_only, None)
])
assert np.array_equal(cv2.merge([b, g, r]), bgr)
print("RGB channel means:", [float(c.mean()) for c in (r, g, b)])

# ===== 3 =====
ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
y, cr, cb = cv2.split(ycrcb)  # 주의: Y, Cr, Cb 순서
restored = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
neutral_y = np.full_like(y, 128)
chroma_display = cv2.cvtColor(cv2.merge([neutral_y, cr, cb]), cv2.COLOR_YCrCb2RGB)
panels("03_ycrcb.png", [
    ("Original RGB", rgb, None), ("Y: luma", y, (0, 255)),
    ("Cr: red difference", cr, (0, 255)), ("Cb: blue difference", cb, (0, 255)),
    ("Y fixed at 128", chroma_display, None),
    ("Round-trip RGB", cv2.cvtColor(restored, cv2.COLOR_BGR2RGB), None)
])
error = np.abs(restored.astype(np.int16) - bgr.astype(np.int16))
print("Y, Cr, Cb at (125,125):", ycrcb[125, 125].tolist())
print("round-trip max error:", int(error.max()), "MAE:", float(error.mean()))

# ===== 4 =====
hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
prob = hist / gray.size
cdf = np.cumsum(prob)
assert int(hist.sum()) == gray.size
fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
axes[0].bar(np.arange(256), hist, width=1, color="#516b91")
axes[0].set(title="Grayscale histogram", xlabel="Intensity (0-255)", ylabel="Pixel count", xlim=(0, 255))
for channel, color, name in [(0, "red", "R"), (1, "green", "G"), (2, "blue", "B")]:
    counts = np.bincount(rgb[:, :, channel].ravel(), minlength=256)
    axes[1].plot(counts, color=color, label=name, linewidth=1)
axes[1].set(title="RGB histograms", xlabel="Channel value", ylabel="Pixel count", xlim=(0,255))
axes[1].legend()
axes[2].plot(cdf, color="#ae5427")
axes[2].set(title="Grayscale CDF", xlabel="Intensity", ylabel="Cumulative probability", xlim=(0,255), ylim=(0,1))
fig.tight_layout()
fig.savefig(ASSETS / "04_histograms.png", dpi=150)
plt.close(fig)
rng = np.random.default_rng(42)
shuffled = rng.permutation(gray.ravel()).reshape(gray.shape)
assert np.array_equal(np.bincount(gray.ravel(), minlength=256), np.bincount(shuffled.ravel(), minlength=256))
panels("04_same_hist.png", [("Original grayscale", gray, (0,255)), ("Shuffled: SAME histogram", shuffled, (0,255))], cols=2)
print("pixels:", gray.size, "hist sum:", int(hist.sum()), "mean:", float(gray.mean()))

# ===== 5 =====
equalized = cv2.equalizeHist(gray)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
local = clahe.apply(gray)
ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
y, cr, cb = cv2.split(ycrcb)
color_y = cv2.cvtColor(cv2.merge([cv2.equalizeHist(y), cr, cb]), cv2.COLOR_YCrCb2RGB)
wrong_color = cv2.cvtColor(cv2.merge([cv2.equalizeHist(c) for c in cv2.split(bgr)]), cv2.COLOR_BGR2RGB)
panels("05_equalization.png", [
    ("Original grayscale", gray, (0,255)), ("Global equalization", equalized, (0,255)),
    ("CLAHE", local, (0,255)), ("Original RGB", rgb, None),
    ("Equalize Y only", color_y, None), ("Equalize R/G/B separately", wrong_color, None)
])
fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharex=True, sharey="row")
for axcol, (title, im) in zip(axes.T, [("Original",gray), ("Global",equalized), ("CLAHE",local)]):
    counts = np.bincount(im.ravel(), minlength=256)
    axcol[0].bar(np.arange(256), counts, width=1, color="#526e92")
    axcol[0].set(title=title, ylabel="Pixel count", xlim=(0,255))
    axcol[1].plot(np.cumsum(counts) / im.size, color="#ae5427")
    axcol[1].set(xlabel="Intensity", ylabel="CDF", ylim=(0,1))
fig.tight_layout()
fig.savefig(ASSETS / "05_distributions.png", dpi=150)
plt.close(fig)
for title, im in [("Original",gray), ("Global",equalized), ("CLAHE",local)]:
    print(title, "min/max/mean/std:", int(im.min()), int(im.max()), float(im.mean()), float(im.std()))

