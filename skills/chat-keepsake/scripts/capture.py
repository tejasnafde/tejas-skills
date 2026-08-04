#!/usr/bin/env python3
"""
Screenshot a long keepsake page for review, working around the things that make
this harder than it should be.

    python3 capture.py site/index.html                 # full page, sliced
    python3 capture.py site/index.html --skip 10        # only sections 11+ (the tail)
    python3 capture.py site/index.html --pdf out.pdf    # print to PDF

Three problems this solves:

1. Chromium will not produce a screenshot taller than 16384px. A decade-long keepsake
   page runs past that, so the bottom silently vanishes and you review a page whose
   ending you have never seen. --skip N hides the first N sections so the tail renders
   near the top.

2. A tall window breaks any `100svh` hero, because the hero becomes as tall as the
   window. The injected stylesheet pins it to a fixed height for capture only.

3. Scroll-reveal animations leave everything at opacity 0 in a headless render, and
   timed intro sequences are mid-fade when the shutter fires. Forcing reduced motion
   makes well-built pages snap to their final state.

The injected CSS is written to a throwaway copy. Your source file is never touched.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

SHELL_CANDIDATES = [
    "~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
    "~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

CAPTURE_CSS = """
<style id="__capture__">
  /* a tall window would otherwise make these viewport-height units enormous */
  #hero, [data-hero] { min-height: 1000px !important; }
  .seq { min-height: 560px !important; }
  body.locked { overflow: visible !important; height: auto !important; }
  /* fixed atmospherics tile across a tall canvas and muddy the review */
  .glow, .vignette, .grain { display: none !important; }
  __SKIP__
</style></head>"""


def find_chrome():
    import glob
    for pat in SHELL_CANDIDATES:
        for hit in sorted(glob.glob(os.path.expanduser(pat)), reverse=True):
            if os.path.isfile(hit) and os.access(hit, os.X_OK):
                return hit
    sys.exit("No Chromium found. Install a Chrome, or `npx playwright install "
             "chromium-headless-shell`.")


def build_capture_copy(src, skip):
    html = open(src, encoding="utf-8", errors="replace").read()
    skip_rule = ""
    if skip:
        skip_rule = (f"main > section:nth-of-type(-n+{skip}) "
                     f"{{ display: none !important; }}")
    css = CAPTURE_CSS.replace("__SKIP__", skip_rule)
    if "</head>" not in html:
        sys.exit("No </head> in the page; cannot inject capture styles.")
    html = html.replace("</head>", css, 1)

    d = tempfile.mkdtemp(prefix="keepsake-capture-")
    # copy sibling assets so relative image paths still resolve
    src_dir = os.path.dirname(os.path.abspath(src)) or "."
    for entry in os.listdir(src_dir):
        p = os.path.join(src_dir, entry)
        if os.path.isdir(p):
            shutil.copytree(p, os.path.join(d, entry), dirs_exist_ok=True)
    out = os.path.join(d, "capture.html")
    open(out, "w", encoding="utf-8").write(html)
    return out, d


def run(chrome, args):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-prefers-reduced-motion",
                    "--run-all-compositor-stages-before-draw"] + args,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def trim_and_slice(png, out_prefix, slice_h):
    """Crop the white canvas tail and the dead space, then slice for review."""
    try:
        from PIL import Image
    except ImportError:
        print(f"  (install Pillow to auto-trim and slice; raw file at {png})")
        return [png]

    im = Image.open(png).convert("RGB")
    w, h = im.size
    g = im.convert("L")
    px = g.load()

    # 1. where does the page end and the blank canvas begin
    end = h
    step = max(1, w // 240)
    for y in range(h - 1, 0, -3):
        row = [px[x, y] for x in range(0, w, step)]
        if sum(row) / len(row) < 200:       # not near-white
            end = y
            break
    # 2. last row containing actual text
    last = 0
    for y in range(end - 12, 0, -2):
        if max(px[x, y] for x in range(0, w, step)) > 105:
            last = y
            break
    im = im.crop((0, 0, w, min(last + 80, h)))

    W, H = im.size
    n = (H + slice_h - 1) // slice_h
    files = []
    for i in range(n):
        p = f"{out_prefix}-{i:02d}.png"
        im.crop((0, i * slice_h, W, min((i + 1) * slice_h, H))).save(p)
        files.append(p)
    print(f"  page height {H}px, {n} slice(s)")
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--skip", type=int, default=0,
                    help="hide the first N <section>s (use for the tail of a long page)")
    ap.add_argument("--width", type=int, default=430, help="viewport width (phone)")
    ap.add_argument("--height", type=int, default=16000,
                    help="capture height; Chromium hard-caps screenshots at 16384")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--slice", type=int, default=1900, dest="slice_h")
    ap.add_argument("--out", default="review")
    ap.add_argument("--pdf", help="print to this PDF instead of screenshotting")
    a = ap.parse_args()

    if a.height > 16384:
        print("! capping height at 16384; Chromium cannot screenshot taller than that.")
        print("  Use --skip N to capture the tail of a longer page.")
        a.height = 16384

    chrome = find_chrome()
    page, tmp = build_capture_copy(a.page, a.skip)
    url = "file://" + page

    if a.pdf:
        run(chrome, ["--no-pdf-header-footer", "--virtual-time-budget=15000",
                     f"--print-to-pdf={os.path.abspath(a.pdf)}", url])
        print(f"-> {a.pdf}")
    else:
        raw = os.path.abspath(f"{a.out}-raw.png")
        run(chrome, [f"--force-device-scale-factor={a.scale}",
                     f"--window-size={a.width},{a.height}",
                     "--virtual-time-budget=12000",
                     f"--screenshot={raw}", url])
        if not os.path.exists(raw):
            sys.exit("Capture failed. Try a smaller --height.")
        for f in trim_and_slice(raw, a.out, a.slice_h):
            print(f"-> {f}")
        os.remove(raw)

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
