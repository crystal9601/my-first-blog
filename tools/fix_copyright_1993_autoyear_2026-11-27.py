# fix_copyright_1993_autoyear_2026-11-27.py
# Purpose: change every "(c) 2026" copyright in the hosted pages (xoc37cw/*.html)
# to "(c) 1993-[year]".
#  - Visible page text (HTML outside <script> and comments): 1993&ndash;<span class="ccyr">2026</span>,
#    and a small script at the end of the page fills in the current year, so it updates itself.
#  - PDF / print text built in JavaScript: typed "1993-2026" (PDFs keep their publication year).
#    Files whose PDF code maps the en dash use an en dash; the others use a plain hyphen so the PDF never breaks.
#  - Comments and meta tags: typed 1993-2026 (no script can run there).
# Written Nov 27, 2026 by Claudette for Crystal Clear Endeavors LLC dba Crystal Clear Tax.
# (c) 1993-2026 Crystal Clear Endeavors LLC dba Crystal Clear Tax. All rights reserved.
import re, sys, glob, os

YEAR_SCRIPT = ('<script>/* auto copyright year */(function(){var y=new Date().getFullYear();'
               'document.querySelectorAll(".ccyr").forEach(function(e){e.textContent=y;});})();</script>')

def fix_html_text(seg):
    # seg is plain HTML markup (no script, no comment)
    def tag_aware(s):
        out, i = [], 0
        for m in re.finditer(r'<[^>]*>', s):
            out.append(sub_text(s[i:m.start()]))
            out.append(sub_attr(m.group(0)))
            i = m.end()
        out.append(sub_text(s[i:]))
        return ''.join(out)
    def sub_text(t):
        return re.sub(r'(©|&copy;)(\s|&nbsp;)?2026', lambda m: m.group(1)+' 1993&ndash;<span class="ccyr">2026</span>', t)
    def sub_attr(t):
        return re.sub(r'(©|&copy;)(\s|&nbsp;)?2026', lambda m: m.group(1)+' 1993–2026', t)
    return tag_aware(seg)

def fix_js(seg, dash):
    seg = re.sub(r'(©|\\xa9|\\u00a9)\\x202026', lambda m: m.group(1)+'\\x201993'+dash+'2026', seg)
    seg = re.sub(r'(©|&copy;|\\xa9|\\u00a9)(\s|&nbsp;)?2026', lambda m: m.group(1)+' 1993'+dash+'2026', seg)
    return seg

def process(path):
    t = open(path, encoding='utf-8').read()
    has_map = ("'©':0xa9" in t or '"©": 169' in t)
    map_dash = ("'–':" in t or '"–":' in t or "'\\u2013':" in t)
    js_dash = ('\\u2013' if (has_map and map_dash) else '-') if has_map else '\\u2013'
    if has_map and not map_dash:
        js_dash = '-'
    parts = re.split(r'(<script\b[^>]*>.*?</script>|<!--.*?-->)', t, flags=re.S)
    out = []
    for p in parts:
        if p.startswith('<script'):
            out.append(fix_js(p, js_dash))
        elif p.startswith('<!--'):
            out.append(re.sub(r'(©|&copy;)(\s|&nbsp;)?2026', lambda m: m.group(1)+' 1993–2026', p))
        else:
            out.append(fix_html_text(p))
    n = ''.join(out)
    if 'class="ccyr"' in n and 'auto copyright year' not in n:
        if '</body>' in n:
            i = n.rfind('</body>'); n = n[:i] + YEAR_SCRIPT + n[i:]
        else:
            n = n + YEAR_SCRIPT
    left = len(re.findall(r'(©|&copy;|\\xa9)(\s|\\x20|&nbsp;)?2026', n))
    if n != t:
        open(path, 'w', encoding='utf-8').write(n)
    return left, n.count('ccyr')

if __name__ == '__main__':
    folder = sys.argv[1]
    for f in sorted(glob.glob(os.path.join(folder, '*.html'))):
        left, spans = process(f)
        print(os.path.basename(f), 'remaining_2026=', left, 'auto_spans=', spans)
