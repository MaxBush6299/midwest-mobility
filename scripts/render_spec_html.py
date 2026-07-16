"""Render the implementation design spec to a self-contained HTML file."""
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "internal" / "specs" / "2026-06-16-mmc-agent-network-implementation-design.md"
OUT = ROOT / "docs" / "internal" / "specs" / "2026-06-16-mmc-agent-network-implementation-design.html"

CSS = """
:root {
  --bg:#f6f3ec; --panel:#fbf9f4; --ink:#22201c; --soft:#5a544a; --line:#d8cfbf;
  --blue:#2f6db5; --teal:#2b8a86; --plum:#7a4f9e; --rose:#b05568; --code-bg:#efe9df;
}
* { box-sizing:border-box; }
html,body { background:var(--bg); margin:0; }
body {
  font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;
  color:var(--ink); line-height:1.55; font-size:15px;
}
.wrap {
  max-width:980px; margin:32px auto; background:var(--panel);
  border:1px solid var(--line); border-radius:14px;
  box-shadow:0 2px 4px rgba(40,34,24,.05),0 10px 28px rgba(40,34,24,.08);
  padding:48px 56px;
}
h1 { font-size:30px; color:var(--blue); margin:0 0 6px; letter-spacing:-.3px; }
h2 {
  font-size:21px; margin:32px 0 10px; color:var(--ink);
  border-bottom:1px solid var(--line); padding-bottom:6px;
}
h3 { font-size:17px; margin:22px 0 8px; color:var(--plum); }
p { margin:8px 0 12px; }
ul,ol { margin:8px 0 12px; padding-left:24px; }
li { margin:4px 0; }
strong { color:var(--ink); }
a { color:var(--blue); }
hr { border:none; border-top:1px solid var(--line); margin:28px 0; }
blockquote {
  border-left:4px solid var(--teal); background:#eef5f4;
  margin:12px 0; padding:10px 16px; color:var(--soft);
}
code {
  font-family:'Cascadia Code',Consolas,monospace; font-size:13px;
  background:var(--code-bg); padding:1px 5px; border-radius:4px;
  border:1px solid var(--line);
}
pre {
  background:#2b2a28; color:#f0ebe0; padding:16px 18px; border-radius:10px;
  overflow-x:auto; font-size:13px; line-height:1.45;
}
pre code { background:transparent; border:none; padding:0; color:inherit; }
table {
  border-collapse:collapse; width:100%; margin:14px 0; font-size:14px;
  background:#fff; border:1px solid var(--line); border-radius:8px; overflow:hidden;
}
th,td { border-bottom:1px solid var(--line); padding:9px 12px; text-align:left; vertical-align:top; }
th { background:#ece4d3; color:var(--ink); font-weight:700; font-size:13px;
     text-transform:uppercase; letter-spacing:.5px; }
tr:last-child td { border-bottom:none; }
tr:nth-child(even) td { background:#faf7ee; }
"""

def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MMC Reusable Agent Network &mdash; Implementation Design</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
