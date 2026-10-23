#!/usr/bin/env python3
"""Builds YousefTube's standalone pages from tools/content.py. Run from the repo root: python3 tools/build.py"""
import os, re, sys, json, datetime
sys.path.insert(0, os.path.dirname(__file__))
from content import NAMES, HALL, FACTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://youseftube.com"
TODAY = datetime.date.today().isoformat()

# Shared stylesheet: the homepage's own CSS plus subpage additions.
home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
base_css = home[home.index("<style>") + 7: home.index("</style>")]
extra_css = """
.page{padding-block:40px 56px}
.crumbs{font-family:var(--mono);font-size:.75rem;color:var(--muted);margin-bottom:14px}
.crumbs a{color:var(--muted)}
.page h1{font-family:var(--display);font-weight:400;font-size:clamp(2.2rem,6vw,3.6rem);line-height:1.02}
.page .tag{font-size:1.15rem;color:var(--muted);margin:10px 0 24px;max-width:60ch}
.prose{max-width:68ch}
.prose h2{font-size:1.5rem;margin:30px 0 8px}
.prose p{margin:0 0 14px}
.callout{background:var(--paper);border:2px solid var(--ink);border-radius:16px;padding:18px 20px;margin:22px 0;box-shadow:5px 5px 0 var(--accent)}
.callout .eyebrow{display:block;margin-bottom:6px}
.twocol{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:36px}
@media (max-width:860px){.twocol{grid-template-columns:1fr}}
.side ul{padding-left:18px;margin:6px 0 0}
.linkgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.linkcard{display:block;text-decoration:none;border:1.5px solid var(--line);border-radius:14px;padding:16px;background:var(--bg)}
.linkcard:hover{border-color:var(--ink)}
.linkcard b{display:block;font-size:1.1rem}
.linkcard small{color:var(--muted)}
.card a.more{font-weight:600;font-size:.9rem}
.hero-mono{width:72px;height:72px;border-radius:50%;display:grid;place-items:center;font-family:var(--display);font-size:2rem;color:#fff;margin-bottom:14px}
"""
os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
open(os.path.join(ROOT, "assets/site.css"), "w", encoding="utf-8").write(base_css + extra_css)

HEADER = """<header>
  <div class="wrap mast">
    <a class="logo" href="/" aria-label="YousefTube home"><img class="logo-img" src="/logo.png" alt="YousefTube.com"></a>
    <nav aria-label="Sections">
      <a href="/news/">Yousefs Winning</a>
      <a href="/hall-of-fame/">Hall of Fame</a>
      <a href="/names/">Name Guide</a>
      <a href="/wall/">The Wall</a>
      <a href="/fun-facts/">Fun Facts</a>
    </nav>
    <a class="btn" href="#newsletter">Subscribe</a>
  </div>
</header>"""
NEWSBAND = """<section class="newsband" id="newsletter"><div class="wrap in">
  <div><div class="eyebrow">The Yousefsletter · every Friday</div><h2>Get the Yousef Report</h2><p class="fine">One email a week: the best Yousef wins, a new Hall of Fame inductee, and some puns. Unsubscribe anytime.</p></div>
  <form class="signup" novalidate data-source="newsband"><input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"><label class="hp" for="nb-email">Email</label><input id="nb-email" type="email" placeholder="you@example.com" autocomplete="email" required><button class="btn" type="submit">Subscribe</button></form>
</div></section>"""
FOOTER = """<footer>
  <div class="wrap cols">
    <div>
      <a class="logo" href="/" aria-label="YousefTube home"><img class="logo-img" src="/logo.png" alt="YousefTube.com"></a>
      <p>YousefTube is a fan site and a work of affectionate satire. Not affiliated with YouTube, Google, or any of the excellent Yousefs mentioned. News summaries link to their original sources.</p>
    </div>
    <div><h4>Explore</h4><ul><li><a href="/news/">Yousefs Winning</a></li><li><a href="/hall-of-fame/">Hall of Fame</a></li><li><a href="/names/">Name Guide</a></li><li><a href="/fun-facts/">Fun Facts</a></li><li><a href="/wall/">The Yousef Wall</a></li></ul></div>
    <div><h4>About</h4><ul><li><a href="/about/">About YousefTube</a></li><li><a href="/contact/">Contact</a></li><li><a href="/privacy.html">Privacy</a></li></ul></div>
  </div>
</footer>"""

def page(path, title, desc, body, extra_head=""):
    canon = SITE + "/" + path.replace("index.html", "")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/logo.png">
<link rel="icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shrikhand&family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&family=Caveat:wght@700&display=swap">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/wall.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3863850520564064" crossorigin="anonymous"></script>
{extra_head}</head>
<body>
{HEADER}
<main class="wrap page">
{body}
</main>
{NEWSBAND}
{FOOTER}
<div class="toast" id="toast" hidden></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)
    return canon

def strip(s): return re.sub(r"<[^>]+>", "", s)
urls = [SITE + "/"]

# ---- Name guide
cards = "".join(f'<a class="linkcard" href="/names/{n["slug"]}/"><b>{n["name"]}</b><small>{n["lang"]}</small></a>' for n in NAMES)
urls.append(page("names/index.html", "The Yousef Name Guide · YousefTube",
  "Every spelling of Yousef, Youssef, Yusuf and Joseph explained: meanings, origins, popularity and famous namesakes.",
  f"""<div class="crumbs"><a href="/">Home</a> / Name Guide</div>
<h1>The Yousef Name Guide</h1>
<p class="tag">One Hebrew name, <i>Yosef</i>, "he will add," travelled to nearly every language on Earth. Here is every branch of the family, with its meaning, history, popularity and best-known bearers.</p>
<div class="linkgrid">{cards}</div>
<div class="callout prose"><span class="eyebrow">Why so many spellings?</span>Two routes did most of the work. Through Greek and Latin, Yosef became Joseph, José, Giuseppe and Josef. Through Arabic, it became Yūsuf, and then Yousef, Youssef, Yusuf, Youcef and Youssouf depending on which alphabet habits a country picked up along the way.</div>
"""))
for i, n in enumerate(NAMES):
    others = [m for m in NAMES if m is not n][:6]
    sections = "".join(f"<h2>{h}</h2><p>{p}</p>" for h, p in n["body"])
    famous = "".join(f"<li>{f}</li>" for f in n["famous"])
    rel = "".join(f'<li><a href="/names/{m["slug"]}/">{m["name"]}</a></li>' for m in others)
    urls.append(page(f"names/{n['slug']}/index.html", f"{n['name']}: Meaning, Origin and Popularity · YousefTube",
      strip(n["meaning"])[:155],
      f"""<div class="crumbs"><a href="/">Home</a> / <a href="/names/">Name Guide</a> / {n['name']}</div>
<div class="eyebrow">{n['lang']}</div>
<h1>{n['name']}</h1>
<p class="tag">{n['tagline']}</p>
<div class="twocol">
  <article class="prose">
    <h2>Meaning</h2><p>{n['meaning']}</p>
    {sections}
    <div class="callout"><span class="eyebrow">Fun fact</span>{n['fun']}</div>
  </article>
  <aside class="side">
    <div class="sponsor"><div class="eyebrow">Famous bearers</div><ul>{famous}</ul></div>
    <div class="sponsor"><div class="eyebrow">More spellings</div><ul>{rel}</ul></div>
  </aside>
</div>"""))

# ---- Hall of Fame
hcards = "".join(f"""<article class="card"><div class="mono" style="background:{h['color']}">{h['mono']}</div><div class="role">{h['role']}</div><h3>{h['name']}</h3><p>{strip(h['paras'][0])[:170]}…</p><a class="more" href="/hall-of-fame/{h['slug']}/">Read the full story →</a><div class="quip">{h['quip']}</div></article>""" for h in HALL)
urls.append(page("hall-of-fame/index.html", "The Yousef Hall of Fame · YousefTube",
  "Famous Yousefs, Youssefs, Yusufs and Yousufs through history: a photographer, a prophet, a World Cup hero, an Olympic meme and more.",
  f"""<div class="crumbs"><a href="/">Home</a> / Hall of Fame</div>
<h1>The Yousef Hall of Fame</h1>
<p class="tag">Inducted for excellence and/or vibes. Three thousand years of Yousefs, abridged.</p>
<div class="hof">{hcards}</div>
"""))
for h in HALL:
    paras = "".join(f"<p>{p}</p>" for p in h["paras"])
    others = "".join(f'<li><a href="/hall-of-fame/{o["slug"]}/">{o["name"]}</a></li>' for o in HALL if o is not h)
    urls.append(page(f"hall-of-fame/{h['slug']}/index.html", f"{h['name']} · Yousef Hall of Fame",
      strip(h["paras"][0])[:155],
      f"""<div class="crumbs"><a href="/">Home</a> / <a href="/hall-of-fame/">Hall of Fame</a> / {h['name']}</div>
<div class="twocol">
  <article class="prose">
    <div class="hero-mono" style="background:{h['color']}">{h['mono']}</div>
    <div class="eyebrow">{h['role']}</div>
    <h1>{h['name']}</h1>
    <p class="tag">{h['quip']}</p>
    {paras}
  </article>
  <aside class="side">
    <div class="sponsor"><div class="eyebrow">More inductees</div><ul>{others}</ul></div>
  </aside>
</div>"""))

# ---- News archive (reads data/news.json in the browser)
urls.append(page("news/index.html", "Yousefs Winning: Good News Archive · YousefTube",
  "A daily archive of good news about people named Yousef, Youssef, Yusuf and every other spelling. Positive stories only, each linked to its source.",
  """<div class="crumbs"><a href="/">Home</a> / Yousefs Winning</div>
<h1>Yousefs Winning</h1>
<p class="tag">Good news about Yousefs of every spelling, gathered daily. Each story links to its original source. Bad news is someone else's beat.</p>
<div class="wire"><div class="stories" id="stories"><p>Loading the latest wins…</p></div>
<div class="side"><div class="sponsor"><div class="eyebrow">Got a Yousef win?</div><p>Send it to tips@youseftube.com and we may feature it.</p></div></div></div>
<p class="fine" id="updated"></p>
<script>
fetch('/data/news.json',{cache:'no-store'}).then(r=>r.json()).then(d=>{
  const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  document.getElementById('stories').innerHTML=d.stories.map(s=>`<article class="story"><div class="w">${esc(s.icon||'W')}</div><div><h3>${esc(s.title)}</h3><p>${esc(s.blurb)}</p><div class="meta"><span>${esc(s.category)}</span><span>${esc(s.date)}</span><a href="${esc(s.url)}" target="_blank" rel="noopener">Source ↗</a></div></div></article>`).join('');
  if(d.updated)document.getElementById('updated').textContent='Last updated '+d.updated;
}).catch(()=>{document.getElementById('stories').innerHTML='<p>The news desk is on a coffee break. Try again shortly.</p>'});
</script>"""))

# ---- Fun facts
facts = "".join(f'<div class="fact"><div class="n">{n}</div><p>{t}</p></div>' for n, t in FACTS)
urls.append(page("fun-facts/index.html", "Fun Yousef Facts · YousefTube",
  "Shareable, verified and mildly smug facts about the name Yousef and its many spellings, from Saint Joseph's Day to Geppetto.",
  f"""<div class="crumbs"><a href="/">Home</a> / Fun Facts</div>
<h1>Fun Yousef Facts</h1>
<p class="tag">Shareable, verified, mildly smug. Perfect for dinner parties attended by at least one Yousef.</p>
<div class="facts">{facts}</div>
"""))


# ---- The Yousef Wall
urls.append(page("wall/index.html", "The Yousef Wall · YousefTube",
  "Check in as a fellow Yousef, send appreciation to a Yousef in your life, or leave a message on the Yousef Wall.",
  """<div class="crumbs"><a href="/">Home</a> / The Yousef Wall</div>
<div class="eyebrow"><span class="wall-count" id="wall-count">0</span> posts and counting</div>
<h1>The Yousef Wall</h1>
<p class="tag">Check in as a fellow Yousef, send love to a Yousef in your life, or just say hi. No account needed. Be kind; this wall is for good vibes only.</p>
<form class="wall-form" id="wall-form" novalidate>
  <span id="post"></span>
  <fieldset class="kinds"><legend>What are you posting?</legend>
    <label><input type="radio" name="kind" value="checkin" checked> 👋 Checking in as a Yousef</label>
    <label><input type="radio" name="kind" value="appreciation"> 💛 Appreciating a Yousef</label>
    <label><input type="radio" name="kind" value="message"> ✉️ Message to a Yousef</label>
  </fieldset>
  <div class="row">
    <label class="f" for="wall-name">Your name<input id="wall-name" type="text" maxlength="40" placeholder="Yousef" autocomplete="given-name"></label>
    <label class="f" for="wall-place">Where you're from (optional)<input id="wall-place" type="text" maxlength="40" placeholder="San Antonio, TX"></label>
  </div>
  <label class="f" for="wall-body">Your message<textarea id="wall-body" maxlength="280" placeholder="Proud Yousef since 1987. Two S's, no regrets."></textarea></label>
  <input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
    <span class="fine" id="wall-chars">0 / 280</span>
    <button class="btn" type="submit">Post to the wall</button>
  </div>
  <p class="fine" style="margin:0">Posts are public. First names only, please, and no links, phone numbers or private details. We remove anything unkind.</p>
</form>
<div class="wall-grid" id="wall-list" data-limit="100">
  <div class="wall-empty">The wall is fresh paint. Be the first Yousef to sign it.</div>
</div>
"""))

# ---- About & Contact
urls.append(page("about/index.html", "About YousefTube",
  "YousefTube is an affectionate, satirical fan site for everyone named Yousef, and everyone who loves one.",
  """<div class="crumbs"><a href="/">Home</a> / About</div>
<article class="prose">
<h1>About YousefTube</h1>
<p class="tag">The internet's #1 source for Yousef content. Also, as far as we can tell, its only one.</p>
<p>YousefTube celebrates one of the oldest and most widely shared names in the world. Yousef, Youssef, Yusuf, Joseph, José, Giuseppe, Josef, Iosif, Hovsep: they all come from the same Hebrew name, Yosef, "he will add." Few names have crossed so many languages, faiths and borders while keeping their meaning intact.</p>
<p>We collect the good stuff: good news about Yousefs doing great things, a Hall of Fame of notable Yousefs past and present, a guide to every spelling, and a pile of fun facts. The tone is affectionate satire. We make fun of the name, the spellings and the paperwork, never of the people who carry it.</p>
<h2>How the news works</h2>
<p>Each day our news desk scans recent headlines for positive stories about people with the name, in any spelling. We only feature public figures, we skip anything involving crime, conflict or tragedy, and every summary links back to its original source so you can read the full story.</p>
<h2>Who runs this?</h2>
<p>YousefTube was founded by a Yousef, for Yousefs and the people who love them. It is an independent fan site and is not affiliated with YouTube, Google, or any person featured here.</p>
<h2>Get in touch</h2>
<p>Corrections, tips and nominations for the Hall of Fame are always welcome. See our <a href="/contact/">contact page</a>.</p>
</article>"""))
urls.append(page("contact/index.html", "Contact YousefTube",
  "Send YousefTube a tip, a correction, a Hall of Fame nomination or a sponsorship inquiry.",
  """<div class="crumbs"><a href="/">Home</a> / Contact</div>
<article class="prose">
<h1>Contact</h1>
<p class="tag">Tips, corrections, nominations and sponsorships. We read everything, especially if it's about a Yousef.</p>
<div class="callout"><span class="eyebrow">Email</span><b style="font-size:1.3rem;user-select:all">tips@youseftube.com</b></div>
<h2>What to send us</h2>
<p><b>Good news.</b> Know a Yousef (any spelling) who just won something, launched something or did something kind? Send a link to a public news story or official announcement.</p>
<p><b>Corrections.</b> If we got a fact wrong, tell us and point us to a source. We fix errors quickly.</p>
<p><b>Hall of Fame nominations.</b> Tell us who, and why they deserve a plaque.</p>
<p><b>Sponsorship.</b> Interested in sponsoring Yousef of the Month or the weekly newsletter? Say hello.</p>
<p>We feature public figures only. Please don't send private information about anyone.</p>
</article>"""))

# ---- Sitemap & robots
urls.append(SITE + "/privacy.html")
open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print(len(urls), "urls")
