# Renders an animated SVG diagram to MP4: landscape at the SVG's own size,
# and a 1080x1920 vertical version (diagram centred on the dark background).
# Frames are taken by pausing every CSS animation at an exact time, so the
# video is frame-perfect rather than a screen recording.
#
# Usage: python render_video.py <in.svg> <out-basename> <cycle_seconds> [cycles]
#   e.g. python render_video.py 02-storage-tiers/diagrams/tier-flow.svg \
#        02-storage-tiers/diagrams/tier-flow 18 2
# Needs: playwright (uses the installed Microsoft Edge) and imageio-ffmpeg.
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

FPS = 30
BG = "#060D1F"

src, base = Path(sys.argv[1]), sys.argv[2]
cycle = float(sys.argv[3])
cycles = int(sys.argv[4]) if len(sys.argv) > 4 else 2

svg = src.read_text(encoding="utf-8")
w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

html = f"<!doctype html><html><body style='margin:0;background:{BG}'>{svg}</body></html>"
land = f"{base}.mp4"
enc = subprocess.Popen(
    [ffmpeg, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
     "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
     "-movflags", "+faststart", land],
    stdin=subprocess.PIPE,
)

total = int(cycle * cycles * FPS)
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")  # the installed Edge, no browser download
    page = browser.new_page(viewport={"width": w, "height": h})
    page.set_content(html)
    page.wait_for_timeout(300)
    for i in range(total):
        t_ms = (i / FPS) * 1000
        page.evaluate(
            "t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })",
            t_ms,
        )
        enc.stdin.write(page.screenshot(type="png"))
    browser.close()
enc.stdin.close()
enc.wait()

vert = f"{base}-vertical.mp4"
subprocess.run(
    [ffmpeg, "-y", "-loglevel", "error", "-i", land,
     "-vf", f"scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color={BG}",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", vert],
    check=True,
)
print(land, vert, f"{total} frames")
