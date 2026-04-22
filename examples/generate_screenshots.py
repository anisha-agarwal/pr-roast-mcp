#!/usr/bin/env python3
"""Generate styled screenshots from roast markdown files."""

import subprocess
import os
import re
import html as html_mod

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))


def md_to_html_card(title: str, pr_ref: str, content: str) -> str:
    """Convert roast markdown to a styled HTML card."""
    # Escape HTML
    content = html_mod.escape(content)
    # Convert markdown-ish formatting
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    # Convert headers
    content = re.sub(r'^### (.+)$', r'<div style="color:#fca5a5;font-weight:700;font-size:14px;margin:16px 0 8px">\1</div>', content, flags=re.M)
    content = re.sub(r'^## (.+)$', r'<div style="color:#e2e8f0;font-weight:700;font-size:16px;margin:20px 0 10px">\1</div>', content, flags=re.M)
    content = re.sub(r'^# (.+)$', r'<div style="color:#ef4444;font-weight:800;font-size:22px;margin:0 0 16px">\1</div>', content, flags=re.M)
    # Convert bullet points
    content = re.sub(r'^- (.+)$', r'<div style="padding-left:16px;margin:4px 0">• \1</div>', content, flags=re.M)
    # Convert code blocks
    content = re.sub(
        r'```\w*\n(.*?)```',
        r'<pre style="background:#12121a;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:12px 16px;font-family:JetBrains Mono,monospace;font-size:11px;color:#a9b1d6;margin:8px 0;overflow-x:auto">\1</pre>',
        content, flags=re.S
    )
    # Paragraphs
    content = re.sub(r'\n\n', '<br><br>', content)
    content = re.sub(r'---', '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:16px 0">', content)

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:#0f1115; color:#a9b1d6; width:1200px; padding:40px; font-size:13px; line-height:1.6; }}
.card {{ background:#1a1b26; border:1px solid rgba(239,68,68,0.2); border-radius:16px; overflow:hidden; box-shadow:0 20px 60px rgba(0,0,0,0.5); }}
.hdr {{ background:#16161e; padding:14px 24px; display:flex; align-items:center; gap:10px; border-bottom:1px solid rgba(239,68,68,0.1); }}
.dots {{ display:flex; gap:6px; }}
.d {{ width:12px; height:12px; border-radius:50%; }}
.r {{ background:#f7768e; }} .y {{ background:#e0af68; }} .g {{ background:#9ece6a; }}
.t {{ font-family:'JetBrains Mono',monospace; font-size:12px; color:#565f89; margin-left:8px; }}
.b {{ margin-left:auto; background:rgba(239,68,68,0.15); color:#fca5a5; font-size:10px; font-weight:700; padding:3px 10px; border-radius:999px; text-transform:uppercase; }}
.body {{ padding:24px 28px; }}
code {{ font-family:'JetBrains Mono',monospace; font-size:11px; background:#12121a; padding:1px 5px; border-radius:3px; color:#7aa2f7; }}
strong {{ color:#e2e8f0; }}
em {{ color:#c0caf5; }}
.ft {{ padding:10px 24px; background:#12121a; border-top:1px solid rgba(255,255,255,0.04); font-family:'JetBrains Mono',monospace; font-size:10px; color:#565f89; text-align:right; }}
</style></head>
<body><div class="card">
<div class="hdr"><div class="dots"><div class="d r"></div><div class="d y"></div><div class="d g"></div></div><span class="t">pr-roast-mcp</span><span class="b">{pr_ref}</span></div>
<div class="body">{content}</div>
<div class="ft">github.com/anisha-agarwal/pr-roast-mcp</div>
</div></body></html>"""


ROASTS = {
    "pr89": {
        "title": "Initiative Bonus",
        "pr_ref": "PR #89",
        "severity": "🔥🔥🔥",
    },
    "pr81": {
        "title": "AI Chat",
        "pr_ref": "PR #81",
        "severity": "🔥🔥🔥🔥",
    },
    "pr84": {
        "title": "Push Subscribe",
        "pr_ref": "PR #84",
        "severity": "🔥🔥🔥",
    },
    "pr87": {
        "title": "Streak Notifications",
        "pr_ref": "PR #87",
        "severity": "🔥🔥🔥",
    },
    "pr90": {
        "title": "Keep Alive Fix",
        "pr_ref": "PR #90",
        "severity": "🔥🔥",
    },
}


if __name__ == "__main__":
    for name in ROASTS:
        md_file = os.path.join(EXAMPLES_DIR, f"{name}.md")
        if not os.path.exists(md_file):
            print(f"  Skip {name} (no .md file)")
            continue

        info = ROASTS[name]
        content = open(md_file).read()
        html = md_to_html_card(info["title"], info["pr_ref"], content)

        html_file = os.path.join(EXAMPLES_DIR, f"{name}.html")
        open(html_file, "w").write(html)

        png_file = os.path.join(EXAMPLES_DIR, f"{name}.png")
        subprocess.run([
            CHROME, "--headless", "--disable-gpu",
            "--window-size=1200,2000",
            "--force-device-scale-factor=2",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=3000",
            f"--screenshot={png_file}",
            f"file://{html_file}",
        ], capture_output=True)

        if os.path.exists(png_file):
            size = os.path.getsize(png_file) // 1024
            print(f"  OK {name}.png ({size}KB)")
        else:
            print(f"  FAILED {name}")

        os.remove(html_file)
