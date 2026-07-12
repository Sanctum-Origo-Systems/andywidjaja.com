# Portfolio Site — Foundation Spec

## Vision

A personal portfolio site that showcases Patina and Autoloop by *being* the demonstration. Visitors submit feedback, the AI pipeline builds variant implementations, an LLM judge scores them, and the owner curates what ships to the main site. The entire process is visible as a live gallery.

**Thesis:** AI proposes, scores, and presents — human decides. Graduated autonomy in practice.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MAIN SITE (stable)                   │
│  Portfolio · Projects · About · Gallery · Suggest       │
└─────────────────────────────────────────────────────────┘
      │                                    ▲
      │ visitor submits feedback           │ owner adopts variant
      ▼                                    │
┌─────────────────────────────────────────────────────────┐
│                   FEEDBACK PIPELINE                     │
│                                                         │
│  Queue → Validate → Triage → Build → Score → Gallery    │
│                                                         │
│  - Validate: safety, relevance, not malicious           │
│  - Triage: size, feasibility, priority                  │
│  - Build: autoloop implements on a branch               │
│  - Score: LLM judge rates before/after                  │
│  - Gallery: screenshot + diff + score + verdict         │
└─────────────────────────────────────────────────────────┘
```

---

## Core Principles

1. **Main site is always stable** — variants never auto-deploy to production
2. **Transparency** — every step of the pipeline is visible to visitors
3. **Human curation** — owner reviews and decides what to keep
4. **Safety first** — malicious/injection feedback rejected with visible reasoning
5. **Self-referential** — the site demonstrates the tools it showcases

---

## Pages

### Home / Hero
- One-sentence thesis: "I build cognitive systems that learn users over time"
- One striking visual (belief graph, autonomy ladder, or pipeline diagram)
- Subtle "this site improves itself" indicator (e.g. "3 variants built this week")

### Projects
- **Patina** deep-dive: problem → architecture → key decisions → demo
- **Autoloop** deep-dive: "AI that ships features" → economics → success rate

### Gallery (the live demo)
- Carousel/grid of variant builds generated from visitor feedback
- Each variant shows:
- The original feedback request
- Screenshot of the variant (Playwright capture)
- Diff from main site
- LLM judge score (clarity, usability, aesthetics — 1-10 each)
- Owner verdict: adopted / declined (with visible reasoning) / pending
- Filter: all | adopted | declined | pending
- Timeline view: see the site evolve through adopted changes

**Transparency over polish:** Declined variants stay in the gallery with visible
reasoning (e.g. "declined: broke mobile layout", "declined: score 3/10 on clarity").
Failures are a feature — they show the human gate working, demonstrate taste and
judgment, and prove this is a real system with a real success/failure rate. Lab
engineers know real systems fail; showing the feedback loop that recovers from
failure is a stronger signal than a curated 100% success story.

### Suggest a Change
- Simple form: "What would you improve about this site?"
- Shows queue position and current status after submission
- Visible pipeline status: validating → triaged → building → scored → pending review

### Pipeline View (for technical visitors)
- Real-time view of the autoloop pipeline processing feedback
- Run history: success rate, cost per variant, average build time
- Protected paths list (what the AI can't touch)

---

## User Tiers

### Authenticated (GitHub OAuth)
- "Suggest a Change" creates a real GitHub issue under their account
- They receive progress notifications (triaged, built, scored, adopted/declined)
- Their avatar appears next to their suggestion in the gallery and pipeline view
- Higher rate limit: 5 submissions per day
- Can vote/react on other variants in the gallery
- Full participant in the pipeline — their identity is visible throughout

### Anonymous (no login)
- Can browse the full site, gallery, and pipeline view
- Can submit feedback via a simple text form (stored in local database, not GitHub)
- Lower rate limit: 2 submissions per IP per day
- No notifications — check back via the gallery to see status
- Shown as "Anonymous visitor" in the gallery
- Extra validation gate: owner or autoloop batch-reviews anonymous submissions and promotes worthy ones to GitHub issues before entering the build pipeline

### Incentive Design
- Clear CTA: "Log in with GitHub to track your suggestion in real-time"
- Anonymous feedback shows: "Pending promotion — log in for instant pipeline access"
- Targets the right audience: engineers (who have GitHub) get the full experience
- Casual visitors still engage without friction

### Privacy & Trust
- Request minimal OAuth scope: `read:user` only (username + avatar)
- No access to user's repositories, private data, or write permissions
- Issues are created on *our* repo, not theirs
- Explicit disclosure on the form: "We use GitHub login to create an issue on our repo under your name. No access to your repositories."
- OAuth consent screen (GitHub-controlled) clearly shows requested permissions
- Standard practice — same flow as Vercel, Railway, Netlify, Linear
- Users can revoke access anytime from GitHub Settings → Applications

---

## Feedback Pipeline Detail

### 1. Submission
- Text input (max 500 chars)
- Optional category: design / content / feature / bug
- **Authenticated:** creates GitHub issue directly, enters pipeline immediately
- **Anonymous:** stored in local database, enters a promotion queue
- Rate limits per tier (see User Tiers above)

### 2. Validation (LLM judge)
- Is this genuine feedback about the site? → accept
- Is this prompt injection / XSS / offensive? → reject with visible reason
- Is this asking for something impossible or out-of-scope? → reject with reason
- Verdict + reasoning stored and displayed publicly

### 3. Triage (autoloop)
- Size estimate (can this be done in one build cycle?)
- Feasibility check (does it target modifiable paths?)
- Protected paths check (core layout, pipeline config → needs-human)
- Creates a GitHub issue labeled `feedback`

### 4. Build (autoloop implement)
- Autoloop picks up the issue
- Implements on a feature branch
- Runs verification (tests, lint, build succeeds)
- Captures screenshot of the result (Playwright)

### 5. Score (LLM judge)
- Compares main site screenshot vs. variant screenshot
- Scores on:
- **Clarity** (1-10): is the content clearer?
- **Usability** (1-10): is it easier to navigate/use?
- **Aesthetics** (1-10): does it look better?
- **Fidelity** (1-10): does it match what was requested?
- Composite score + one-sentence rationale

### 6. Gallery + Owner Review
- Variant appears in gallery as "pending"
- Owner gets notification (email, push, or Patina catch-up)
- Owner actions: adopt (merge to main), decline (with reason), or defer
- Adopted variants update the main site on next deploy

---

## Tech Stack (recommended)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Frontend | Astro or Next.js | Static-first, fast, good DX |
| Styling | Tailwind + shadcn/ui | Polished look without a designer |
| Hosting | VPS (existing) or Vercel | Already have VPS for autoloop |
| Database | SQLite | Feedback queue, scores, verdicts |
| Screenshots | Playwright | Headless capture of variants |
| CI/CD | GitHub Actions | Branch previews, build verification |
| Pipeline | Autoloop | Triage + implement from feedback issues |
| Scoring | Claude API (Haiku) | Cheap per-judgment, good enough for scoring |

---

## Protected Paths

Autoloop cannot modify:
- `autoloop/`, `autoloop.toml` (pipeline infrastructure)
- Core layout components (header, footer, nav)
- Pipeline/scoring logic
- Authentication or rate-limiting code
- This spec

---

## Phased Rollout

### Phase 1: Polished Static Site
- Design and ship the main portfolio site
- Projects pages for Patina and Autoloop
- No dynamic features yet
- Deploy to existing domain

### Phase 2: Wire Up Autoloop
- Create the site's repo with autoloop init
- Set up feedback → GitHub issue pipeline
- Basic gallery page showing implemented variants (manual screenshots initially)

### Phase 3: Automated Scoring + Gallery
- Add Playwright screenshot capture
- Add LLM judge scoring
- Build the interactive gallery with filters and timeline
- Owner review notifications

### Phase 4: Public Launch
- Enable the "Suggest a Change" form
- Rate limiting and abuse prevention
- Pipeline view page for technical visitors
- Announce / share

---

## Success Metrics

- Visitors submit feedback (engagement)
- Variants get built successfully (pipeline reliability)
- Owner adopts some variants (quality of AI output)
- Technical visitors spend time on pipeline view (depth of interest)
- Site improves measurably over time (LLM scores trend upward)

---

## Resolved Questions

- **Domain:** andywidjaja.com (Route 53 DNS, Vercel hosting)
- **Deployment:** Live at https://andywidjaja.com (deployed 2026-07-11). Auto-deploys on push to main via Vercel.
- **HTTPS:** Automatic via Vercel. HSTS enabled. www redirects to apex.
- **Identity:** Personal brand (Andy Widjaja) — you're selling *you*, not just Patina
- **Scope:** Portfolio + projects now. Blog/essays after the paper lands (Q4)
- **Access:** Fully public for browsing. Auth only for feedback submission (Phase 4)
- **Cost cap:** $2-5/day max on Haiku scoring during active periods. Minimal when idle.

---

## Design & UX Spec (Phase 1 — Builder-Actionable)

### Target Audience

Top AI lab engineering staff (Anthropic, OpenAI, DeepMind, Mistral). The site
must signal "serious builder" within 3 seconds. Not a marketing site. Not a
designer portfolio. A builder's site that proves you ship production systems.

### Design Principles

1. **Dark mode default** — engineers live in dark terminals. Light mode available but not primary.
2. **Typography-first** — one excellent font family (Inter for body, JetBrains Mono for code). No hero images or stock photos.
3. **One live metric on hero** — not a wall of stats. One thing that makes them lean in (e.g. "151 PRs implemented autonomously · last run: 2h ago").
4. **Architecture diagrams over screenshots** — observer/builder diagram, feedback pipeline, dual belief graph. Excalidraw-style or clean SVG.
5. **Code is one click away** — every project section has a direct repo link. Open source = credibility.
6. **No "About Me" wall of text** — one line bio, then let projects speak.
7. **Sub-1-second load** — static HTML. No JavaScript framework overhead for what's essentially a document. Astro preferred.
8. **Monospace accents** — terminal-aesthetic touches (code blocks, system-style status indicators). Signals "one of us" to the target audience.

### What to Avoid

- ❌ Gradient hero backgrounds
- ❌ "Full-stack developer | Cloud architect | AI enthusiast" taglines
- ❌ Testimonials or endorsements
- ❌ Career timeline (that's LinkedIn)
- ❌ Animated counters or scroll-triggered effects
- ❌ "Let's connect" CTAs
- ❌ Any mention of Amazon/AWS branding
- ❌ Stock photography or decorative illustrations

### Layout Spec

```
┌─────────────────────────────────────────────────────┐
│  Andy Widjaja                          [GitHub] [→] │  nav: name + one link only
├─────────────────────────────────────────────────────┤
│                                                     │
│  I build AI systems that improve                    │  one sentence, large, centered
│  themselves under human oversight.                  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  [live] 151 PRs merged autonomously           │  │  one real-time stat, monospace
│  │  last run: 2h ago · 0 human interventions     │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  PATINA                                  [repo →]   │
│  Cognitive AI that learns your judgment             │
│  ┌───────────────────────────────────────────────┐  │
│  │  [observer/builder architecture diagram]      │  │  SVG or Excalidraw embed
│  └───────────────────────────────────────────────┘  │
│  • Belief graph with contradiction detection        │
│  • Self-improvement loop (metrics-driven)           │
│  • Bounded autonomy: human merge gate               │
│  • 31 MCP tools · 241 tests · running in prod       │
│                                                     │
├─────────────────────────────────────────────────────┤
│  AUTOLOOP                                [repo →]   │
│  Governed build pipeline for any repo               │
│  ┌───────────────────────────────────────────────┐  │
│  │  [triage → decompose → implement → verify]    │  │  flow diagram
│  └───────────────────────────────────────────────┘  │
│  • One-command setup: autoloop init                 │
│  • Serial dispatch + dependency ordering            │
│  • Config-driven: works on any language/toolchain   │
│  • Protected paths: loop can't modify itself        │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [Gallery →]  "This site improves itself"           │  teaser for Phase 2+
├─────────────────────────────────────────────────────┤
│                                                     │
│  andy@widjaja ~ $                                   │  footer: terminal-style
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Color Palette (dark mode)

| Element | Value | Usage |
|---------|-------|-------|
| Background | `#0d1117` | Page background (GitHub dark) |
| Surface | `#161b22` | Cards, diagrams, code blocks |
| Border | `#30363d` | Subtle separators |
| Text primary | `#e6edf3` | Body text |
| Text secondary | `#8b949e` | Labels, metadata |
| Accent | `#58a6ff` | Links, live indicators |
| Success | `#3fb950` | "Running," "merged," positive states |
| Code font | JetBrains Mono | All monospace elements |
| Body font | Inter | All prose |

### Light Mode (secondary)

Same layout, invert to:
- Background: `#ffffff`
- Surface: `#f6f8fa`
- Border: `#d0d7de`
- Text: `#1f2328`
- Accent: `#0969da`

### Responsive Behavior

- Desktop (>768px): full layout as diagrammed
- Mobile: single column, diagrams scale to full-width, nav collapses to name only
- No hamburger menu — there's nothing to put in it. Just scroll.

### The "Live Indicator" (hero stats)

A compact monospace row of live pipeline metrics, each hyperlinked to the real
GitHub board so visitors can click through and verify:

```
[live] 151 PRs merged · 12 open issues · 94% success · last run: 2h ago
      ↓               ↓                ↓              ↓
      /pulls?merged   /issues          /pipeline      /actions
```

Each stat links to:

| Stat | Destination |
|------|-------------|
| PRs merged | `github.com/.../pulls?q=is:merged+label:autoloop` |
| Open issues | `github.com/.../issues?q=is:open` |
| Success rate | `/pipeline` page (Phase 3) or repo Actions tab |
| Last run | Specific workflow run URL |

**Implementation (GitHub Action → static JSON):**

```yaml
# .github/workflows/stats.yml — runs every hour
- name: Update stats
 run: |
   MERGED=$(gh pr list --state merged --label autoloop --json number --jq length)
   OPEN_ISSUES=$(gh issue list --state open --json number --jq length)
   CLOSED_ISSUES=$(gh issue list --state closed --json number --jq length)
   TOTAL=$((MERGED + $(gh pr list --state closed --label autoloop --json number --jq length)))
   RATE=$(echo "scale=2; $MERGED / $TOTAL" | bc)
   LAST=$(gh run list --workflow autoloop --limit 1 --json updatedAt --jq '.[0].updatedAt')
   echo "{\"prs_merged\":$MERGED,\"issues_open\":$OPEN_ISSUES,\"issues_closed\":$CLOSED_ISSUES,\"success_rate\":$RATE,\"last_run\":\"$LAST\"}" > public/stats.json
- name: Commit & push
 run: git add public/stats.json && git commit -m "chore: update stats" && git push
```

The site fetches `/stats.json` on page load — static file served from CDN, sub-10ms.
Data is at most 1 hour stale, which is fine for the "last run: Xh ago" display.

**Why not client-side GitHub API:** 200-500ms latency per load, 60 req/hr rate limit
unauthenticated, CORS issues. The pre-computed JSON gives live feel with static speed.

For Phase 1 (before the Action exists), hardcode the stats. Replace with the Action
once autoloop is wired up (Phase 2).

### Reference Aesthetics

Sites that hit the right tone for this audience:
- rauchg.com (Guillermo Rauch — minimal, typographic, one idea per page)
- simonwillison.net (datasette) — projects-first, clean, fast
- Linear.app marketing pages — dark, precise, engineering-credible
- Anthropic's research pages — serious, clear, no fluff

### File Structure (Phase 1)

```
site/
├── src/
│   ├── pages/
│   │   ├── index.astro          # hero + project cards
│   │   ├── patina.astro         # deep-dive page
│   │   └── autoloop.astro       # deep-dive page
│   ├── components/
│   │   ├── Header.astro         # name + GitHub link
│   │   ├── ProjectCard.astro    # reusable project block
│   │   ├── LiveStat.astro       # the hero indicator
│   │   └── Footer.astro         # terminal-style footer
│   ├── layouts/
│   │   └── Base.astro           # dark mode, fonts, meta
│   └── assets/
│       ├── patina-arch.svg      # observer/builder diagram
│       └── autoloop-flow.svg    # triage→implement flow
├── public/
│   └── favicon.svg
├── astro.config.mjs
├── tailwind.config.mjs
├── package.json
└── autoloop.toml                # if wiring Phase 2
```

### Content for Project Pages

**Patina page** should include:
- Problem statement (one paragraph: "AI resets every session")
- Architecture diagram (observer/builder/air gap/human gate)
- Key numbers (31 tools, 241 tests, 151 PRs, running since July 4)
- The self-improvement thesis (one paragraph)
- "Novel contribution" (CAIS principles instantiated, self-evolution trilemma satisfied)
- Repo link (prominent)

**Autoloop page** should include:
- Problem statement (one paragraph: "AI coding agents produce merge conflicts and can't sequence dependencies")
- Pipeline diagram (triage → size → decompose → implement → verify → PR)
- Key features (config-driven, language-agnostic, one-command setup, protected paths)
- The `autoloop init` command shown as a terminal capture
- Repo link (prominent)

### Acceptance Criteria (Phase 1)

- [x] Site loads in <1 second (static, no client-side JS required for content)
- [x] Dark mode is default, light mode toggle works
- [x] Hero shows thesis + stats row + LinkedIn link
- [x] Patina section has architecture diagram + repo link
- [x] Autoloop section has pipeline diagram + repo link
- [x] Mobile responsive (single column, readable on iOS)
- [x] No Amazon/AWS branding anywhere
- [x] Deployed to personal domain (https://andywidjaja.com, 2026-07-11)
- [x] HTTPS with HSTS, www redirects to apex
- [ ] Lighthouse score >95 (performance + accessibility)

---

## Enhancement List (for autoloop — Phase 1 decomposition)

> These are `## Enhancement` sections that `create_issue.py --from-spec` will
> parse into GitHub issues for the builder.

## Enhancement 1: Scaffold Astro project with dark-mode layout

Create the base Astro project with Tailwind, dark mode default, Inter + JetBrains
Mono fonts, and the Base layout component. Include Header (name + GitHub link) and
Footer (terminal-style). No content yet — just the shell.

**Files:** `site/` directory, `package.json`, `astro.config.mjs`, `tailwind.config.mjs`,
`src/layouts/Base.astro`, `src/components/Header.astro`, `src/components/Footer.astro`

**Acceptance criteria:**
- Dev server runs with `npm run dev`
- Dark mode renders by default
- Fonts load correctly (Inter body, JetBrains Mono code)
- Lighthouse accessibility >95

## Enhancement 2: Build hero section with thesis and live stat

Implement the home page hero: one-sentence thesis (large, centered), plus the
LiveStat component showing a build-time PR count. Use the layout from Enhancement 1.

**Files:** `src/pages/index.astro`, `src/components/LiveStat.astro`

**Acceptance criteria:**
- Thesis text renders: "I build AI systems that improve themselves under human oversight."
- LiveStat shows a hardcoded count (e.g. "151 PRs merged autonomously") — dynamic fetch is Phase 2
- Responsive: readable on mobile
- No images or decorative elements — typography only

## Enhancement 3: Build Patina project card and deep-dive page

Create the Patina section on the home page (ProjectCard component) and a dedicated
`/patina` page with the architecture diagram placeholder, key numbers, thesis paragraph,
and repo link.

**Files:** `src/components/ProjectCard.astro`, `src/pages/patina.astro`,
`src/assets/patina-arch.svg` (placeholder diagram)

**Acceptance criteria:**
- Home page shows Patina card with title, one-line description, and [repo →] link
- `/patina` page renders with all content sections (problem, architecture, numbers, thesis, link)
- Architecture diagram area shows a placeholder SVG (replace with real diagram later)
- Repo link goes to `https://github.com/Sanctum-Origo-Systems/patina`

## Enhancement 4: Build Autoloop project card and deep-dive page

Create the Autoloop section on the home page and a dedicated `/autoloop` page with
the pipeline flow diagram placeholder, features list, the `autoloop init` terminal
example, and repo link.

**Files:** `src/pages/autoloop.astro`, `src/assets/autoloop-flow.svg` (placeholder)

**Acceptance criteria:**
- Home page shows Autoloop card with title, one-line description, and [repo →] link
- `/autoloop` page renders with all content sections (problem, diagram, features, init example, link)
- Terminal code block showing `autoloop init` usage
- Repo link goes to `https://github.com/Sanctum-Origo-Systems/autoloop`

## Enhancement 5: Add gallery teaser and deploy configuration

Add the "This site improves itself" teaser section at the bottom of the home page
(static text for now, links to nothing — placeholder for Phase 2). Configure
static build output for deployment.

**Files:** `src/pages/index.astro` (append section), `astro.config.mjs` (output: static)

**Acceptance criteria:**
- Gallery teaser appears below project cards
- `npm run build` produces a static `dist/` directory
- All pages render correctly in the built output
- Ready for deployment to any static host (Vercel, Netlify, or VPS nginx)