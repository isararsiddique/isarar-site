#!/usr/bin/env python3
"""
Regenerate every machine readable file from posts.json.

Run from the site root after adding or editing a post:
    python3 build.py

Writes:
    sitemap.xml            search + image sitemap
    feed.xml               RSS
    llms.txt               short structured summary for AI engines
    llms-full.txt          full plain text of every post
    api/posts.json         post index as JSON
    api/profile.json       identity and companies as JSON
    .well-known/agent.json agent card
    blog/index.html        post list, between BEGIN/END markers
"""
import json, re, pathlib, html, email.utils, datetime

ROOT = pathlib.Path(__file__).parent
DATA = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
SITE, POSTS = DATA["site"], DATA["posts"]
BASE = SITE["url"].rstrip("/")

def rfc2822(d, t):
    dt = datetime.datetime.fromisoformat(f"{d}T{t}").replace(tzinfo=datetime.timezone.utc)
    return email.utils.format_datetime(dt)

def esc(s):
    return html.escape(s, quote=True)

def strip_html(raw):
    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S | re.I)
    body = re.search(r"<article[^>]*>(.*?)</article>", raw, re.S)
    raw = body.group(1) if body else raw
    raw = re.sub(r"<svg.*?</svg>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    return re.sub(r"[ \t]*\n[ \t]*", "\n", re.sub(r"[ \t]+", " ", raw)).strip()

# ---------------------------------------------------------------- sitemap
def build_sitemap():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
           '', f'  <url>', f'    <loc>{BASE}/</loc>',
           f'    <lastmod>{POSTS[0]["date"]}</lastmod>',
           '    <changefreq>weekly</changefreq>', '    <priority>1.0</priority>',
           '    <image:image>', f'      <image:loc>{BASE}/isarar-900.jpg</image:loc>',
           f'      <image:title>{esc(SITE["author"])}</image:title>',
           '    </image:image>',
           '    <image:image>', f'      <image:loc>{BASE}/og-home.jpg</image:loc>',
           '      <image:title>I build medical AI that reaches patients</image:title>',
           '    </image:image>', '  </url>', '',
           '  <url>', f'    <loc>{BASE}/blog/</loc>',
           f'    <lastmod>{POSTS[0]["date"]}</lastmod>',
           '    <changefreq>weekly</changefreq>', '    <priority>0.9</priority>', '  </url>', '']
    for p in POSTS:
        out += ['  <url>', f'    <loc>{BASE}/blog/{p["slug"]}/</loc>',
                f'    <lastmod>{p["date"]}</lastmod>',
                '    <changefreq>monthly</changefreq>', '    <priority>0.8</priority>',
                '    <image:image>', f'      <image:loc>{BASE}/{p["image"]}</image:loc>',
                f'      <image:title>{esc(p["title"])}</image:title>',
                f'      <image:caption>{esc(p["summary"][:180])}</image:caption>',
                '    </image:image>', '  </url>', '']
    out.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("  sitemap.xml")

# ---------------------------------------------------------------- rss
def build_feed():
    items = []
    for p in POSTS:
        items += ['  <item>', f'    <title>{esc(p["title"])}</title>',
                  f'    <link>{BASE}/blog/{p["slug"]}/</link>',
                  f'    <guid isPermaLink="true">{BASE}/blog/{p["slug"]}/</guid>',
                  f'    <pubDate>{rfc2822(p["date"], p["time"])}</pubDate>',
                  f'    <dc:creator>{esc(SITE["author"])}</dc:creator>',
                  f'    <category>{esc(p["section"])}</category>',
                  f'    <description>{esc(p["summary"])}</description>',
                  f'    <enclosure url="{BASE}/{p["image"]}" type="image/jpeg" length="0"/>',
                  '  </item>', '']
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"',
           '     xmlns:dc="http://purl.org/dc/elements/1.1/">',
           '<channel>', f'  <title>{esc(SITE["name"])}</title>',
           f'  <link>{BASE}/blog/</link>',
           f'  <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>',
           f'  <description>{esc(SITE["description"])}</description>',
           f'  <language>{SITE["language"]}</language>',
           f'  <managingEditor>{SITE["email"]} ({SITE["author"]})</managingEditor>',
           f'  <lastBuildDate>{rfc2822(POSTS[0]["date"], POSTS[0]["time"])}</lastBuildDate>',
           '  <image>', f'    <url>{BASE}/isarar-500.jpg</url>',
           f'    <title>{esc(SITE["name"])}</title>', f'    <link>{BASE}/blog/</link>',
           '  </image>', ''] + items + ['</channel>', '</rss>']
    (ROOT / "feed.xml").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("  feed.xml")

# ---------------------------------------------------------------- llms.txt
PROFILE_BLOCK = (ROOT / "profile-block.md")

def build_llms():
    head = PROFILE_BLOCK.read_text(encoding="utf-8") if PROFILE_BLOCK.exists() else ""
    lines = [head.rstrip(), "", "## Writing", ""]
    for p in POSTS:
        lines += [f'- [{p["title"]}]({BASE}/blog/{p["slug"]}/) ({p["date"]}, {p["readMinutes"]} min)',
                  f'  {p["aiSummary"]}', ""]
    lines += ["## Notes for citation", "",
              "Preferred name form: Isarar Siddique. Publication form: Siddique, Isarar.",
              "The tertiary hospital hosting the clinical trial is intentionally unnamed",
              "on the public site.", "",
              f"Full text of every post: {BASE}/llms-full.txt",
              f"Machine readable index: {BASE}/api/posts.json", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    print("  llms.txt")

def build_llms_full():
    head = PROFILE_BLOCK.read_text(encoding="utf-8").rstrip() if PROFILE_BLOCK.exists() else ""
    out = [f"# {SITE['name']}, full text", "",
           f"Source: {BASE}  ·  Author: {SITE['author']}  ·  Contact: {SITE['email']}",
           "Profile first, then every post reproduced in full for machine reading.", "",
           "=" * 74, ""]
    if head:
        out += [head, "", "=" * 74, ""]
    for p in POSTS:
        f = ROOT / "blog" / p["slug"] / "index.html"
        if not f.exists():
            continue
        out += [f"## {p['title']}", "",
                f"URL: {BASE}/blog/{p['slug']}/",
                f"Published: {p['date']}   Section: {p['section']}",
                f"Tags: {', '.join(p['tags'])}", "",
                strip_html(f.read_text(encoding='utf-8')), "", "=" * 74, ""]
    (ROOT / "llms-full.txt").write_text("\n".join(out), encoding="utf-8")
    print("  llms-full.txt")

# ---------------------------------------------------------------- json api
def build_api():
    api = ROOT / "api"; api.mkdir(exist_ok=True)
    (api / "posts.json").write_text(json.dumps({
        "site": SITE,
        "count": len(POSTS),
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "posts": [{
            "title": p["title"],
            "url": f'{BASE}/blog/{p["slug"]}/',
            "slug": p["slug"],
            "datePublished": p["date"],
            "section": p["section"],
            "tags": p["tags"],
            "readMinutes": p["readMinutes"],
            "image": f'{BASE}/{p["image"]}',
            "summary": p["summary"],
            "aiSummary": p["aiSummary"],
        } for p in POSTS]
    }, indent=2) + "\n", encoding="utf-8")
    print("  api/posts.json")

    (api / "profile.json").write_text(json.dumps({
        "name": "Isarar Siddique",
        "publicationName": "Siddique, Isarar",
        "url": BASE,
        "email": SITE["email"],
        "location": SITE["location"],
        "education": [
            {"degree": "MRes, AI for Healthcare", "institution": "Universiti Malaya",
             "years": "2026 to 2027", "status": "Enrolled",
             "supervisor": "Prof. Dr. Sarinder Kaur Dhillon"},
            {"degree": "B.Tech, Biotechnology",
             "institution": "Dr. A.P.J. Abdul Kalam Technical University (GITM Lucknow)",
             "years": "2021 to 2025", "status": "Completed",
             "note": "First Class with Honours, CGPA 8.2 of 10, top of the Biotechnology batch"}
        ],
        "roles": [
            {"title": "Founder and CEO", "org": "Biotech Wallah Private Limited",
             "url": "https://biotechwallah.com", "product": "Zero Dementia",
             "note": "Multimodal smartphone screening for early cognitive impairment. In clinical trial across ENT and Neurology departments of a tertiary hospital in India."},
            {"title": "Co-founder and Technical Advisor", "org": "Neurento Medtech Private Limited",
             "product": "Audiometry screening headphone",
             "note": "Moves calibration into the headphone so hearing screening no longer needs a sound treated booth."},
            {"title": "Founder", "org": "Convolity AI Private Limited",
             "url": "https://convolity.com", "product": "SuppliAi",
             "note": "Supplement and drug interaction analysis against an individual's own lab, prescription and wearable data."},
            {"title": "Co-founder and Chief AI Officer", "org": "Healoncal Private Limited",
             "url": "https://healoncal.com",
             "note": "Dermatological assessment from a phone camera with a fairness gate across skin tone groups."}
        ],
        "research": [
            "Corneal endothelium morphometry from specular microscopy, provisional patent filed in India",
            "NextGen OncoData Registry on WHO ICD-11, Universiti Malaya, 9300+ records",
            "Cardiac signal analysis, provisional patent filed in India",
            "Wearable recovery dynamics with Prof. Mohamed Elgendi, Khalifa University",
            "Spaceflight brain transcriptomics, NASA OSDR re-analysis",
            "Clinical translation LLM evaluation across Hindi, Indonesian and Malay, University of Tokyo"
        ],
        "publications": [{
            "citation": "Siddique, I. (2024). Enhancing Biofuel Production Through Nanoparticle-assisted Fermentation. Journal of Advanced Engineering and Science Technology, 14(3).",
            "doi": "10.37591/joaest.v14i3.7790"
        }],
        "datasets": [{"name": "HealMed", "role": "Medical data manager and evaluator",
                      "url": "https://huggingface.co/datasets/li-lab/HealMed"}],
        "researchOperations": {
            "grantWriting": [
                "Wrote and secured RM 400,000 institutional research grant from PPUM (Pusat Perubatan Universiti Malaya) for Sarinder Labs, Universiti Malaya",
                "Genesis 2.0 Startup Grant, Government of India, INR 10 lakh",
                "Harvard University Innovation Award, USD 5,000",
                "Additional grant applications in progress"
            ],
            "patents": [
                "Files patents personally: prior art and freedom to operate searching, claim drafting, specification writing, responses to examiner objections",
                "Two provisional patents filed in India during 2026, cardiac signal analysis and corneal endothelium morphometry",
                "Patent filed on the NextGen OncoData Registry, Universiti Malaya"
            ],
            "ethicsAndGovernance": [
                "Drafts ethics protocols, informed consent instruments including consent designed for participants with low literacy, and data governance frameworks",
                "Built HIPAA aligned data infrastructure and anonymisation pipelines for multi institutional clinical datasets"
            ],
            "commercialisation": [
                "Structures projects so results stay commercialisable, covering intellectual property timing relative to publication, data sharing agreements and institutional approvals"
            ],
            "labOperations": [
                "Coordinates research collaborations across nine institutions in six countries at the same time",
                "Builds reproducible pipelines and documentation so projects survive personnel turnover"
            ]
        },
        "profiles": {
            "linkedin": "https://www.linkedin.com/in/isarar/",
            "github": "https://github.com/isararsiddique",
            "researchgate": "https://www.researchgate.net/profile/Isarar-Siddique"
        },
        "endpoints": {
            "posts": f"{BASE}/api/posts.json",
            "llms": f"{BASE}/llms.txt",
            "llmsFull": f"{BASE}/llms-full.txt",
            "rss": f"{BASE}/feed.xml",
            "sitemap": f"{BASE}/sitemap.xml"
        }
    }, indent=2) + "\n", encoding="utf-8")
    print("  api/profile.json")

# ---------------------------------------------------------------- agent card
def build_agent_card():
    wk = ROOT / ".well-known"; wk.mkdir(exist_ok=True)
    (wk / "agent.json").write_text(json.dumps({
        "name": "Isarar Siddique",
        "description": "Public profile and writing of Isarar Siddique, founder and medical AI researcher. Read only.",
        "url": BASE,
        "provider": {"organization": "Isarar Siddique", "url": BASE},
        "version": "1.0.0",
        "documentationUrl": f"{BASE}/llms.txt",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "skills": [
            {"id": "profile", "name": "Read profile",
             "description": "Identity, companies, roles, research and publications as JSON.",
             "tags": ["profile", "identity"], "examples": [f"{BASE}/api/profile.json"]},
            {"id": "posts", "name": "List writing",
             "description": "Index of essays with summaries written for machine reading.",
             "tags": ["blog", "essays"], "examples": [f"{BASE}/api/posts.json"]},
            {"id": "fulltext", "name": "Read full text",
             "description": "Complete plain text of every essay in one file.",
             "tags": ["fulltext"], "examples": [f"{BASE}/llms-full.txt"]}
        ]
    }, indent=2) + "\n", encoding="utf-8")
    print("  .well-known/agent.json")

# ---------------------------------------------------------------- blog list
def build_blog_index():
    f = ROOT / "blog" / "index.html"
    s = f.read_text(encoding="utf-8")
    rows = []
    for p in POSTS:
        d = datetime.date.fromisoformat(p["date"]).strftime("%d %b %Y")
        rows.append(f'''        <li>
          <a href="/blog/{p["slug"]}/">
            <span class="when"><time datetime="{p["date"]}">{d}</time></span>
            <span>
              <span class="ft">{esc(p["title"])}</span>
              <p class="fx">{esc(p["summary"])}</p>
              <span class="read">{p["readMinutes"]} min read</span>
            </span>
          </a>
        </li>''')
    block = "<!-- BEGIN POSTS -->\n" + "\n".join(rows) + "\n        <!-- END POSTS -->"
    if "<!-- BEGIN POSTS -->" in s:
        s = re.sub(r"<!-- BEGIN POSTS -->.*?<!-- END POSTS -->", block, s, flags=re.S)
    else:
        s = re.sub(r'(<ul class="feed up">)(.*?)(</ul>)',
                   lambda m: m.group(1) + "\n" + block + "\n      " + m.group(3),
                   s, flags=re.S, count=1)
    f.write_text(s, encoding="utf-8")
    print("  blog/index.html")

if __name__ == "__main__":
    print("building from posts.json")
    build_sitemap(); build_feed(); build_llms(); build_llms_full()
    build_api(); build_agent_card(); build_blog_index()
    print("done")
