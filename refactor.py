#!/usr/bin/env python3
# refactor.py — factorise le CSS, passe en immersif, prépare le build.
# Lit raw/, écrit dist/. Ne modifie jamais raw/.

import re, pathlib, shutil, html

SRC = pathlib.Path("raw")
OUT = pathlib.Path("dist")
ENTRY_OLD = "Sommaire_prototype.html"
ENTRY_NEW = "index.html"

def read(p):  return p.read_text(encoding="utf-8")
def write(p, s): p.write_text(s, encoding="utf-8")

# --- 1. Reset du dossier de sortie ---
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

files = sorted(p for p in SRC.glob("*.html"))
if not files:
    raise SystemExit("Aucun .html dans raw/. Vérifie le dossier.")

# --- 2. Extraction des règles CSS de chaque fichier ---
# On découpe chaque bloc <style> en règles individuelles "sélecteur { corps }".
rule_re = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)

def extract_style(doc):
    m = re.search(r"<style>(.*?)</style>", doc, re.S)
    return (m.group(1), m.span()) if m else ("", None)

def rules_of(css):
    # renvoie liste de (selecteur_normalise, regle_brute)
    out = []
    for m in rule_re.finditer(css):
        sel = " ".join(m.group(1).split())
        body = m.group(2).strip()
        raw = f"{sel}{{{body}}}"
        out.append((sel + "||" + body, raw))
    return out

per_file = {}
counts = {}
for p in files:
    doc = read(p)
    css, span = extract_style(doc)
    rules = rules_of(css)
    per_file[p.name] = {"doc": doc, "css": css, "span": span, "rules": rules}
    for key, _ in rules:
        counts[key] = counts.get(key, 0) + 1

N = len(files)
# règle "commune" = présente à l'identique dans TOUS les fichiers
common_keys = {k for k, c in counts.items() if c == N}

# --- 3. Construction de app.css : tronc commun + responsive ---
common_rules = []
seen = set()
# on garde l'ordre du premier fichier pour la lisibilité
for key, raw in per_file[files[0].name]["rules"]:
    if key in common_keys and key not in seen:
        common_rules.append(raw)
        seen.add(key)

RESPONSIVE = """
/* ---- Responsive : immersif sur mobile ---- */
@media (max-width: 600px){
  body{padding:0 !important;background:#000 !important;
       align-items:stretch !important;min-height:100dvh !important;}
  .wrap{gap:0 !important;width:100% !important;}
  .phone{width:100vw !important;height:100dvh !important;border-radius:0 !important;
         padding:0 !important;box-shadow:none !important;background:#000 !important;}
  .screen{border-radius:0 !important;height:100dvh !important;}
  .island{display:none !important;}
  .caption{display:none !important;}
}
"""

app_css = "/* app.css — DA commune du prototype Mo (généré) */\n\n" \
          + "\n".join(common_rules) + "\n" + RESPONSIVE
write(OUT / "app.css", app_css)

# --- 4. Réécriture de chaque fichier ---
def strip_caption(doc):
    # retire <div class="caption">...</div> (immersif)
    return re.sub(r'\s*<div class="caption">.*?</div>', "", doc, flags=re.S)

def rewrite(p):
    info = per_file[p.name]
    doc = info["doc"]
    css = info["css"]
    span = info["span"]
    if span is None:
        return doc  # pas de style, on laisse tel quel

    # règles spécifiques = celles non communes
    specific = [raw for key, raw in info["rules"] if key not in common_keys]
    link = '<link rel="stylesheet" href="app.css">'
    if specific:
        block = link + "\n<style>\n" + "\n".join(specific) + "\n</style>"
    else:
        block = link

    # remplace le <style>...</style> d'origine par le lien + styles propres
    start, end = span
    style_open = doc.rfind("<style>", 0, start + 7)
    doc = doc[:style_open] + block + doc[doc.find("</style>", start) + len("</style>"):]

    doc = strip_caption(doc)
    # réécrit les liens vers l'ancien point d'entrée
    doc = doc.replace(ENTRY_OLD, ENTRY_NEW)
    return doc

for p in files:
    out_doc = rewrite(p)
    name = ENTRY_NEW if p.name == ENTRY_OLD else p.name
    write(OUT / name, out_doc)

# --- 5. Rapport ---
print(f"OK  {N} fichiers traités")
print(f"    {len(common_rules)} règles communes -> dist/app.css")
print(f"    point d'entree : dist/{ENTRY_NEW}")
print(f"    ouvre pour verifier : open dist/{ENTRY_NEW}")