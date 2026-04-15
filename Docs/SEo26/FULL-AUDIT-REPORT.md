# Full SEO Audit Report — machinaos.ai
**Audit Date:** 2026-03-31  
**Audited URL:** https://machinaos.ai  
**Business Type:** B2B SaaS / Developer Tool — Pre-launch AI orchestration product (static HTML site, 9 pages)  
**Auditor:** Claude SEO Audit System  
**Related site:** ai-radar.it (same owner ecosystem — machina-intelligence.com)

---

## Executive Summary

### Overall SEO Health Score: 31 / 100 🔴 Critical

| Category | Weight | Raw Score | Weighted Score |
|---|---|---|---|
| Technical SEO | 25% | 20/100 | 5.0 |
| Content Quality | 25% | 30/100 | 7.5 |
| On-Page SEO | 20% | 38/100 | 7.6 |
| Schema / Structured Data | 10% | 0/100 | 0.0 |
| Performance (CWV) | 10% | 72/100 | 7.2 |
| Images | 5% | 55/100 | 2.75 |
| AI Search Readiness | 5% | 15/100 | 0.75 |
| **TOTAL** | **100%** | | **30.8 / 100** |

> **Context:** This score reflects a pre-launch product site that has focused on product design over search infrastructure. The good news: the site's static HTML foundation makes fixes fast and cheap. Almost every issue here is a missing element rather than something broken that needs reconstruction.

### Business Type Detected
Pre-launch B2B SaaS / developer tool. MachinaOS is a local-first AI orchestration layer — an "intent-native shell" that routes natural-language goals into governed, multi-step agentic workflows. Product appears to be in late alpha / early beta (pricing explicitly labeled "placeholder"). Target audience: developers, engineering teams, tech leads, consultants running AI automation locally.

**Parent company:** machina-intelligence.com  
**Ecosystem:** ai-radar.tech, shopfloor-copilot.com, teyra.it, fantacalcioai.it

### Top 5 Critical Issues

1. **No robots.txt** — Returns 404. Search engines have no instructions; crawl budget and blocking rules are undefined.

2. **No sitemap.xml** — Returns 404. Google must discover all pages by crawling alone — unreliable for a small static site.

3. **Zero schema markup across all 9 pages** — No Organization, no SoftwareApplication, no BreadcrumbList. No rich result eligibility anywhere.

4. **No canonical URLs on any page** — Both `/` and `/index.html` likely return 200 for the same content with no canonical to resolve the duplicate. No other page has a canonical tag.

5. **No meta descriptions on any page** — Google will generate its own snippets from page content, which for thin pages (150–300 words) will be low quality.

### Top 5 Quick Wins

1. **Create robots.txt + sitemap.xml** — 30-minute fix that immediately tells Google about all 9 pages. The two most impactful technical changes available.

2. **Add `<link rel="canonical">` to every page** — Self-referencing canonicals resolve the `/` vs `/index.html` duplicate and future-proof all pages. One line per page template.

3. **Add meta descriptions to all 9 pages** — Direct CTR improvement. Each page needs one unique 150-char description.

4. **Add Organization + SoftwareApplication schema to homepage** — Unlocks Knowledge Panel eligibility and product rich results. Under 1 hour to implement.

5. **Set `<html lang="en">` on all pages** — One attribute, affects accessibility and search language targeting across the entire site.

---

## 1. Technical SEO

### 1.1 robots.txt — Score: 0/100 (MISSING)

**Status: CRITICAL — File returns 404**

Without robots.txt:
- Crawlers fall back to their defaults (crawl everything accessible)
- No crawl-delay guidance (can cause server load spikes)
- No sitemap declaration
- No blocking of non-content paths (if any exist)
- Minor perception issue: Google expects this file to exist

**Recommended robots.txt:**
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

# AI search indexing — allow for discovery traffic
User-agent: PerplexityBot
Allow: /

User-agent: ChatGPT-User
Allow: /
```

### 1.2 Sitemap — Score: 0/100 (MISSING)

**Status: CRITICAL — sitemap.xml returns 404**

For a 9-page static site, a missing sitemap means Google must discover pages through crawling internal links only. If any page is orphaned (not linked from another page), it will never be found.

**All 9 pages confirmed accessible via crawl:**
- / (homepage)
- /about.html
- /features.html
- /pricing.html
- /user-stories.html
- /demo-guide.html
- /screens.html
- /contact.html
- /links.html

**Recommended sitemap.xml** — see ACTION-PLAN.md for full XML template.

### 1.3 Canonical URL Issues — Score: 15/100

**Critical: / and /index.html both return 200 with same content**

Static HTML servers typically serve both `https://machinaos.ai/` and `https://machinaos.ai/index.html`. Without a canonical tag, Google must choose one to index — and may split link equity between both.

**No canonical tags exist on any of the 9 pages.**

**Fix:** Add self-referencing canonical to every page:
```html
<!-- On / (homepage) -->
<link rel="canonical" href="https://machinaos.ai/" />

<!-- On /about.html -->
<link rel="canonical" href="https://machinaos.ai/about.html" />
```

**Additional issue:** Navigation links use relative `.html` paths (`href="about.html"`). This works but means internal links look like `about.html` not `/about.html`. Canonicals must use absolute URLs.

### 1.4 URL Structure — Score: 65/100

**Static .html extension URLs:**
- Functionally sound — all pages return 200
- SEO neutral — Google indexes `.html` URLs without penalty
- Minor concern: some modern sites prefer extension-less clean URLs (`/about` vs `/about.html`)
- If migrating to extension-less URLs in future, 301 redirects from `.html` versions are required

**URL quality assessment:**
- `/about.html` — clear, descriptive ✅
- `/features.html` — clear ✅
- `/user-stories.html` — clear, keyword-relevant ✅
- `/demo-guide.html` — clear ✅
- `/pricing.html` — clear ✅
- `/screens.html` — acceptable (could be `/gallery.html` or `/screenshots.html` for clarity)
- `/links.html` — weak (this is an ecosystem/related-products page; `/ecosystem.html` would be more descriptive)

### 1.5 Missing Meta Tags — Score: 10/100

| Tag | Status | Impact |
|---|---|---|
| Meta description | 🔴 Missing on ALL 9 pages | High — Google generates low-quality snippets |
| `<html lang="">` | 🔴 Not set on any page | Medium — accessibility + language targeting |
| OG title / description / image | 🔴 Missing on all pages | Medium — social sharing unfurls will be poor |
| Twitter card | 🔴 Missing on all pages | Low-Medium — Twitter/X share previews |
| Viewport meta | Unknown | Should be set for mobile |

### 1.6 HTTPS & Security

- HTTPS confirmed (all URLs served over https://)
- Security headers not measurable via crawl — run `securityheaders.com` scan
- Static site likely has fewer attack surfaces than dynamic sites

### 1.7 International SEO

- Single language (English) — no hreflang needed ✅
- `<html lang="en">` must be set for screen readers and language inference

### 1.8 Internal Linking — Score: 60/100

**Strengths:**
- All 9 pages are interlinked via the consistent navigation menu
- Footer mirrors navigation — every page is reachable from every other page
- No orphaned pages (all pages linked from nav)

**Weaknesses:**
- Navigation links use relative paths (`about.html`) — canonical/absolute form preferred in `<link>` tags
- No in-content contextual links between pages (e.g., user-stories.html doesn't link to features.html)
- /links.html outbound links to 5 related ecosystem sites — none have `rel="nofollow"` (minor)

---

## 2. Content Quality

### 2.1 E-E-A-T Assessment — Score: 18/100 (Low Quality per September 2025 QRG)

This is a pre-launch product with significant trust signal deficits.

| Signal | Status | Notes |
|---|---|---|
| Named founders/team | 🔴 Missing | No person mentioned anywhere |
| Author credentials | 🔴 Missing | No bios, no LinkedIn, no GitHub |
| Company details | ⚠️ Partial | machina-intelligence.com referenced |
| About page | 🔴 Weak | ~280 words, no team, no founding story |
| Contact info | ✅ Present | 4 email addresses across roles |
| Physical address | 🔴 Missing | No location |
| Social media | 🔴 Missing | No Twitter/X, LinkedIn, GitHub linked from homepage |
| External mentions | Unknown | No press links visible |
| Product reviews | 🔴 Missing | Pre-launch |
| Trust badges | 🔴 Missing | No certifications, no security audits |
| Privacy policy | 🔴 Missing | Not found in crawl |
| Terms of service | 🔴 Missing | Not found in crawl |

**For a developer tool targeting engineering teams**, the complete absence of named founders is a significant trust gap. Developers evaluate tools in part through the team behind them.

### 2.2 Content Depth by Page

| Page | Words | Assessment |
|---|---|---|
| Homepage | ~650 | Thin for a product homepage |
| /about.html | ~280 | Very thin — about pages need 500+ words min |
| /features.html | ~235 | Very thin — each feature deserves 100+ words |
| /demo-guide.html | ~210 | Very thin — a real guide needs 800+ words |
| /user-stories.html | ~1,150 | Best page — good depth |
| /screens.html | ~220 | Gallery page — acceptable given 18 images |
| /pricing.html | ~200 | Thin + explicitly "placeholder" |
| /contact.html | ~155 | Thin — acceptable for contact pages |
| /links.html | ~180 | Thin — acceptable as an index page |

**Average across non-contact/links pages: ~420 words** — well below competitive developer tool sites which typically have 1,000–3,000 words per key page.

### 2.3 Placeholder Pricing Page — Special Risk

The pricing page title explicitly includes "Placeholder Tiers Preview." This creates several risks:
1. **Trust erosion**: Users who find this page via search discover the product isn't ready
2. **Thin content**: 200 words, all placeholder
3. **CTR impact**: If "Placeholder" appears in a SERP snippet, click-through rate plummets

**Recommendation:** Either remove from Google's index (`noindex`) until finalized, or replace title with the actual product name and add substantive feature comparison content.

### 2.4 Missing Content for Developer Tool SEO

Developer tools compete heavily on content. The site is missing:

| Missing Content | SEO Value |
|---|---|
| Technical blog / changelog | High — organic discovery, E-E-A-T, backlinks |
| Getting started guide (full) | High — "how to" queries, long-tail |
| API/SDK documentation | High — developer trust, technical SEO |
| Comparison pages ("MachinaOS vs AutoGen") | High — bottom-funnel queries |
| Integration guides (Ollama, LM Studio, etc.) | High — long-tail technical queries |
| Use case deep-dives | Medium |
| Changelog / release notes | Medium — freshness signals |

### 2.5 Target Keyword Opportunities

Given the product concept, the following query categories are underaddressed:

| Query Category | Example | Competition |
|---|---|---|
| Local AI orchestration | "local LLM orchestration", "on-premise AI agent framework" | Medium |
| AI workflow automation | "AI task automation local", "agentic workflow tool" | Medium-High |
| Intent-driven AI | "intent-based AI execution", "governed AI workflows" | Low (emerging) |
| Developer AI tools | "AI developer tools 2026", "LLM workflow tool" | High |
| Alternatives | "AutoGen alternative", "LangChain alternative local" | High |

### 2.6 AI Citation Readiness — Score: 15/100

| Signal | Status |
|---|---|
| Named authors / experts | 🔴 Absent |
| Structured technical content | ⚠️ Minimal |
| Factual claims with evidence | 🔴 Absent |
| llms.txt | 🔴 Missing |
| Schema markup | 🔴 None |
| External citations of the site | Unknown (pre-launch) |
| Clear unique value proposition | ✅ Present |

---

## 3. On-Page SEO

### 3.1 Title Tag Analysis

| Page | Title | Length | Quality |
|---|---|---|---|
| Homepage | "MachinaOS \| Local-First Intent Runtime" | ~40 chars | ⚠️ Weak — "Intent Runtime" not a searched phrase |
| /about.html | "About MachinaOS \| Architecture and Roadmap" | ~43 chars | ⚠️ Misses keywords |
| /features.html | "MachinaOS Features \| Planning, Policy, Execution" | ~49 chars | ✅ Adequate |
| /pricing.html | "MachinaOS Pricing \| Placeholder Tiers Preview" | ~47 chars | 🔴 "Placeholder" in title is harmful |
| /user-stories.html | "MachinaOS User Stories \| Real Workflows, Real Execution" | ~56 chars | ✅ Good |
| /demo-guide.html | "MachinaOS Demo Guide \| Local Runtime Setup" | ~43 chars | ✅ Good |
| /screens.html | "MachinaOS Screens \| Runtime Interface Gallery" | ~47 chars | ⚠️ "Screens" is weak; "Screenshots" or "Interface" better |
| /contact.html | "Contact MachinaOS \| Support, Sales, Careers" | ~44 chars | ✅ Good |
| /links.html | "MachinaOS Ecosystem \| Related Products and Platforms" | ~53 chars | ✅ Acceptable |

**Priority title fix:** Homepage title "Local-First Intent Runtime" is not a phrase developers search for. Consider: "MachinaOS — AI Agent Orchestration for Local Workflows" or "MachinaOS | Local AI Workflow Automation Tool".

### 3.2 H1 Analysis

| Page | H1 | Assessment |
|---|---|---|
| Homepage | "The First Intent-Driven Operating Layer" | ⚠️ Marketing copy, not keyword-optimized |
| /about.html | "The Age of Neural-Native Computing" | 🔴 Describes a concept, not the page |
| /features.html | "Neural Architecture" | 🔴 Too vague — no product name or benefit |
| /pricing.html | "Neural Tiers" | 🔴 Non-descriptive; should say "MachinaOS Pricing" |
| /user-stories.html | "Real workflows, real execution" | ⚠️ Marketing tagline, not keyword |
| /demo-guide.html | "System Initialization" / "Activation Protocol" | 🔴 Jargon — not a searcher's language |
| /screens.html | "MachinaOS Screens" / "Visual Library" | ⚠️ Acceptable but weak |
| /contact.html | "Get in Touch" | ✅ Conventional, acceptable |

**Pattern:** The site uses evocative marketing language ("Neural-Native Computing", "Neural Architecture", "Activation Protocol") rather than descriptive, searchable language. This is a consistent on-page SEO weakness.

### 3.3 Heading Structure Quality

- All pages appear to use a single H1 ✅ (no double H1 issues)
- H2/H3 hierarchy present on most pages ✅
- H3 headings on homepage ("Heuristic Intent Router", "Planner and Executor Split") are technical and descriptive ✅

---

## 4. Schema & Structured Data

### 4.1 Current Implementation

**Score: 0/100 — Literally zero schema on the entire site.**

No JSON-LD, no microdata, no RDFa on any of the 9 pages.

### 4.2 Priority Schema to Add

| Schema Type | Page | Impact | Notes |
|---|---|---|---|
| `Organization` | Homepage | High — Knowledge Panel | Include `@id`, `parentOrganization`, all emails |
| `SoftwareApplication` | Homepage | High — Product rich results | Use `PreOrder` availability pre-launch |
| `WebSite` | Homepage | Medium — Sitelinks search | |
| `BreadcrumbList` | All inner pages | Medium — SERP breadcrumbs | Two-item list: Home → Page |
| `WebPage` | /demo-guide.html, /features.html | Medium | Generic context for crawlers |
| `AboutPage` | /about.html | Medium — E-E-A-T | |
| `ContactPage` | /contact.html | Low | |
| `ImageGallery` + `ImageObject` | /screens.html | Medium | |

**Schema types confirmed NOT to add:**

| Type | Reason |
|---|---|
| `HowTo` | ❌ Removed from Google Search permanently — September 2023 |
| `FAQPage` | ❌ Restricted to government/healthcare — August 2023 |
| `Product` | ❌ Use `SoftwareApplication` instead |
| `AggregateRating` | ❌ Policy violation pre-launch; add only after real reviews |
| `Dataset` | ❌ Rich results retired by Google — late 2025 |

> **Pre-launch rule:** All `Offer` objects in `SoftwareApplication` must use `"availability": "https://schema.org/PreOrder"`. Change to `InStock` at launch. Do NOT fabricate prices that aren't displayed on the page.

See ACTION-PLAN.md for full JSON-LD templates.

---

## 5. Performance

### 5.1 Assessment

Static HTML = inherently good performance baseline. No JavaScript frameworks, no CMS, no server-side processing.

| Metric | Risk Level | Primary Driver |
|---|---|---|
| LCP | LOW | Static HTML, minimal images |
| INP | VERY LOW | No complex JavaScript interactions |
| CLS | LOW-MEDIUM | screens.html images (if undimensioned) |
| TTFB | VERY LOW | Static file serving |

### 5.2 Only Performance Risk: screens.html Images

The screens page has ~18 product screenshots. Estimated grade **C–D if unoptimized, A–B if optimized**.

| Risk | Impact | Fix |
|---|---|---|
| No `width`/`height` on `<img>` tags | CLS HIGH — 18 layout shifts accumulating | Add explicit dimensions to every img |
| Full-resolution PNG format | LCP HIGH — each PNG could be 500KB–2MB | Convert all to WebP (60–80% smaller) |
| No lazy loading | LCP + load time HIGH | `loading="lazy"` on images 2–18 |
| No preload on LCP image | LCP MEDIUM | `fetchpriority="high"` + preload hint on image 1 |

**Critical nuance:** Do NOT add `loading="lazy"` to the first (above-fold) screenshot — this delays LCP. Only images 2–18 should be lazy-loaded.

```html
<!-- First image — no lazy, high priority -->
<img src="screenshot-01.webp" width="1280" height="800" fetchpriority="high" alt="...">
<link rel="preload" as="image" href="screenshot-01.webp" fetchpriority="high"> <!-- in <head> -->

<!-- All subsequent images — lazy load -->
<img src="screenshot-02.webp" width="1280" height="800" loading="lazy" alt="...">
```

### 5.2b Font Loading — CLS Risk on All Pages

If the site uses custom web fonts (Google Fonts, Adobe Fonts, or self-hosted) **without** `font-display: swap`, text renders in the fallback system font and reflows when the custom font loads — causing CLS across every page, not just screens.html.

**Fix:** Verify fonts are declared with `font-display: swap` in CSS. If system fonts only, this risk is zero.

### 5.3 Performance Advantages

- Static HTML: TTFB typically <100ms
- No JavaScript framework parse/execute overhead
- No third-party scripts (no badge embeds, no analytics confirmed)
- Small text payloads on all pages
- No external font CDNs detected
- **No JS rendering dependency** — all content in initial HTML response; Google's crawler doesn't need to queue for JS execution. This is a significant SEO advantage over React/Next.js/Vue sites.

**Overall: Performance is the site's strongest dimension.** Very low effort required.

---

## 6. Images

### 6.1 Coverage

| Page | Images | Alt Text |
|---|---|---|
| Homepage | None detected | N/A |
| /about.html | None detected | N/A |
| /features.html | None detected | N/A |
| /pricing.html | None detected | N/A |
| /user-stories.html | None detected | N/A |
| /demo-guide.html | None detected | N/A |
| /screens.html | ~18 screenshots | ✅ Descriptive alt text present |
| /contact.html | None detected | N/A |
| /links.html | None detected | N/A |

**screens.html alt text example:** "MachinaOS system settings interface", "MachinaOS workflow orchestration board" — good quality ✅

### 6.2 Missing Opportunities

- **Homepage**: No product screenshot or hero image — text-only above the fold is a conversion and SEO weakness
- **Features page**: Feature descriptions without supporting screenshots reduce engagement and SEO depth
- **User Stories page**: No workflow diagrams or output screenshots to support the use case claims
- **About page**: No team photos (even abstract/anonymous ones signal human presence)

---

## 7. AI Search Readiness

### 7.1 Score: 15/100

| Signal | Status |
|---|---|
| llms.txt | 🔴 Missing |
| robots.txt AI crawler rules | 🔴 robots.txt doesn't exist |
| Schema structured data | 🔴 None |
| Named experts | 🔴 None |
| Factual unique claims | ⚠️ Present but unsubstantiated |
| Clear topical focus | ✅ Strong (AI orchestration niche) |
| RSS/feeds | 🔴 None |
| Transparency/methodology page | 🔴 Missing |

### 7.2 llms.txt Recommendation

Create `https://machinaos.ai/llms.txt`:
```markdown
# MachinaOS

> Local-first intent runtime for governed AI agent orchestration.

## About
MachinaOS is an intent-native orchestration layer that routes natural-language goals
into structured, multi-step agentic workflows with human approval checkpoints.
Built for developers and engineering teams requiring traceable, local-first AI execution.

## Key Capabilities
- Heuristic intent routing
- Planner/executor separation
- Multi-agent delegation with scoped permissions
- Local memory layers
- Human approval gates for risky operations

## Resources
- Demo Guide: https://machinaos.ai/demo-guide.html
- Features: https://machinaos.ai/features.html
- User Stories: https://machinaos.ai/user-stories.html
- Pricing: https://machinaos.ai/pricing.html

## Parent Company
Machina Intelligence — https://machina-intelligence.com
```

---

## 8. Site Architecture

```
machinaos.ai/
├── index.html          (homepage — product overview)
├── features.html       (feature list)
├── user-stories.html   (9 use cases — best page)
├── demo-guide.html     (setup wizard)
├── screens.html        (product screenshots)
├── pricing.html        (placeholder tiers)
├── about.html          (architecture + roadmap)
├── contact.html        (email contacts)
└── links.html          (ecosystem)
```

**Assessment:** Clean and flat architecture — appropriate for a small product site. All pages are one click from the homepage. No depth issues.

**Missing structural elements:**
- No `/blog/` or `/docs/` section
- No legal pages (`/privacy`, `/terms`)
- No changelog (`/changelog`)
- No `sitemap.xml`
- No `robots.txt`

---

## 9. Competitive Context

MachinaOS competes in the AI developer tools space against:
- **LangChain** / **LangGraph** — dominant, massive content library
- **AutoGen** (Microsoft) — strong developer community
- **CrewAI** — growing open-source community
- **Ollama** — local LLM runtime (adjacent)
- **LM Studio** — local LLM GUI (adjacent)

All competitors have extensive documentation, blog content, GitHub presence, and community — none of which MachinaOS currently shows in its web presence. The "local-first, governed execution" angle is a genuine differentiator but is not visible in search results without content to surface it.

---

*Report generated by Claude SEO Audit System | machinaos.ai | 2026-03-31*
