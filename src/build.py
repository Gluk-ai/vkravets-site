"""Builds vkravets.com: /index.html (EN), /ua/index.html, /ru/index.html from src/.

    python3 src/build.py            # writes into the repo root
    python3 src/build.py OUT_DIR    # writes elsewhere (previews)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else ROOT
sys.path.insert(0, HERE)
from content import LANGS  # noqa: E402

SITE = "https://vkravets.com"
SERIF = os.environ.get("SERIF", "lora")  # one serif with Cyrillic, so every language looks the same
SERIF_NAME = {"lora": "Lora", "literata": "Literata", "alegreya": "Alegreya", "source-serif-4": "Source Serif 4"}[SERIF]

LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
CYR = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"
FONTS = [  # family, file stem, weight
    (SERIF_NAME, SERIF, 400), (SERIF_NAME, SERIF, 600),
    ("Inter Tight", "inter-tight", 400), ("Inter Tight", "inter-tight", 500),
    ("JetBrains Mono", "jetbrains-mono", 500),
    ("Caveat", "caveat", 500), ("Caveat", "caveat", 600),
]
CERTS = [
    ("Claude Code 101", "Anthropic", "https://verify.skilljar.com/c/a3wdvseo9pcv"),
    ("Claude Platform 101", "Anthropic", "https://verify.skilljar.com/c/pc8kwwha6gfr"),
    ("Introduction to Subagents", "Anthropic", "https://verify.skilljar.com/c/hgdqv9u9etd4"),
    ("Introduction to Agent Skills", "Anthropic", "https://verify.skilljar.com/c/af3nckzghptv"),
    ("AI Capabilities and Limitations", "Anthropic", "https://academy.claude.com/verify/7a9643520fec5370d7a3ebd395fb4665"),
    ("Software Testing", "SkillUp · 2023", None),
]


def font_faces():
    out = []
    for fam, stem, w in FONTS:
        for sub, rng in (("latin", LATIN), ("cyrillic", CYR)):
            out.append(f'@font-face{{font-family:"{fam}";font-weight:{w};font-display:swap;'
                       f'src:url(/fonts/{stem}-{sub}-{w}-normal.woff2) format("woff2");unicode-range:{rng}}}')
    return "\n".join(out)


def esc_attr(s):
    return s.replace("&amp;", "&").replace("&", "&amp;").replace('"', "&quot;")


def lang_select(c):
    items = "".join(
        f'<li><a class="lang-item" href="{l["path"]}" hreflang="{l["lang"]}" lang="{l["lang"]}"'
        f'{" aria-current=\"true\"" if l is c else ""}><span class="lang-code">{l["label"]}</span>'
        f'<span>{l["name_native"]}</span>{"<svg class=\"lang-check\" viewBox=\"0 0 16 16\" aria-hidden=\"true\"><path d=\"M3 8.5l3 3 7-7\"/></svg>" if l is c else ""}</a></li>'
        for l in LANGS)
    return (f'<div class="lang"><button class="lang-btn" type="button" aria-haspopup="true" aria-expanded="false" '
            f'aria-controls="lang-menu" aria-label="{c["lang_word"]}: {c["name_native"]}">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9s1.3-6.4 3.9-9z"/></svg>'
            f'<span>{c["label"]}</span><svg class="lang-chev" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4"/></svg></button>'
            f'<ul class="lang-menu" id="lang-menu" hidden>{items}</ul></div>')


def page(c):
    nav = c["nav"]
    alts = "\n".join(f'<link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}">' for l in LANGS)
    person = {"@context": "https://schema.org", "@type": "Person", "name": "Vasyl Kravets", "alternateName": ["Василь Кравець", "Василий Кравец"],
              "jobTitle": "AI Automation & Web Developer", "url": SITE + "/", "email": "mailto:hello@corepulsedev.com",
              "address": {"@type": "PostalAddress", "addressLocality": "Vaughan", "addressRegion": "ON", "addressCountry": "CA"},
              "sameAs": ["https://www.linkedin.com/in/kravetsCP", "https://corepulsedev.com"], "knowsLanguage": ["en", "uk", "ru"]}
    preload_sub = "cyrillic" if c["lang"] != "en" else "latin"
    preloads = "\n".join(f'<link rel="preload" href="/fonts/{s}-{preload_sub}-{w}-normal.woff2" as="font" type="font/woff2" crossorigin>'
                         for s, w in ((SERIF, 400), ("caveat", 500), ("inter-tight", 400)))
    sketch = open(os.path.join(HERE, "sketch.svg")).read().replace(
        'aria-label="Pencil sketch of a desk: a monitor with a chat conversation, a keyboard, a wrench and a plant"',
        f'aria-label="{esc_attr(c["sketch_alt"])}"')
    projects = "".join(f'''
        <article class="proj rv">
          <p class="proj-meta"><span>{p["when"]}</span><span>{p["kind"]}</span></p>
          <h3>{p["title"]}</h3>
          <p class="proj-sub">{p["sub"]}</p>
          <p class="d">{p["text"]}</p>
          <ul class="tags">{"".join(f'<li class="tag">{t}</li>' for t in p["tags"])}</ul>
          <a class="proj-link" href="https://{p["url"]}" target="_blank" rel="noopener">{p["url"]} ↗</a>
        </article>''' for p in c["projects"])
    jobs = "".join(f'''
        <li class="job rv"><span class="when">{w}</span><div><h3>{r}</h3><p class="where">{co}</p><p class="d">{d}</p></div></li>'''
                   for w, r, co, d in c["jobs"])
    skills = "".join(f'''
        <div class="skill-group rv"><h4>{g}</h4><ul class="chips">{"".join(f'<li class="chip">{x}</li>' for x in xs)}</ul></div>'''
                     for g, xs in c["skills"])
    certs = "".join(
        (f'<li><a class="cert" href="{u}" target="_blank" rel="noopener">{n} <small>{o}</small></a></li>' if u
         else f'<li><span class="cert">{n} <small>{o}</small></span></li>') for n, o, u in CERTS)
    facts = "".join(f"<p><b>{k}</b>{v}</p>" for k, v in c["facts"])
    css = open(os.path.join(HERE, "style.css")).read().replace("--serif:Fraunces,", f'--serif:"{SERIF_NAME}",')
    js = open(os.path.join(HERE, "main.js")).read()
    return f'''<!doctype html>
<html lang="{c["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{c["title"]}</title>
<meta name="description" content="{esc_attr(c["description"])}">
<meta name="theme-color" content="#f5f1e8">
<link rel="canonical" href="{SITE}{c["path"]}">
{alts}
<link rel="alternate" hreflang="x-default" href="{SITE}/">
<meta property="og:type" content="profile">
<meta property="og:locale" content="{c["locale"]}">
<meta property="og:title" content="{esc_attr(c["title"])}">
<meta property="og:description" content="{esc_attr(c["og_description"])}">
<meta property="og:url" content="{SITE}{c["path"]}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/icon-48.png" type="image/png" sizes="48x48">
<link rel="apple-touch-icon" href="/icon-192.png">
{preloads}
<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
<script>if(!matchMedia("(prefers-reduced-motion: reduce)").matches&&"IntersectionObserver" in window)document.documentElement.classList.add("js")</script>
<style>
{font_faces()}
{css}</style>
</head>
<body>
<header class="top" id="top">
  <div class="wrap top-in">
    <a class="mark" href="#main" aria-label="{c["name"]}">{c["name"]}</a>
    <nav aria-label="Main">
      <a class="hide-sm" href="#work">{nav[0]}</a>
      <a class="hide-sm" href="#experience">{nav[1]}</a>
      <a class="hide-sm" href="#skills">{nav[2]}</a>
      {lang_select(c)}
      <a class="nav-cta" href="#contact">{nav[3]}</a>
    </nav>
  </div>
</header>

<main id="main">
  <section class="hero">
    <div class="wrap hero-in">
      <div>
        <h1>{c["name_lines"][0]}<br>{c["name_lines"][1]}</h1>
        <p class="role">{c["role"]}</p>
        <p class="intro">{c["intro"]}</p>
        <p class="status">{c["status"]}</p>
        <div class="ctas">
          <a class="btn" href="#work">{c["cta_work"]}</a>
          <a class="btn ghost" href="/Vasyl-Kravets-Resume.pdf" download>{c["cta_pdf"]}</a>
        </div>
      </div>

      {sketch.strip()}
    </div>
  </section>

  <section class="sec" id="about" aria-labelledby="about-h">
    <div class="wrap two">
      <h2 class="sec-h rv" id="about-h"><span class="num">01</span>{c["about_h"]}</h2>
      <div class="rv">
        <p class="lead">{c["about"]}</p>
        <div class="facts">{facts}</div>
      </div>
    </div>
  </section>

  <section class="sec" id="work" aria-labelledby="work-h">
    <div class="wrap two">
      <h2 class="sec-h rv" id="work-h"><span class="num">02</span>{c["work_h"]}<span class="note">{c["work_note"]}</span></h2>
      <div class="projs">{projects}
      </div>
    </div>
  </section>

  <section class="sec" id="experience" aria-labelledby="exp-h">
    <div class="wrap two">
      <h2 class="sec-h rv" id="exp-h"><span class="num">03</span>{c["exp_h"]}</h2>
      <ol>{jobs}
      </ol>
    </div>
  </section>

  <section class="sec" id="skills" aria-labelledby="skills-h">
    <div class="wrap two">
      <h2 class="sec-h rv" id="skills-h"><span class="num">04</span>{c["skills_h"]}</h2>
      <div class="skills">{skills}
      </div>
    </div>
  </section>

  <section class="sec" id="certificates" aria-labelledby="cert-h">
    <div class="wrap two">
      <h2 class="sec-h rv" id="cert-h"><span class="num">05</span>{c["cert_h"]}</h2>
      <div class="rv">
        <ul class="certs">{certs}</ul>
        <p class="edu"><b>{c["edu_degree"]}</b><span class="edu-note">{c["edu_note"]}</span>{c["edu_school"]}</p>
      </div>
    </div>
  </section>
</main>

<footer class="foot" id="contact">
  <div class="wrap">
    <p class="signature rv" aria-hidden="true">{c["name"]}</p>
    <h2 class="foot-h rv">{c["talk_h"]}</h2>
    <p class="foot-p rv">{c["talk_p"]}</p>
    <div class="ctas rv">
      <a class="btn" href="mailto:hello@corepulsedev.com">hello@corepulsedev.com</a>
      <a class="btn ghost" href="https://www.linkedin.com/in/kravetsCP" target="_blank" rel="noopener">LinkedIn ↗</a>
      <a class="btn ghost" href="/Vasyl-Kravets-Resume.pdf" download>{c["pdf_short"]}</a>
    </div>
    <p class="copy">{c["copy"]}</p>
  </div>
</footer>

<script>
{js}</script>
</body>
</html>
'''


for c in LANGS:
    d = os.path.join(OUT, c["path"].strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w") as f:
        f.write(page(c))
with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
    urls = "".join(f'<url><loc>{SITE}{c["path"]}</loc><lastmod>2026-11-02</lastmod>'
                   + "".join(f'<xhtml:link rel="alternate" hreflang="{l["lang"]}" href="{SITE}{l["path"]}"/>' for l in LANGS)
                   + "</url>" for c in LANGS)
    f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n')
print("built", [c["path"] for c in LANGS], "serif:", SERIF_NAME, "->", OUT)
