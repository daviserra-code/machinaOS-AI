# Action Plan — machinaos.ai
**Based on:** Full SEO Audit, May 4, 2026
**Overall Score:** 70/100 (was 31/100 on March 31, +39 in 34 days)
**Goal:** Reach 82+ within 14 days (fix Critical + High issues)

---

## Priority Matrix

| ID | Issue | Priority | Effort | Impact | Pages |
|---|---|---|---|---|---|
| C-1 | `og:image` / `twitter:image` empty on all pages | CRITICAL | Low | High | 9/9 |
| C-2 | `SoftwareApplication` schema missing `image` | CRITICAL | Low | High | `/` |
| H-1 | Heading hierarchy skips H2 (H1 → H3) | HIGH | Low | Medium | 7/9 |
| H-2 | Sitemap `lastmod` stale (35 days) | HIGH | Low | Medium | sitemap.xml |
| H-3 | Empty `<img src="">` element | HIGH | Low | Low | `/screens.html` |
| H-4 | No `width`/`height` on images → CLS risk | HIGH | Low | High | `/screens.html`, `/links.html` |
| H-5 | Enterprise `Offer` missing `price` | HIGH | Low | Medium | `/` |
| M-1 | `HowTo` schema missing on demo guide | MEDIUM | Low | Medium | `/demo-guide.html` |
| M-2 | `ContactPage` schema missing | MEDIUM | Low | Low | `/contact.html` |
| M-3 | `AboutPage` + founder `Person` schema missing | MEDIUM | Medium | Medium | `/about.html` |
| M-4 | No FAQ section / `FAQPage` schema anywhere | MEDIUM | Medium | Medium | features, about |
| M-5 | Thin content on 5 pages | MEDIUM | Medium | Medium | demo-guide, screens, about, contact, links |
| M-6 | No contextual in-prose internal linking | MEDIUM | Low | Medium | features, user-stories |
| M-7 | Convert PNG screenshots to WebP/AVIF | MEDIUM | Medium | Medium | `/screens.html` |
| L-1 | No founder/author Person on any page | LOW | Medium | Medium | About |
| L-2 | Self-host favicons (currently Google service) | LOW | Low | Low | `/links.html` |
| L-3 | Re-evaluate Google-Extended block post-launch | LOW | n/a | Strategic | robots.txt |
| L-4 | Add security headers at the host | LOW | Low | Low | site-wide |

---

## Week 1 — Critical & High (Days 1-7)

### Day 1: Social/AI preview image (C-1)

Create one shared 1200×630 PNG hero image (logo + tagline "MachinaOS — Local-First Intent Runtime"). Save as `assets/og/og-default.png`. Then add to every page `<head>`:

```html
<meta property="og:image" content="https://machinaos.ai/assets/og/og-default.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="MachinaOS — Local-First Intent Runtime for governed AI agent orchestration" />
<meta name="twitter:image" content="https://machinaos.ai/assets/og/og-default.png" />
```

**Verify:**
```powershell
$pages = @('','features.html','user-stories.html','demo-guide.html','screens.html','about.html','contact.html','links.html')
foreach ($p in $pages) {
  $html = (Invoke-WebRequest "https://machinaos.ai/$p" -UseBasicParsing).Content
  if ($html -notmatch 'og:image') { "MISSING og:image on /$p" }
}
```

Then validate previews at:
- https://www.opengraph.xyz/url/https%3A%2F%2Fmachinaos.ai
- https://cards-dev.twitter.com/validator

---

### Day 1: SoftwareApplication `image` and Enterprise `price` (C-2, H-5)

Update the `SoftwareApplication` JSON-LD on `index.html`:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://machinaos.ai/#software",
  "name": "MachinaOS",
  "image": "https://machinaos.ai/assets/og/og-default.png",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "softwareVersion": "0.2",
  "url": "https://machinaos.ai",
  "featureList": "https://machinaos.ai/features.html",
  "screenshot": "https://machinaos.ai/screens.html",
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "USD",
    "lowPrice": "0",
    "highPrice": "49",
    "offerCount": "3",
    "availability": "https://schema.org/PreOrder",
    "offers": [
      { "@type": "Offer", "name": "Free", "price": "0", "priceCurrency": "USD",
        "availability": "https://schema.org/PreOrder",
        "description": "Single local runtime, core tool registry, session memory, demo mode" },
      { "@type": "Offer", "name": "Intelligence", "price": "49", "priceCurrency": "USD",
        "availability": "https://schema.org/PreOrder",
        "description": "Multi-agent delegation, Visual Workflow Studio, Security Center, MCP, 7 LLM providers" },
      { "@type": "Offer", "name": "Enterprise", "price": "0", "priceCurrency": "USD",
        "availability": "https://schema.org/PreOrder",
        "priceSpecification": { "@type": "PriceSpecification", "price": "0", "priceCurrency": "USD",
          "valueAddedTaxIncluded": false },
        "description": "Distributed agent mesh, security policy templates, contact sales for pricing" }
    ]
  },
  "publisher": { "@id": "https://machinaos.ai/#organization" }
}
```

(`price: "0"` on Enterprise + `description: "contact sales for pricing"` is the standard pattern Google accepts for "contact for quote" tiers.)

Validate at: https://validator.schema.org/ and https://search.google.com/test/rich-results.

---

### Day 2: Heading hierarchy (H-1)

For each of the 7 affected pages (`features`, `user-stories`, `demo-guide`, `about`, `contact`, `links`, `pricing`), promote the section-heading H3s to H2. Subsection H3s remain H3.

Example — `features.html`:
- Currently: `<h1>NeuralArchitecture</h1>` then 36 `<h3>` of mixed weight.
- Fix: identify the ~4–6 top-level section labels (e.g., "Planning", "Policy", "Execution", "Observability") and change those `<h3>` → `<h2>`. Leave the 30+ feature-detail headings as `<h3>`.

`screens.html` has zero section headings — add `<h2>Core controls</h2>`, `<h2>Agent automation</h2>`, `<h2>Insights & observability</h2>` above the existing image groups.

**Verify:**
```powershell
foreach ($p in 'features.html','user-stories.html','demo-guide.html','about.html','contact.html','links.html','pricing.html','screens.html') {
  $html = (Invoke-WebRequest "https://machinaos.ai/$p" -UseBasicParsing).Content
  $h2 = ([regex]::Matches($html, '<h2')).Count
  "$p  h2=$h2"
}
```
Expected: every page reports `h2 >= 2`.

---

### Day 2: Sitemap freshness (H-2)

Update `sitemap.xml` so `lastmod` reflects the *actual* most recent change per URL. If pages have not changed since 2026-03-31, leave them; if they have, set to today (2026-05-04). Ideally automate this in your build pipeline (file mtime → `lastmod`).

Also bump `lastmod` for any page whose markup changes as a result of the fixes in this action plan.

After deployment, resubmit the sitemap in Google Search Console.

---

### Day 3: Image dimensions + broken image (H-3, H-4)

`screens.html`:
1. Remove the orphan `<img src="" alt="">` at the end of the gallery.
2. For every screenshot, capture intrinsic dimensions and add `width`/`height` attributes:

```html
<img src="assets/screens/core/system-settings.png"
     alt="MachinaOS system settings interface"
     width="1600" height="900"
     loading="lazy" decoding="async" />
```

PowerShell to extract real dimensions:
```powershell
Add-Type -AssemblyName System.Drawing
Get-ChildItem "path\to\assets\screens\*.png" -Recurse | ForEach-Object {
  $img = [System.Drawing.Image]::FromFile($_.FullName)
  "{0} {1} {2}" -f $_.Name, $img.Width, $img.Height
  $img.Dispose()
}
```

`links.html`: favicon images are 32×32 — add `width="32" height="32"` to all 5.

---

## Week 2 — Medium Priority (Days 8-14)

### M-1: HowTo schema on demo guide

The page already has 5 ordered steps. Wrap them in `HowTo` JSON-LD:

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Set up MachinaOS local runtime",
  "description": "Activate the MachinaOS runtime, register a workspace, apply a policy profile, and run your first inspectable plan.",
  "totalTime": "PT15M",
  "tool": [{ "@type": "HowToTool", "name": "MachinaOS runtime 0.2+" }],
  "step": [
    { "@type": "HowToStep", "position": 1, "name": "Start the runtime",
      "text": "Launch the MachinaOS runtime from the system tray or CLI; verify the local socket is bound." },
    { "@type": "HowToStep", "position": 2, "name": "Register a workspace",
      "text": "Point MachinaOS at your project directory; the workspace registry indexes available tools." },
    { "@type": "HowToStep", "position": 3, "name": "Apply a policy profile",
      "text": "Choose a built-in policy profile (read-only, sandbox, full) or define a custom approval gate." },
    { "@type": "HowToStep", "position": 4, "name": "Run your first plan",
      "text": "Submit a natural-language goal; review the proposed plan in the inspector before approval." },
    { "@type": "HowToStep", "position": 5, "name": "Inspect the timeline",
      "text": "Open the event timeline to audit each tool call, output, and approval decision." }
  ]
}
```

### M-2: ContactPage schema

Add to `contact.html` `<head>`:
```json
{
  "@context": "https://schema.org",
  "@type": "ContactPage",
  "name": "Contact MachinaOS",
  "url": "https://machinaos.ai/contact.html",
  "mainEntity": { "@id": "https://machinaos.ai/#organization" }
}
```

### M-3 + L-1: AboutPage + founder Person

Pre-requisite: publish a 2-paragraph founder bio on `about.html` with a real name and link to LinkedIn.

```json
{
  "@context": "https://schema.org",
  "@type": "AboutPage",
  "name": "About MachinaOS",
  "url": "https://machinaos.ai/about.html",
  "mainEntity": {
    "@type": "Organization",
    "@id": "https://machinaos.ai/#organization",
    "founder": {
      "@type": "Person",
      "name": "<FOUNDER NAME>",
      "url": "https://www.linkedin.com/in/<handle>",
      "jobTitle": "Founder",
      "worksFor": { "@id": "https://machinaos.ai/#organization" }
    }
  }
}
```

### M-4: FAQ section + FAQPage schema

Add a 6-question FAQ at the bottom of `features.html` answering the likely "what is", "how does it differ from", and "what does X mean" questions:

- What does "intent-native" mean?
- How is MachinaOS different from LangChain / AutoGen / CrewAI?
- Does MachinaOS run fully locally?
- Which LLM providers does MachinaOS support?
- What is the policy gate / approval system?
- Is MachinaOS open source?

Wrap in `FAQPage` JSON-LD. Also add 3-question FAQ to `about.html` (company-level questions).

### M-5: Content depth

| Page | Current | Target | Action |
|---|---|---|---|
| `/demo-guide.html` | 287 | 600 | Add a "Prerequisites", "Troubleshooting", and "What's next" section |
| `/about.html` | 326 | 600 | Add founder paragraph (M-3), product origin story, roadmap teaser |
| `/screens.html` | 123 | 300 | Add intro paragraph per section (Core / Automation / Insights) |
| `/contact.html` | 136 | 250 | Add response-time expectations, separate sales/support/careers pathways |
| `/links.html` | 142 | 300 | Add 1-sentence description per linked product |

### M-6: Contextual in-prose links

Audit `features.html` and `user-stories.html` for unlinked mentions of sibling pages and add inline `<a>` tags. Examples:

- features.html mentions "real-world workflows" → link to `/user-stories.html`
- features.html mentions "screens" or "interface" → link to `/screens.html`
- user-stories.html mentions specific features → link to the relevant section anchor in `/features.html`
- about.html mentions "Machina Intelligence" → link to `https://machina-intelligence.com` (already external in nav, but reinforce in body)

### M-7: WebP/AVIF conversion for screens

```powershell
# Requires cwebp.exe in PATH
Get-ChildItem "assets\screens\*.png" -Recurse | ForEach-Object {
  $out = $_.FullName -replace '\.png$', '.webp'
  cwebp -q 85 $_.FullName -o $out
}
```

Then in `screens.html` use `<picture>`:
```html
<picture>
  <source srcset="assets/screens/core/system-settings.webp" type="image/webp" />
  <img src="assets/screens/core/system-settings.png"
       alt="MachinaOS system settings interface"
       width="1600" height="900" loading="lazy" decoding="async" />
</picture>
```

Expected savings: ~70 % file-size reduction across 22 PNGs.

---

## Backlog (post-launch / strategic)

| ID | Item | Trigger to revisit |
|---|---|---|
| L-2 | Self-host the 5 favicons in `/links.html` (10 KB total) | Anytime |
| L-3 | Re-evaluate `Google-Extended: Disallow` in robots.txt — currently blocks Gemini grounding | When AI surface visibility becomes a lead-gen priority |
| L-4 | Add CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy at the host (Netlify/Vercel/Cloudflare) | Anytime, low effort |
| L-5 | Publish a public changelog / roadmap page | When v0.3 ships |
| L-6 | Add `aggregateRating` to `SoftwareApplication` | When you have ≥5 verifiable reviews (G2, Capterra, Product Hunt) |
| L-7 | Expand `llms.txt` with a "vs LangChain / AutoGen / CrewAI" comparison block | Anytime — high-leverage for AI assistants |

---

## Score Projection

| Milestone | Score | Actions Completed |
|---|---|---|
| Mar 31 (baseline) | 31/100 | — |
| **May 4 (current)** | **70/100** | March 31 critical fixes shipped |
| After Week 1 | ~78/100 | C-1, C-2, H-1, H-2, H-3, H-4, H-5 |
| After Week 2 | ~83/100 | + M-1 to M-7 |
| With founder bio + FAQ depth (Week 3-4) | ~86/100 | + L-1 |
| Long-term ceiling (current 9-page footprint) | ~90/100 | Reviews + changelog + content depth |

The remaining ~10 points to reach 100/100 require organic signals that come with launch and use: real customer logos, third-party reviews, backlinks, indexed search traffic, blog/changelog cadence.

---

## Verification Checklist (Run After Each Fix)

```powershell
# C-1: og:image present
foreach ($p in '','features.html','user-stories.html','demo-guide.html','screens.html','about.html','contact.html','links.html') {
  $html = (Invoke-WebRequest "https://machinaos.ai/$p" -UseBasicParsing).Content
  if ($html -notmatch 'og:image') { "FAIL og:image: /$p" } else { "OK   og:image: /$p" }
}

# C-2 + H-5: SoftwareApplication has image and complete offers
$html = (Invoke-WebRequest "https://machinaos.ai/" -UseBasicParsing).Content
if ($html -match '"@type":\s*"SoftwareApplication"' -and $html -match '"image"') { "OK SoftwareApplication.image" }

# H-1: every page has at least 2 H2s
foreach ($p in 'features.html','user-stories.html','demo-guide.html','about.html','contact.html','links.html','pricing.html','screens.html') {
  $html = (Invoke-WebRequest "https://machinaos.ai/$p" -UseBasicParsing).Content
  $h2 = ([regex]::Matches($html, '<h2[\s>]')).Count
  if ($h2 -lt 2) { "FAIL h2($h2): /$p" } else { "OK   h2($h2): /$p" }
}

# H-2: sitemap lastmod current
(Invoke-WebRequest "https://machinaos.ai/sitemap.xml" -UseBasicParsing).Content | Select-String '<lastmod>(.*?)</lastmod>'

# H-3 + H-4: no empty img src on screens, all imgs have width/height
$html = (Invoke-WebRequest "https://machinaos.ai/screens.html" -UseBasicParsing).Content
if ($html -match 'src=""') { "FAIL empty img on /screens.html" }
$imgs = [regex]::Matches($html, '<img[^>]*>')
$missing = ($imgs | Where-Object { $_.Value -notmatch 'width=' -or $_.Value -notmatch 'height=' }).Count
"imgs without dims on /screens.html: $missing"

# M-1: HowTo on demo guide
(Invoke-WebRequest "https://machinaos.ai/demo-guide.html" -UseBasicParsing).Content -match '"@type":\s*"HowTo"'
```

---

*Action plan generated 2026-05-04 from the Full SEO Audit. Update progress weekly. Re-audit recommended on 2026-05-31.*
