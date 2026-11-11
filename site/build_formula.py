"""Build the formula mockup page: inline the map shapes and the latest data snapshot.
Usage: python site/build_formula.py MAP_JSON  (writes site/formula.html and dist/WSFI_Formula_Mockup.html)"""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
mp = json.load(open(sys.argv[1]))
snap = json.load(open(root / "site/data/mockup_inputs.json"))
t = (root / "site/formula.template.html").read_text()
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = t.replace("/*__MAP__*/null", js(mp)).replace("/*__SNAP__*/null", js(snap))
(root / "site/formula.html").write_text(page)
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>\n'
       '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
(root / "dist").mkdir(exist_ok=True)
(root / "dist/WSFI_Formula_Mockup.html").write_text(doc)
print(len(page), "bytes")
