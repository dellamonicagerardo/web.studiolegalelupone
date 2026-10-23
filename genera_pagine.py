# -*- coding: utf-8 -*-
"""Crea le pagine delle notizie, l'elenco e la sitemap a partire da articoli.json."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://studiolegalelupone.it"
MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]


def esc(value):
    return html.escape(value or "", quote=True)


def data_it(iso):
    parts = str(iso or "").split("-")
    if len(parts) != 3:
        return esc(iso)
    giorno = int(parts[2])
    mese = MESI[int(parts[1]) - 1]
    return "%d %s %s" % (giorno, mese, parts[0])


def paragrafi(testo):
    blocchi = [b.strip() for b in re.split(r"\n\s*\n", testo or "") if b.strip()]
    return "\n".join("<p>%s</p>" % esc(b).replace("\n", "<br>") for b in blocchi)


def nav(prefix, current):
    voci = [
        ("studio.html", "Lo studio", "studio"),
        ("aree.html", "Aree", "aree"),
        ("professionisti.html", "Professionisti", "professionisti"),
        ("notizie.html", "Notizie", "notizie"),
    ]
    links = []
    for href, label, key in voci:
        stato = ' aria-current="page"' if key == current else ""
        links.append('<li><a href="%s%s"%s>%s</a></li>' % (prefix, href, stato, label))
    return """
      <a class="logo" href="%sindex.html"><img src="%sassets/logo.png" alt="Studio Legale Lupone"></a>
      <ul class="nav-links" id="menu">
        %s
      </ul>
      <a class="btn" href="%scontatti.html">Contatti</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Apri il menu"><span></span></button>
    """ % (prefix, prefix, "\n        ".join(links), prefix)


def footer(prefix, current):
    voci = [
        ("studio.html", "Lo studio", "studio"),
        ("aree.html", "Aree", "aree"),
        ("professionisti.html", "Professionisti", "professionisti"),
        ("notizie.html", "Notizie", "notizie"),
        ("contatti.html", "Contatti", "contatti"),
        ("privacy.html", "Privacy", "privacy"),
    ]
    links = []
    for href, label, key in voci:
        stato = ' aria-current="page"' if key == current else ""
        links.append('<li><a href="%s%s"%s>%s</a></li>' % (prefix, href, stato, label))
    return """
  <footer class="footer">
    <div class="footer-grid">
      <div>
        <h2>Studio Legale Lupone</h2>
        <p>Assistenza legale a Mercato San Severino e Castel San Giorgio. Si riceve previo appuntamento.</p>
      </div>
      <div>
        <h2>Contatti</h2>
        <ul>
          <li><a href="tel:+39089826253">089 826253</a></li>
          <li><a href="https://wa.me/393206160597" target="_blank" rel="noopener">WhatsApp 320 6160597</a></li>
        </ul>
      </div>
      <div>
        <h2>Sedi</h2>
        <ul>
          <li>Via Ten. Francesco Falco 20/1, Mercato San Severino</li>
          <li>Via Luigi Guerrasio 72, Castel San Giorgio</li>
        </ul>
      </div>
      <div>
        <h2>Pagine</h2>
        <ul>
          %s
        </ul>
      </div>
    </div>
    <div class="legal">
      <span>Studio Legale Lupone © 2026</span>
      <a href="%sprivacy.html">Privacy</a>
    </div>
  </footer>
    """ % ("\n          ".join(links), prefix)


def dock(prefix):
    luigi = "https://wa.me/393206160597?text=Buongiorno%2C%20vorrei%20un%20appuntamento%20con%20l%27avv.%20Luigi%20Lupone."
    giuseppe = "https://wa.me/393206160597?text=Buongiorno%2C%20vorrei%20un%20appuntamento%20con%20l%27avv.%20Giuseppe%20Lupone."
    return """
  <aside class="dock" id="dock" aria-label="Contatto rapido" inert>
    <a class="dock-person" href="%s" target="_blank" rel="noopener">
      <img src="%sassets/luigi.jpg" alt="">
      <strong>Luigi Lupone</strong>
      <small>Civile</small>
      <span class="dock-cta">Contatti</span>
    </a>
    <a class="dock-person" href="%s" target="_blank" rel="noopener">
      <img src="%sassets/giuseppe.jpg" alt="">
      <strong>Giuseppe Lupone</strong>
      <small>Penale</small>
      <span class="dock-cta">Contatti</span>
    </a>
  </aside>""" % (luigi, prefix, giuseppe, prefix)


def meta(title, description, path, image):
    url = SITE + path
    return """
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>%s</title>
  <meta name="description" content="%s">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="%s">
  <meta property="og:locale" content="it_IT">
  <meta property="og:site_name" content="Studio Legale Lupone">
  <meta property="og:title" content="%s">
  <meta property="og:description" content="%s">
  <meta property="og:url" content="%s">
  <meta property="og:image" content="%s">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#f3f4f2">
    """ % (esc(title), esc(description), url, esc(title), esc(description), url, esc(image))


def scheda(item, prefix):
    href = prefix + "notizie/" + item["slug"] + ".html"
    immagine = ""
    if item.get("immagine"):
        immagine = '<img src="%s%s" alt="">' % (prefix, esc(item["immagine"]))
    return (
        '<li><a href="%s">%s<div class="news-body"><p class="news-meta">%s · %s</p><h3>%s</h3><p>%s</p>'
        '<span class="news-more">Leggi l\'articolo</span></div></a></li>'
        % (href, immagine, esc(item["categoria"]), data_it(item["data"]), esc(item["titolo"]), esc(item["descrizione"]))
    )


def pagina_articolo(item):
    path = "/notizie/" + item["slug"] + ".html"
    image = SITE + "/" + item["immagine"] if item.get("immagine") else SITE + "/assets/studio-panorama.jpg"
    title = item["titolo"] + " | Studio Legale Lupone"
    cover = ""
    if item.get("immagine"):
        cover = '<img class="article-cover" src="../%s" alt="%s">' % (esc(item["immagine"]), esc(item["titolo"]))
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Notizie", "item": SITE + "/notizie.html"},
            {"@type": "ListItem", "position": 3, "name": item["titolo"], "item": SITE + path},
        ],
    }
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item["titolo"],
        "description": item["descrizione"],
        "datePublished": item["data"],
        "dateModified": item["data"],
        "inLanguage": "it-IT",
        "mainEntityOfPage": SITE + path,
        "image": image,
        "author": {"@type": "Organization", "name": "Studio Legale Lupone", "url": SITE + "/"},
        "publisher": {
            "@type": "Organization",
            "name": "Studio Legale Lupone",
            "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png"},
        },
    }
    return """<!DOCTYPE html>
<html lang="it">
<head>
%s
  <meta property="og:type" content="article">
  <link rel="icon" href="../assets/favicon.png" type="image/png">
  <link rel="stylesheet" href="../css/styles.css">
  <script type="application/ld+json">
  %s
  </script>
  <script type="application/ld+json">
  %s
  </script>
</head>
<body>
  <a class="skip" href="#contenuto">Vai al contenuto</a>
  <header class="topbar">
    <nav class="nav" aria-label="Principale">%s
    </nav>
  </header>
  <main class="page article" id="contenuto">
    <nav class="crumbs" aria-label="Percorso"><a href="../index.html">Home</a><span aria-hidden="true">/</span><a href="../notizie.html">Notizie</a><span aria-hidden="true">/</span><span>%s</span></nav>
    <article>
      %s
      <p class="news-meta">%s · <time datetime="%s">%s</time></p>
      <h1>%s</h1>
      <p class="lead">%s</p>
      %s
      <p><a class="btn" href="../contatti.html">Scrivi allo studio</a></p>
    </article>
  </main>
%s
%s
  <script src="../js/main.js"></script>
</body>
</html>
""" % (
        meta(title, item["descrizione"], path, image),
        json.dumps(crumbs, ensure_ascii=False),
        json.dumps(article, ensure_ascii=False),
        nav("../", ""),
        esc(item["titolo"]),
        cover,
        esc(item["categoria"]),
        esc(item["data"]),
        data_it(item["data"]),
        esc(item["titolo"]),
        esc(item["descrizione"]),
        paragrafi(item.get("testo") or ""),
        footer("../", ""),
        dock("../"),
    )


def pagina_notizie(articoli):
    title = "Notizie | Studio Legale Lupone"
    description = "Note dello Studio Legale Lupone su pronunce e questioni di diritto civile, penale e amministrativo."
    image = SITE + "/assets/studio-panorama.jpg"
    elenco = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": item["titolo"],
                "url": SITE + "/notizie/" + item["slug"] + ".html",
            }
            for i, item in enumerate(articoli)
        ],
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Notizie", "item": SITE + "/notizie.html"},
        ],
    }
    cards = "\n        ".join(scheda(item, "") for item in articoli)
    return """<!DOCTYPE html>
<html lang="it">
<head>
%s
  <meta property="og:type" content="website">
  <link rel="icon" href="assets/favicon.png" type="image/png">
  <link rel="stylesheet" href="css/styles.css">
  <script type="application/ld+json">
  %s
  </script>
  <script type="application/ld+json">
  %s
  </script>
</head>
<body>
  <a class="skip" href="#contenuto">Vai al contenuto</a>
  <header class="topbar">
    <nav class="nav" aria-label="Principale">%s
    </nav>
  </header>
  <main class="page page-wide" id="contenuto">
    <nav class="crumbs" aria-label="Percorso"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>Notizie</span></nav>
    <p class="eyebrow">Notizie</p>
    <h1>Note già pubblicate dallo studio.</h1>
    <p>Note su pronunce e questioni già trattate dallo studio.</p>
    <ul class="news">
        %s
    </ul>
  </main>
%s
%s
  <script src="js/main.js"></script>
</body>
</html>
""" % (
        meta(title, description, "/notizie.html", image),
        json.dumps(crumbs, ensure_ascii=False),
        json.dumps(elenco, ensure_ascii=False),
        nav("", "notizie"),
        cards,
        footer("", "notizie"),
        dock(""),
    )


def sitemap(articoli):
    pagine = [
        ("/", "2026-10-23"),
        ("/studio.html", "2026-10-23"),
        ("/aree.html", "2026-10-23"),
        ("/professionisti.html", "2026-10-23"),
        ("/contatti.html", "2026-10-23"),
        ("/notizie.html", "2026-10-23"),
        ("/privacy.html", "2026-10-23"),
    ]
    for item in articoli:
        pagine.append(("/notizie/" + item["slug"] + ".html", item["data"]))
    body = "\n".join(
        "  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>" % (SITE, path, lastmod)
        for path, lastmod in pagine
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body
        + "\n</urlset>\n"
    )


def main():
    catalogo = json.loads((ROOT / "articoli.json").read_text(encoding="utf-8"))
    articoli = [item for item in catalogo["articoli"] if str(item.get("testo") or "").strip() and item.get("slug")]
    cartella = ROOT / "notizie"
    cartella.mkdir(exist_ok=True)
    attesi = set()
    for item in articoli:
        nome = item["slug"] + ".html"
        attesi.add(nome)
        (cartella / nome).write_text(pagina_articolo(item), encoding="utf-8")
    for vecchia in cartella.glob("*.html"):
        if vecchia.name not in attesi:
            vecchia.unlink()
    (ROOT / "notizie.html").write_text(pagina_notizie(articoli), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(articoli), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE,
        encoding="utf-8",
    )
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    inizio = "<!-- pagine-notizie -->"
    fine = "<!-- /pagine-notizie -->"
    if inizio not in index or fine not in index:
        raise SystemExit("Marcatori delle notizie assenti in index.html")
    blocco = inizio + "\n        " + "\n        ".join(scheda(item, "") for item in articoli) + "\n        " + fine
    index = index[: index.index(inizio)] + blocco + index[index.index(fine) + len(fine) :]
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    print("pagine", len(articoli))


if __name__ == "__main__":
    main()
