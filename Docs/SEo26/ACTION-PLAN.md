# SEO Action Plan — machinaos.ai
**Generated:** 2026-03-31  
**Overall Health Score:** 31 / 100  
**Priority Framework:** Critical → High → Medium → Low

> **Context:** This is a pre-launch startup site with 9 static HTML pages. Almost every issue is a *missing* element rather than something broken. The static HTML foundation makes every fix below fast and low-risk.

---

## CRITICAL — Fix Immediately

### C-1: Deploy robots.txt
**Impact:** 🔴 Undefined crawl behavior, no sitemap declaration  
**Effort:** 🟢 Low (5 minutes — file is ready)  

**File ready at:** [`reports/machinaos-ai/robots.txt`](reports/machinaos-ai/robots.txt) — deploy to web root.

The generated file is minimal. **Before deploying, add AI crawler policy rules** (paste below into the file):

Create `https://machinaos.ai/robots.txt`:
```
User-agent: *
Allow: /

Sitemap: https://machinaos.ai/sitemap.xml

# AI training crawlers — block to retain content rights
User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: CCBot
Disallow: /

# AI search indexing — allow for product discovery
User-agent: PerplexityBot
Allow: /

User-agent: ChatGPT-User
Allow: /
```

---

### C-2: Deploy sitemap.xml
**Impact:** 🔴 Google cannot reliably discover all pages  
**Effort:** 🟢 Low (5 minutes — file is ready)  

**File ready at:** [`reports/machinaos-ai/sitemap.xml`](reports/machinaos-ai/sitemap.xml) — deploy to web root.

**8 URLs included.** `/pricing.html` and `/index.html` are intentionally excluded (see notes in file).

After deploying, submit in Google Search Console: _Sitemaps → Enter sitemap URL → Submit_.

The XML content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <url>
    <loc>https://machinaos.ai/</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>

  <url>
    <loc>https://machinaos.ai/features.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <url>
    <loc>https://machinaos.ai/user-stories.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <!-- pricing.html EXCLUDED — placeholder content, noindex recommended -->

  <url>
    <loc>https://machinaos.ai/demo-guide.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>

  <url>
    <loc>https://machinaos.ai/screens.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>

  <url>
    <loc>https://machinaos.ai/about.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>

  <url>
    <loc>https://machinaos.ai/contact.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>

  <url>
    <loc>https://machinaos.ai/links.html</loc>
    <lastmod>2026-03-31</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.4</priority>
  </url>

</urlset>
```

> **Note on pricing.html:** Included here with priority 0.8. Once pricing is finalized remove "Placeholder" from the title. If keeping as placeholder long-term, add `<meta name="robots" content="noindex">` and remove from sitemap.

---

### C-3: Fix Homepage Duplicate — 301 Redirect + Canonical
**Impact:** 🔴 `/` and `/index.html` both return 200 — splits link equity and indexation  
**Effort:** 🟢 Low (30 minutes)

Two steps required — both needed:

**Step 1: Server-level 301 redirect in nginx:**
```nginx
location = /index.html {
    return 301 https://machinaos.ai/;
}
```

**Step 2: Add canonical tag to homepage (served at `/`):**
```html
<link rel="canonical" href="https://machinaos.ai/" />
```

Do NOT include `/index.html` in the sitemap — only include `https://machinaos.ai/`.

---

### C-4: Add Canonical Tags to All Other Pages
**Impact:** 🔴 No URL authority declaration on any page  
**Effort:** 🟢 Low (30 minutes)  

Add to `<head>` of every page (absolute URLs):

```html
<!-- index.html -->
<link rel="canonical" href="https://machinaos.ai/" />

<!-- about.html -->
<link rel="canonical" href="https://machinaos.ai/about.html" />

<!-- features.html -->
<link rel="canonical" href="https://machinaos.ai/features.html" />

<!-- pricing.html -->
<link rel="canonical" href="https://machinaos.ai/pricing.html" />

<!-- user-stories.html -->
<link rel="canonical" href="https://machinaos.ai/user-stories.html" />

<!-- demo-guide.html -->
<link rel="canonical" href="https://machinaos.ai/demo-guide.html" />

<!-- screens.html -->
<link rel="canonical" href="https://machinaos.ai/screens.html" />

<!-- contact.html -->
<link rel="canonical" href="https://machinaos.ai/contact.html" />

<!-- links.html -->
<link rel="canonical" href="https://machinaos.ai/links.html" />
```

---

### C-4: Noindex Pricing Page Until Content is Finalized
**Impact:** 🔴 "Placeholder" in title/content destroys CTR; thin 200-word page risks quality signals  
**Effort:** 🟢 Low (5 minutes)  

Add to `<head>` of `pricing.html`:
```html
<meta name="robots" content="noindex, follow">
```

The page is already excluded from `sitemap.xml` and `Disallow`'d in `robots.txt` (per generated files). The `noindex` meta tag is the belt-and-suspenders protection in case Google finds the page via internal links despite the robots.txt disallow.

**When pricing is finalized:**
1. Remove `noindex` tag
2. Update title: `MachinaOS Pricing | Plans for Developers and Teams`
3. Add pricing.html back to sitemap.xml
4. Remove the `Disallow: /pricing.html` line from robots.txt

---

## HIGH — Fix Within 1 Week

### H-1: Add Meta Descriptions to All 9 Pages
**Impact:** 🟠 Direct CTR improvement — Google generates poor snippets from thin pages  
**Effort:** 🟢 Low (1 hour)  

| Page | Suggested Meta Description |
|---|---|
| Homepage | "MachinaOS is a local-first AI orchestration layer that transforms intent into governed, multi-step agentic workflows. Built for developers who need traceability." |
| /about.html | "Explore MachinaOS's architecture, roadmap, and engineering principles behind local-first, governed AI execution. Three development stages: Core, Shell, OS Layer." |
| /features.html | "MachinaOS features: neural indexing, contextual exploration, multi-agent delegation, policy enforcement, and human approval gates for local AI workflows." |
| /pricing.html | "MachinaOS plans: Free tier for local runtimes, Intelligence at $49/mo for multi-agent workflows, and Enterprise for distributed AI deployments." |
| /user-stories.html | "How developers and engineering teams use MachinaOS for repo onboarding, environment setup, debugging, consultancy discovery, and governed automation." |
| /demo-guide.html | "Step-by-step guide to setting up MachinaOS: initialize the local runtime, map workspace context, apply safety policies, and run your first governed AI goal." |
| /screens.html | "Screenshots of the MachinaOS runtime interface — system controls, workflow orchestration, agent coordination, and runtime monitoring." |
| /contact.html | "Contact MachinaOS for support, sales, or careers. Reach us at info@machinaos.ai or sales@machina-intelligence.com." |
| /links.html | "MachinaOS ecosystem: Machina Intelligence, AI Radar, Shopfloor Copilot, Teyra, and FantaCalcio AI — related products and platforms." |

---

### H-2: Set HTML Lang Attribute on All Pages
**Impact:** 🟠 Accessibility + language targeting  
**Effort:** 🟢 Low (5 minutes)  

Change `<html>` to `<html lang="en">` on every page.

---

### H-3: Add Organization + SoftwareApplication Schema to Homepage
**Impact:** 🟠 Knowledge Panel eligibility, product rich results  
**Effort:** 🟢 Low (45 minutes)  

> **Schema types to avoid (all will produce zero rich results):**
> - `Product` — designed for retail goods, not SaaS; use `SoftwareApplication` only
> - `FAQPage` — restricted to government/healthcare since August 2023
> - `HowTo` — removed from Google Search permanently in September 2023
> - `AggregateRating` — do NOT add until real post-launch reviews exist (policy violation)

Add to homepage `<head>`:
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://machinaos.ai/#organization",
  "name": "MachinaOS",
  "url": "https://machinaos.ai",
  "description": "Local-first intent runtime for governed AI agent orchestration",
  "foundingDate": "2025",
  "parentOrganization": {
    "@type": "Organization",
    "name": "Machina Intelligence",
    "url": "https://machina-intelligence.com"
  },
  "contactPoint": [
    {"@type": "ContactPoint", "email": "info@machinaos.ai", "contactType": "customer support"},
    {"@type": "ContactPoint", "email": "sales@machina-intelligence.com", "contactType": "sales"}
  ]
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://machinaos.ai/#software",
  "name": "MachinaOS",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "description": "Intent-native AI orchestration layer for local-first, governed multi-agent workflows",
  "url": "https://machinaos.ai",
  "softwareVersion": "beta",
  "featureList": "https://machinaos.ai/features.html",
  "screenshot": "https://machinaos.ai/screens.html",
  "offers": [
    {
      "@type": "Offer",
      "name": "Free",
      "price": "0",
      "priceCurrency": "USD",
      "availability": "https://schema.org/PreOrder",
      "description": "Single local runtime, core tool registry, session memory"
    },
    {
      "@type": "Offer",
      "name": "Intelligence",
      "price": "49",
      "priceCurrency": "USD",
      "availability": "https://schema.org/PreOrder",
      "description": "Multi-agent delegation, consensus flows, capability learning"
    },
    {
      "@type": "Offer",
      "name": "Enterprise",
      "availability": "https://schema.org/PreOrder",
      "description": "Distributed agent mesh, security policy templates, org-wide observability"
    }
  ],
  "publisher": {"@id": "https://machinaos.ai/#organization"}
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://machinaos.ai/#website",
  "name": "MachinaOS",
  "url": "https://machinaos.ai",
  "publisher": {"@id": "https://machinaos.ai/#organization"},
  "inLanguage": "en"
}
</script>
```

---

### H-4: Add WebPage Schema to Demo Guide (not HowTo)
**Impact:** 🟠 Semantic context for crawlers  
**Effort:** 🟢 Low (15 minutes)  

> ⚠️ **Correction:** HowTo rich results were **permanently removed from Google Search in September 2023**. Do not use `HowTo` schema — it will parse without error but never produce rich results. Use `WebPage` instead.

```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": "https://machinaos.ai/demo-guide.html#page",
  "name": "MachinaOS Setup Guide — Getting Started Locally",
  "description": "Step-by-step guide to initializing the MachinaOS local runtime, mapping workspace context, applying safety policies, and running your first governed AI goal.",
  "url": "https://machinaos.ai/demo-guide.html",
  "about": {"@id": "https://machinaos.ai/#software"},
  "isPartOf": {"@id": "https://machinaos.ai/#website"},
  "breadcrumb": {
    "@type": "BreadcrumbList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://machinaos.ai/"},
      {"@type": "ListItem", "position": 2, "name": "Demo Guide", "item": "https://machinaos.ai/demo-guide.html"}
    ]
  }
}
</script>
```

---

### H-5: Add BreadcrumbList Schema to All Non-Homepage Pages
**Impact:** 🟠 Breadcrumb display in SERPs  
**Effort:** 🟢 Low (30 minutes)  

Example for /features.html:
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://machinaos.ai/"},
    {"@type": "ListItem", "position": 2, "name": "Features", "item": "https://machinaos.ai/features.html"}
  ]
}
</script>
```

Repeat pattern for all 8 non-homepage pages.

---

### H-6: Add OG and Twitter Card Tags to All Pages
**Impact:** 🟠 Social sharing appearance, referral traffic quality  
**Effort:** 🟢 Low (1 hour)  

Add to `<head>` of all pages (customize per page):
```html
<!-- Open Graph -->
<meta property="og:type" content="website" />
<meta property="og:title" content="MachinaOS | Local-First AI Orchestration" />
<meta property="og:description" content="Intent-native runtime for governed AI agent workflows. Local-first, traceable, human-approved." />
<meta property="og:url" content="https://machinaos.ai/" />
<meta property="og:image" content="https://machinaos.ai/og-image.png" />
<meta property="og:site_name" content="MachinaOS" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="MachinaOS | Local-First AI Orchestration" />
<meta name="twitter:description" content="Intent-native runtime for governed AI agent workflows." />
<meta name="twitter:image" content="https://machinaos.ai/og-image.png" />
```

**Also create:** `og-image.png` — 1200×630px product screenshot or logo card. Needed for all social shares.

---

### H-7: Create llms.txt
**Impact:** 🟠 AI search engine discovery (Perplexity, ChatGPT)  
**Effort:** 🟢 Low (20 minutes)  

Create `https://machinaos.ai/llms.txt`:
```markdown
# MachinaOS

> Local-first intent runtime for governed AI agent orchestration.

## About
MachinaOS is an intent-native orchestration layer that converts natural-language goals 
into structured, multi-step agentic workflows with human approval checkpoints. 
Built for developers needing local-first, traceable AI execution.

## Key Capabilities
- Heuristic intent routing
- Planner/executor separation with governed execution
- Multi-agent delegation with scoped permissions
- Persistent local memory layers
- Human approval gates for risky operations

## Pricing
- Free: Single local runtime
- Intelligence: $49/mo — multi-agent workflows
- Enterprise: Custom — distributed agent mesh

## Resources
- Features: https://machinaos.ai/features.html
- User Stories: https://machinaos.ai/user-stories.html
- Demo Guide: https://machinaos.ai/demo-guide.html

## Company
MachinaOS is built by Machina Intelligence — https://machina-intelligence.com
```

---

### H-8: Add Legal Pages (Privacy Policy + Terms)
**Impact:** 🟠 Trust signal, GDPR compliance for EU users  
**Effort:** 🟡 Medium (legal review needed)  

The site has no privacy policy or terms of service. For a product with email contact forms, newsletter signups (if any), and pricing, these are legally required for EU users (GDPR). Both pages should be linked from the footer.

Create:
- `https://machinaos.ai/privacy.html`
- `https://machinaos.ai/terms.html`
- Add both to sitemap and footer navigation

---

## MEDIUM — Fix Within 1 Month

### M-1: Optimize Homepage Title and H1 for Search Intent

**Current title:** "MachinaOS | Local-First Intent Runtime"  
**Problem:** "Intent Runtime" is jargon not searched by your target audience

**Recommended title:** "MachinaOS — Local AI Agent Orchestration for Developers"  
Or: "MachinaOS | Governed AI Workflow Automation, Local-First"

**Current H1:** "The First Intent-Driven Operating Layer"  
**Problem:** Marketing tagline, not keyword-relevant

**Recommended H1:** "MachinaOS — Local-First AI Agent Orchestration"  
Or keep the tagline but add an SEO-optimized subtitle visible below it

---

### M-2: Fix H1 Tags on Key Pages

| Page | Current H1 | Recommended H1 |
|---|---|---|
| /about.html | "The Age of Neural-Native Computing" | "About MachinaOS — Architecture and Roadmap" |
| /features.html | "Neural Architecture" | "MachinaOS Features — Governed AI Execution" |
| /pricing.html | "Neural Tiers" | "MachinaOS Pricing — Plans for Developers and Teams" |
| /demo-guide.html | "System Initialization" | "MachinaOS Setup Guide — Getting Started Locally" |
| /user-stories.html | "Real workflows, real execution" | Keep, or add "MachinaOS Use Cases" as subtitle |

---

### M-3: Expand Thin Content on Key Pages

Priority order:

**1. About page (~280 words → target 600+ words)**
- Add founding story / why MachinaOS was built
- Add team information (even pseudonymous handles help)
- Add the "Our Infrastructure" / "Our Stack" angle (what hardware, what models)
- Expand Engineering Principles section

**2. Features page (~235 words → target 800+ words)**
- Each of the 7 features deserves its own 100-word description
- Add technical detail: "how it works under the hood"
- Add code snippets or command examples

**3. Demo Guide (~210 words → target 1,000+ words)**
- This should be a genuine technical setup guide
- Add prerequisites, system requirements, installation commands
- Add screenshots from screens.html gallery
- Add troubleshooting section

**4. Homepage (~650 words → target 1,000+ words)**
- Add a "How MachinaOS compares" section
- Add a technical stack overview
- Add a "Who it's for" section with developer personas

---

### M-4: Optimize screens.html Images (Ordered by CWV Impact)

18 screenshots = entire site's CWV risk. Apply in this order:

**Step 1 — Add `width` and `height` to every `<img>` (CLS fix — highest priority):**
A single unsized image above the fold can produce CLS ≥ 0.15. With 18 images, cumulative CLS can exceed 0.25 (poor).

**Step 2 — Convert all PNGs to WebP** (60–80% size reduction for UI screenshots):
```bash
cwebp -q 85 screenshot-01.png -o screenshot-01.webp
```

**Step 3 — Correct lazy loading (do NOT lazy-load the first image):**
```html
<!-- First image: fetchpriority + preload in <head> -->
<link rel="preload" as="image" href="screenshot-01.webp" fetchpriority="high">
<img src="screenshot-01.webp" width="1280" height="800"
     fetchpriority="high" alt="MachinaOS main dashboard">

<!-- All subsequent images: lazy load -->
<img src="screenshot-02.webp" width="1280" height="800"
     loading="lazy" alt="MachinaOS settings panel">
```

**Step 4 — Add `srcset` for mobile** (serve smaller images on small screens):
```html
<img srcset="screenshot-01-800.webp 800w, screenshot-01-1280.webp 1280w"
     sizes="(max-width: 768px) 800px, 1280px"
     src="screenshot-01-1280.webp" width="1280" height="800"
     loading="lazy" alt="...">
```

**Also audit: font-display** — If using custom web fonts, add `font-display: swap` to prevent CLS from font reflow on every text page.

---

### M-5: Add Product Screenshots to Key Pages

The screens.html gallery is the only page with visual content. Consider adding:

- **Homepage**: 1–2 screenshots above/near the fold (hero section)
- **Features page**: 1 screenshot per feature showing it in action
- **User Stories page**: Workflow diagram or output screenshot per story
- **Demo Guide**: Screenshots of each setup step

This significantly improves E-E-A-T (shows the product exists), reduces bounce rate, and increases content depth.

---

### M-6: Add Social Media Profiles

No social media is linked from the homepage. For developer tools, this is a significant trust gap.

**Recommended immediate priority:**
1. **GitHub** — Essential for developer tool credibility. Even a public repo with a README builds trust.
2. **Twitter/X** — Developer community presence
3. **LinkedIn** — B2B trust signal

Add links to social profiles from footer + add `sameAs` to Organization schema.

---

### M-7: Add `rel="noopener noreferrer"` to Ecosystem Links + Request Inbound Link
**Affects:** /links.html  
**Fix:** Add `rel="noopener noreferrer"` to all 5 external ecosystem links on /links.html.

**More importantly:** Request that **machina-intelligence.com** add a prominent link pointing TO machinaos.ai. The parent company site is the highest-authority domain in the ecosystem — this inbound link is free and currently missing. One conversation, measurable impact on domain authority.

---

### M-8: Rename /links.html to /ecosystem.html

The URL `/links.html` is generic and weak for SEO. `/ecosystem.html` or `/related.html` is more descriptive.

If renamed, add 301 redirect: `/links.html` → `/ecosystem.html`

---

## LOW — Backlog

### M-9: Verify www vs Non-www Redirect
Both `https://machinaos.ai/` and `https://www.machinaos.ai/` should not both return 200. Configure nginx to 301-redirect one to the other consistently, then register only the canonical version in Google Search Console.

---

### M-10: Add HSTS and Security Headers in nginx
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```
Run `securityheaders.com` scan to verify after deployment.

---

## LOW — Backlog

### L-1: Start a Technical Blog or Docs Section
**Highest long-term SEO investment for a developer tool.**

Developer tools live and die on content. LangChain, AutoGen, and CrewAI have thousands of indexed documentation pages. Even 5–10 well-written blog posts on specific developer pain points ("Running LLMs locally with MachinaOS", "Governed AI workflows vs AutoGen") would build organic traffic.

Target topics:
- "How to run governed AI workflows locally with MachinaOS"
- "MachinaOS vs AutoGen: local-first orchestration compared"
- "Multi-agent AI coordination without cloud dependencies"
- "Intent-driven automation for developer environments"

---

### L-2: Create a GitHub Repository with Documentation
A public GitHub repo signals project legitimacy to developers and provides natural backlink opportunities. Many developer tools get discovered through GitHub search.

---

### L-3: Add Changelog Page
A `/changelog.html` page showing version history signals active development and provides freshness signals to search engines.

---

### L-4: Consider Extension-less URLs
Currently `/about.html`, `/features.html` etc. Consider migrating to `/about`, `/features` for cleaner URLs. Requires 301 redirects from `.html` versions. Low priority since `.html` URLs work fine for SEO.

---

### L-5: Submit to Developer Product Directories
For initial backlink acquisition and brand visibility:
- Product Hunt
- Hacker News (Show HN post)
- Dev.to article about MachinaOS
- Awesome lists on GitHub (e.g., "awesome-llm-apps")
- Y Combinator Startup Directory (if applicable)

---

## Priority Summary Dashboard

| # | Action | Priority | Effort | Impact |
|---|---|---|---|---|
| C-1 | Create robots.txt | 🔴 Critical | Low | High |
| C-2 | Create sitemap.xml | 🔴 Critical | Low | High |
| C-3 | Add canonical tags to all 9 pages | 🔴 Critical | Low | High |
| C-4 | Fix pricing page title (remove "Placeholder") | 🔴 Critical | Low | Medium |
| H-1 | Add meta descriptions to all 9 pages | 🟠 High | Low | High |
| H-2 | Set `<html lang="en">` on all pages | 🟠 High | Low | Low |
| H-3 | Add Organization + SoftwareApplication schema | 🟠 High | Low | High |
| H-4 | Add HowTo schema to demo guide | 🟠 High | Low | Medium |
| H-5 | Add BreadcrumbList schema to all pages | 🟠 High | Low | Medium |
| H-6 | Add OG + Twitter card tags | 🟠 High | Low | Medium |
| H-7 | Create llms.txt | 🟠 High | Low | Medium |
| H-8 | Add Privacy Policy + Terms pages | 🟠 High | Medium | High |
| M-1 | Optimize homepage title/H1 for keywords | 🟡 Medium | Low | High |
| M-2 | Fix H1 tags on key pages | 🟡 Medium | Low | Medium |
| M-3 | Expand thin content (about, features, demo guide) | 🟡 Medium | High | High |
| M-4 | Optimize screens.html images (WebP, lazy load) | 🟡 Medium | Medium | Medium |
| M-5 | Add product screenshots to key pages | 🟡 Medium | Medium | High |
| M-6 | Add social media profiles | 🟡 Medium | Medium | High |
| M-7 | nofollow ecosystem links | 🟡 Medium | Low | Low |
| M-8 | Rename /links.html to /ecosystem.html | 🟡 Medium | Low | Low |
| L-1 | Start technical blog / docs | 🔵 Low | High | Very High |
| L-2 | Create GitHub repository | 🔵 Low | Medium | High |
| L-3 | Add changelog page | 🔵 Low | Low | Medium |
| L-4 | Migrate to extension-less URLs | 🔵 Low | Medium | Low |
| L-5 | Submit to developer directories | 🔵 Low | Medium | High |

---

## Projected Score After Critical + High Fixes

| Category | Current | After Fixes | Delta |
|---|---|---|---|
| Technical SEO | 20 | 62 | +42 |
| Content Quality | 30 | 38 | +8 |
| On-Page SEO | 38 | 65 | +27 |
| Schema | 0 | 55 | +55 |
| Performance | 72 | 78 | +6 |
| Images | 55 | 58 | +3 |
| AI Search Readiness | 15 | 52 | +37 |
| **Overall** | **31** | **56** | **+25** |

After Medium fixes (especially content expansion and social profiles): ~**65/100**

---

*Action Plan generated by Claude SEO Audit System | machinaos.ai | 2026-03-31*
