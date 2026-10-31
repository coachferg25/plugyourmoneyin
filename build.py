#!/usr/bin/env python3
"""Regenerate the whole static site from data/*.json.   Usage: python3 build.py
Output goes to ./site (safe to delete and rebuild). No dependencies beyond Python 3."""
import json, shutil, pathlib, html, datetime
ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "site"
cfg = json.load(open(ROOT/"data/site.json"))
apps = json.load(open(ROOT/"data/apps.json"))["apps"]
changes = sorted(json.load(open(ROOT/"data/changelog.json"))["entries"], key=lambda e: e["date"], reverse=True)
BASE = cfg["base_url"].rstrip("/")
PLAT = [("chatgpt","ChatGPT"),("claude","Claude"),("grok","Grok")]
STATUS_LABEL = {"yes":"Works","partial":"Partial","no":"No","unknown":"Unknown"}
ACCESS = {"read-only":("Read-only","Can look at balances and transactions. Cannot move money or trade."),
          "read-edit":("Read + edit","Can read, and may be able to change data inside the app (not move money)."),
          "draft-trades":("Drafts trades","AI prepares orders; a human must confirm them in the broker's app."),
          "can-trade":("Can trade","AI can place real orders."),
          "none":("Nothing to connect","No official route found.")}
CONF_LABEL = {"documented":"","inferred":"inferred","reported":"reported (secondary source)","third-party-claim":"third-party claim",
              "absence-of-docs":"no docs found","vendor-staff-statement":"staff statement"}
e = html.escape
today = max([a["checked"] for a in apps])

def pretty(d): return datetime.date.fromisoformat(d).strftime("%b %-d, %Y")

def badge(st): return f'<span class="badge s-{st}">{STATUS_LABEL[st]}</span>'
def abadge(k): return f'<span class="abadge a-{k}" title="{e(ACCESS[k][1])}">{ACCESS[k][0]}</span>'

DISCLAIMER = ("Not financial advice. This site is for information only. Statuses come from each company's public pages "
              "and may be out of date or wrong. Check the source link before you connect any account, and never give an AI your bank password.")

def layout(title, desc, path, body, extra_head="", jsonld=""):
    url = f"{BASE}/{path}".rstrip("/") if path else BASE + "/"
    depth = path.count("/")
    rel = "../"*depth
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(cfg['name'])}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="{rel}assets/style.css">
{extra_head}{jsonld}
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap bar">
 <a class="brand" href="{rel or './'}index.html"><span class="plug">⏻</span> {e(cfg['name'])}</a>
 <nav><a href="{rel}index.html#table">Status board</a><a href="{rel}safety.html">Safety</a><a href="{rel}changes.html">What changed</a><a href="{rel}index.html#newsletter">Newsletter</a></nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer><div class="wrap">
 <p class="disc"><strong>Disclaimer.</strong> {e(DISCLAIMER)}</p>
 <p class="small">Independent. Not affiliated with OpenAI, Anthropic, xAI or any company listed. Some links may become affiliate links in the future; if so, they will be marked.
 Last full check: {pretty(today)}. <a href="{rel}changes.html">What changed</a>.</p>
</div></footer>
</body></html>"""

def newsletter():
    return f"""<section id="newsletter" class="card news">
<h2>Get the weekly change list</h2>
<p>One short email when a bank, broker or app changes what it allows with ChatGPT, Claude or Grok.</p>
<!-- TODO: {e(cfg['newsletter_note'])} -->
<form action="{e(cfg['newsletter_action'])}" method="post" data-todo="newsletter-placeholder">
 <label class="sr" for="email">Email address</label>
 <input id="email" type="email" name="email" placeholder="you@example.com" required>
 <button type="submit">Subscribe</button>
</form>
<p class="small todo">TODO (builder): this form is a placeholder and is not connected to any service yet.</p>
</section>"""

def affiliate(a):
    return f"""<aside class="card affil" data-affiliate-slot="{e(a['slug'])}">
<h3>Open {e(a['name'])}</h3>
<!-- AFFILIATE-SLOT: {e(a['slug'])} | url: {e(str(a['affiliate']['url']))} | {e(a['affiliate']['note'])} -->
<p class="small todo">Affiliate link slot (empty). Nothing is linked here yet. If a link is added later it will be labelled as an affiliate link.</p>
</aside>"""

def row_summary(a):
    return " / ".join(f"{n}: {STATUS_LABEL[a['platforms'][k]['status']]}" for k,n in PLAT)

# ---------- homepage ----------
def home():
    rows=[]
    for a in sorted(apps,key=lambda x:x["name"].lower()):
        cells="".join(f'<td data-sort="{a["platforms"][k]["status"]}" data-col="{k}">{badge(a["platforms"][k]["status"])}</td>' for k,_ in PLAT)
        rows.append(f'<tr data-cat="{e(a["category"])}" data-access="{a["access"]}" data-name="{e(a["name"].lower())}">'
                    f'<th scope="row" data-sort="{e(a["name"].lower())}"><a href="apps/{a["slug"]}.html">{e(a["name"])}</a><span class="cat">{e(a["category"])}</span></th>'
                    f'{cells}<td data-sort="{a["access"]}">{abadge(a["access"])}</td><td class="route">{e(a["route"])}</td>'
                    f'<td data-sort="{a["checked"]}" class="date">{pretty(a["checked"])}</td></tr>')
    cats=sorted({a["category"] for a in apps})
    cat_opts="".join(f'<option>{e(c)}</option>' for c in cats)
    acc_opts="".join(f'<option value="{k}">{v[0]}</option>' for k,v in ACCESS.items())
    # counts
    def counts(k):
        c={s:0 for s in STATUS_LABEL}
        for a in apps: c[a["platforms"][k]["status"]]+=1
        return c
    cards="".join(f'<div class="stat"><h3>{n}</h3>'+"".join(f'<span class="badge s-{s}">{STATUS_LABEL[s]} {counts(k)[s]}</span> ' for s in STATUS_LABEL)+'</div>' for k,n in PLAT)
    body=f"""
<section class="hero">
<h1>Can I plug my money into my AI?</h1>
<p class="lead">{e(cfg['tagline'])}</p>
<p class="small">{len(apps)} apps checked against their own help pages and docs. Last full check <strong>{pretty(today)}</strong>. We say <em>Unknown</em> when we can't confirm, never a guess.</p>
</section>
<section class="stats" aria-label="Summary counts">{cards}</section>
<section class="card note"><strong>Quick answer.</strong> ChatGPT (Finances) and Grok (Finance integration) can link US bank, card and investment accounts <em>read-only</em> through Plaid. Claude has no built-in bank linking yet; it relies on company connectors (MCP) and third-party tools. Brokerages like Robinhood, Public and IBKR are the ones that can also <em>trade</em>. <a href="safety.html">Read the safety guide first.</a></section>
<section id="table">
<h2>Status board</h2>
<div class="filters">
 <label>Search <input id="q" type="search" placeholder="Fidelity, Chase, YNAB…"></label>
 <label>Type <select id="fcat"><option value="">All</option>{cat_opts}</select></label>
 <label>Access <select id="facc"><option value="">All</option>{acc_opts}</select></label>
 <label>Works with <select id="fplat"><option value="">Any</option><option value="chatgpt">ChatGPT</option><option value="claude">Claude</option><option value="grok">Grok</option></select></label>
 <span id="count" class="small" aria-live="polite"></span>
</div>
<div class="tablewrap"><table id="board">
<thead><tr><th scope="col" data-key="name" aria-sort="ascending"><button>App</button></th><th scope="col"><button data-key="chatgpt">ChatGPT</button></th><th scope="col"><button data-key="claude">Claude</button></th><th scope="col"><button data-key="grok">Grok</button></th><th scope="col"><button data-key="access">Access</button></th><th scope="col">Route</th><th scope="col"><button data-key="date">Checked</button></th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<details class="legend card"><summary>How to read this</summary>
<ul>
<li>{badge('yes')} A documented way to connect it exists and works for that assistant.</li>
<li>{badge('partial')} Only through a limited route: third-party tool, self-hosted setup, read-only subset, or not individually confirmed.</li>
<li>{badge('no')} No official or supported route found as of the check date.</li>
<li>{badge('unknown')} We couldn't confirm either way. We don't guess.</li>
</ul>
<p><strong>Access:</strong> {abadge('read-only')} {abadge('read-edit')} {abadge('draft-trades')} {abadge('can-trade')}. Tags like “inferred” or “third-party claim” on each app page tell you how strong the evidence is.</p>
</details>
</section>
<section class="card affil-home"><h3>Tools to consider</h3>
<!-- AFFILIATE-SLOT: homepage-banner -->
<p class="small todo">Affiliate-ready slot (empty). Nothing is linked yet.</p></section>
{newsletter()}
<script src="assets/app.js" defer></script>
"""
    ld='<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"WebSite","name":cfg["name"],"url":BASE+"/","description":cfg["tagline"]})+'</script>'
    return layout(f"{cfg['name']}: which money apps work with ChatGPT, Claude and Grok",
      "A live status board of US banks, brokerages and budgeting apps and whether they work with ChatGPT, Claude and Grok, read-only or can trade. Sources and dates on every row.","",body,jsonld=ld)

# ---------- app page ----------
SRC_LABEL={"vendor":"Company's own page","vendor-staff":"Company staff statement","third-party":"Third-party source"}
def app_page(a):
    n=e(a["name"])
    plats="".join(f"""<tr><th scope="row">{nm}</th><td>{badge(a['platforms'][k]['status'])}</td><td>{e(a['platforms'][k]['how'])}
{('<span class="conf">'+CONF_LABEL.get(a['platforms'][k]['confidence'],a['platforms'][k]['confidence'])+'</span>') if CONF_LABEL.get(a['platforms'][k]['confidence'],'x') else ''}</td></tr>""" for k,nm in PLAT)
    issues="".join(f"<li>{e(i)}</li>" for i in a["issues"]) or "<li>None recorded.</li>"
    srcs="".join(f'<li><a href="{e(s["url"])}" rel="nofollow noopener" target="_blank">{e(s["label"])}</a> <span class="tag t-{s["type"]}">{SRC_LABEL[s["type"]]}</span></li>' for s in a["sources"])
    cg=a["platforms"]["chatgpt"]["status"]; cl=a["platforms"]["claude"]["status"]
    def ans(k):
        s=a["platforms"][k]["status"]
        return {"yes":"Yes.","partial":"Partly.","no":"No.","unknown":"Unknown."}[s]
    faq=[(f"Does {a['name']} work with ChatGPT?",f"{ans('chatgpt')} {a['platforms']['chatgpt']['how']}"),
         (f"Does {a['name']} work with Claude?",f"{ans('claude')} {a['platforms']['claude']['how']}"),
         (f"Does {a['name']} work with Grok?",f"{ans('grok')} {a['platforms']['grok']['how']}"),
         (f"Can an AI trade or move money in {a['name']}?",ACCESS[a['access']][1]+" "+a["access_note"])]
    faq_html="".join(f"<details open><summary>{e(q)}</summary><p>{e(r)}</p></details>" for q,r in faq)
    ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":r}} for q,r in faq]}
    body=f"""
<nav class="crumbs"><a href="../index.html">Status board</a> › {n}</nav>
<h1>Does {n} work with ChatGPT, Claude and Grok?</h1>
<p class="lead">{e(a['summary'])}</p>
<p class="small">Checked {pretty(a['checked'])} · {e(a['category'])} · Route: {e(a['route'])}</p>
<table class="plat"><thead><tr><th>Assistant</th><th>Status</th><th>How</th></tr></thead><tbody>{plats}</tbody></table>
<section class="card"><h2>Read-only or can it trade?</h2><p>{abadge(a['access'])} {e(a['access_note'])}</p></section>
<section><h2>Known issues and caveats</h2><ul>{issues}</ul></section>
<section><h2>Common questions</h2>{faq_html}</section>
<section><h2>Sources</h2><ul class="srcs">{srcs}</ul><p class="small">Statuses are only as good as these sources. Found something out of date? That's what the weekly check is for. Contact: {e(cfg['contact'])}.</p></section>
{affiliate(a)}
{newsletter()}
<p><a href="../safety.html">Before you connect anything, read the safety guide →</a></p>
"""
    return layout(f"Does {a['name']} work with ChatGPT, Claude and Grok? ({pretty(a['checked'])})",
      f"{a['name']} and AI assistants: ChatGPT {STATUS_LABEL[cg]}, Claude {STATUS_LABEL[cl]}, Grok {STATUS_LABEL[a['platforms']['grok']['status']]}. Read-only or can trade? Sources and last-checked date.",
      f"apps/{a['slug']}.html",body,jsonld='<script type="application/ld+json">'+json.dumps(ld)+'</script>')

def fix_rel(page):  # newsletter anchor links on app pages
    return page

def safety():
    body="""
<h1>Is it safe to plug your money into an AI?</h1>
<p class="lead">Short answer: looking is much safer than acting. Here is how to keep it that way.</p>
<section><h2>The three levels of access</h2>
<ol><li><strong>Read-only.</strong> The AI can see balances and transactions. It cannot move money. ChatGPT Finances and Grok's Finance integration work this way, through Plaid.</li>
<li><strong>Read + edit.</strong> Budgeting apps like Monarch can offer an option that lets the AI change data inside the app. Keep it off unless you need it.</li>
<li><strong>Can trade.</strong> Brokers like Robinhood, Public and Coinbase let an AI place real orders. A mistake can cost real money.</li></ol></section>
<section><h2>Rules of thumb</h2><ul>
<li>Never type your bank or brokerage password into a chat or give it to an AI agent. Banks such as Chase say they block agents that log in as you.</li>
<li>Connect through the company's own sign-in screen (OAuth or Plaid), so the AI never sees your password.</li>
<li>Start read-only. Add trading only in a small separate account with money you can afford to lose.</li>
<li>Prefer a company's official connector over a third-party one. Third-party servers may hold your tokens or data.</li>
<li>Check which accounts you shared and revoke what you don't use (your bank's “linked apps” page, and Plaid's portal).</li>
<li>An AI can be wrong. Double-check numbers before acting, and be careful with anything that can place an order.</li>
<li>Read the privacy settings. For example, OpenAI says it does not train on your Finances data; confirm current terms yourself.</li></ul></section>
<section><h2>Why “Partial” is common</h2><p>Banks and brokers decide what is allowed. Some block logins by AI agents but allow customer-approved data sharing. Rules are changing fast, and a US federal data-sharing rule (CFPB section 1033) is currently on hold during a rewrite. See <a href="changes.html">what changed</a>.</p></section>
<section class="card"><strong>Not financial advice.</strong> Nothing here is a recommendation to buy, sell or connect anything.</section>
"""
    return layout("Is it safe to connect your bank or brokerage to ChatGPT, Claude or Grok?","A plain-English safety guide: read-only vs trading access, what to share, and what never to share when connecting money accounts to an AI assistant.","safety.html",body)

def changes_page():
    names={a["slug"]:a["name"] for a in apps}
    items="".join(f'<li><time datetime="{c["date"]}">{pretty(c["date"])}</time><h3>{e(c["title"])}</h3><p>{e(c["detail"])}</p>'
        +(f'<p class="small">App: <a href="apps/{c["slug"]}.html">{e(names[c["slug"]])}</a>'+(f' · <a href="{e(c["source"])}" rel="nofollow noopener" target="_blank">Source</a>' if c.get("source") else '')+'</p>' if c.get("slug") else '')+'</li>' for c in changes)
    body=f'<h1>What changed</h1><p class="lead">A dated log of changes to what works with ChatGPT, Claude and Grok. Newest first.</p><ul class="log">{items}</ul>{newsletter()}'
    return layout("What changed: money apps and AI assistants","Dated log of changes to which banks, brokers and money apps work with ChatGPT, Claude and Grok.","changes.html",body)

def write(path, content):
    p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding="utf-8")

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/"assets",OUT/"assets")
    write("index.html",home())
    for a in apps: write(f"apps/{a['slug']}.html",app_page(a))
    write("safety.html",safety()); write("changes.html",changes_page())
    urls=[""]+[f"apps/{a['slug']}.html" for a in apps]+["safety.html","changes.html"]
    sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{BASE}/{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)+"</urlset>\n"
    write("sitemap.xml",sm)
    write("robots.txt",f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print(f"Built {len(apps)} app pages + {len(urls)} total URLs into {OUT}")
if __name__=="__main__": main()
