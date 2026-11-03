import json, subprocess, sys, html, os
# Renders a .drawio file to PNG with headless Edge and the diagrams.net viewer.
# Usage: python render_drawio.py <in.drawio> <out.png> <width> <height>
src, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
xml = open(src, encoding="utf-8").read()
cfg = {"xml": xml, "toolbar": "", "nav": False, "lightbox": False, "border": 0, "resize": False, "zoom": 1}
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#060D1F;width:{w}px;height:{h}px;overflow:hidden}}</style></head>
<body><div class="mxgraph" style="width:{w}px" data-mxgraph="{html.escape(json.dumps(cfg))}"></div>
<script src="https://viewer.diagrams.net/js/viewer-static.min.js"></script></body></html>"""
hp = os.path.join(os.path.dirname(out), "_render.html")
open(hp, "w", encoding="utf-8").write(page)
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
subprocess.run([edge, "--headless=new", "--user-data-dir=" + os.path.join(os.path.dirname(out), "edgeprof2"), "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                "--force-device-scale-factor=2", "--virtual-time-budget=20000", f"--screenshot={out}",
                "file:///" + hp.replace("\\", "/")], check=True)
print("rendered", out)
