#!/usr/bin/env python3
"""md2docx — minimal Markdown -> .docx (Word) with zero external deps.

Why it exists: the sdlc **TW** role's deliverable is a .docx (Word) document,
but environments often lack pandoc / python-docx / LibreOffice. This builds a
*valid* OOXML .docx from a Markdown subset using only the Python standard
library (zipfile + string OOXML), so the TW role can always emit .docx.

Scope (deliberately small — TW docs are prose, not layout): supports `# / ## /
###` headings, paragraphs, `- ` / `* ` bullets, and `**bold**` inline. For
richer documents prefer pandoc (`pandoc in.md -o out.docx`) or python-docx; this
is the no-install fallback.

Usage:  python3 md2docx.py INPUT.md OUTPUT.docx
        python3 md2docx.py - OUTPUT.docx   # read Markdown from stdin
"""
from __future__ import annotations

import sys
import re
import zipfile


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def runs(text: str) -> str:
    """Inline **bold** -> OOXML runs; everything else plain."""
    out = []
    for i, chunk in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if chunk == "":
            continue
        bold = i % 2 == 1  # odd indices are the captured **bold** groups
        rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{xml_escape(chunk)}</w:t></w:r>')
    return "".join(out) or '<w:r><w:t xml:space="preserve"></w:t></w:r>'


def para(text: str, *, size: int | None = None, bold: bool = False, bullet: bool = False) -> str:
    ppr = []
    if bullet:
        ppr.append('<w:ind w:left="360" w:hanging="360"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    if size or bold:
        rpr = "<w:rPr>" + ("<w:b/>" if bold else "") + (f'<w:sz w:val="{size}"/>' if size else "") + "</w:rPr>"
        body = f'<w:r>{rpr}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
    else:
        body = runs(text)
    if bullet:
        body = '<w:r><w:t xml:space="preserve">• </w:t></w:r>' + body
    return f"<w:p>{ppr_xml}{body}</w:p>"


def md_to_body(md: str) -> str:
    paras = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("### "):
            paras.append(para(line[4:], size=26, bold=True))
        elif line.startswith("## "):
            paras.append(para(line[3:], size=30, bold=True))
        elif line.startswith("# "):
            paras.append(para(line[2:], size=36, bold=True))
        elif line.lstrip().startswith(("- ", "* ")):
            paras.append(para(line.lstrip()[2:], bullet=True))
        else:
            paras.append(para(line))
    return "".join(paras)


CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    "</Types>"
)
RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    "</Relationships>"
)


def build_docx(md: str, out_path: str) -> None:
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{md_to_body(md)}<w:sectPr/></w:body></w:document>"
    )
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", document)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, out = sys.argv[1], sys.argv[2]
    md = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    build_docx(md, out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
