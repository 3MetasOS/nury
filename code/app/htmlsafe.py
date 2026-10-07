"""Keep only plain document markup in HTML that came from Markdown we do not fully control (the build log).

python-markdown passes raw HTML through. An entry in BUILD_LOG.md with a script tag, an event attribute or a javascript:
link would run in a reader's browser. This keeps a short list of tags and attributes and drops everything else: the
tag is removed, text inside it stays (inside script, style and similar, it is dropped too). Standard library only."""
import html
import re
from html.parser import HTMLParser

ALLOWED = {"p", "br", "hr", "ul", "ol", "li", "strong", "em", "b", "i", "code", "pre", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6",
           "table", "thead", "tbody", "tr", "th", "td", "a", "details", "summary", "del", "sup", "sub"}
VOID = {"br", "hr"}
DROP_WITH_CONTENT = {"script", "style", "iframe", "object", "embed", "template", "noscript", "svg", "math", "textarea", "title", "head"}
SAFE_HREF = re.compile(r"^(https?://|mailto:|#|/|\./|\.\./)[^\s]*$", re.I)
SAFE_CLASS = re.compile(r"^[A-Za-z0-9_\- ]{1,60}$")
SAFE_ALIGN = re.compile(r"^text-align:\s*(left|right|center)\s*;?$", re.I)


class _Clean(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in DROP_WITH_CONTENT:
            self.skip += 1
            return
        if self.skip:
            return
        if tag not in ALLOWED:            # an unknown tag is shown as text, so '<question>' stays readable and nothing runs
            self.out.append(html.escape(self.get_starttag_text() or "", quote=False))
            return
        keep = []
        for k, v in attrs:
            v = v or ""
            if tag == "a" and k == "href" and SAFE_HREF.match(v.strip()):
                keep.append(("href", v.strip()))
            elif tag == "a" and k == "title":
                keep.append(("title", v))
            elif tag == "code" and k == "class" and SAFE_CLASS.match(v):
                keep.append(("class", v))
            elif tag in ("th", "td") and k == "style" and SAFE_ALIGN.match(v.strip()):
                keep.append(("style", v.strip()))
            elif tag in ("th", "td") and k == "align" and v in ("left", "right", "center"):
                keep.append(("align", v))
        if tag == "a" and any(k == "href" for k, _ in keep):
            keep.append(("rel", "noopener noreferrer"))
        attr = "".join(f' {k}="{html.escape(v, quote=True)}"' for k, v in keep)
        self.out.append(f"<{tag}{attr}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in DROP_WITH_CONTENT:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in ALLOWED:
            if tag not in VOID:
                self.out.append(f"</{tag}>")
        else:
            self.out.append(html.escape(f"</{tag}>", quote=False))

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))

    def handle_entityref(self, name):
        if not self.skip:
            self.out.append(f"&{name};")

    def handle_charref(self, name):
        if not self.skip:
            self.out.append(f"&#{name};")


def clean(markup):
    p = _Clean()
    p.feed(markup or "")
    p.close()
    return "".join(p.out)
