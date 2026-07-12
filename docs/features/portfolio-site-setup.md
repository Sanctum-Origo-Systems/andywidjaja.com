# Portfolio Site Setup — Runbook

> **Human-run setup, NOT a coding task.** No `## Enhancement N:` sections.
> The companion spec (`portfolio-site.md`) contains the design, content, and
> Enhancement sections for the builder. This file covers initialization only.
>
> **Do this on the personal device.** The portfolio site is a personal project,
> not an Amazon/work asset. Use your personal GitHub account and personal machine.

---

## Prerequisites

- Personal device with Node.js 18+ and npm
- `gh` CLI authenticated to personal GitHub (`Sanctum-Origo-Systems`)
- Patina repo cloned locally (for `autoloop init`)
- A personal domain (existing — point DNS after deploy)

---

## Step 1: Create the repo

```bash
mkdir ~/Git/andywidjaja.com && cd ~/Git/andywidjaja.com
git init
gh repo create Sanctum-Origo-Systems/andywidjaja.com \
 --public --source=. --push --description "Personal portfolio — built and improved by AI"
```

> Adjust the repo name to match your actual domain if different.

---

## Step 2: Scaffold Astro + Tailwind

```bash
cd ~/Git/andywidjaja.com
npm create astro@latest . -- --template minimal --no-install --typescript strict
npm install
npm install tailwindcss @tailwindcss/vite
npm install @fontsource/inter @fontsource/jetbrains-mono
```

Create `tailwind.config.mjs`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
 content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
 darkMode: 'class',
 theme: {
   extend: {
     colors: {
       bg: '#0d1117',
       surface: '#161b22',
       border: '#30363d',
       'text-primary': '#e6edf3',
       'text-secondary': '#8b949e',
       accent: '#58a6ff',
       success: '#3fb950',
     },
     fontFamily: {
       sans: ['Inter', 'system-ui', 'sans-serif'],
       mono: ['JetBrains Mono', 'monospace'],
     },
   },
 },
 plugins: [],
}
```

Update `astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
 output: 'static',
 vite: {
   plugins: [tailwindcss()],
 },
});
```

Verify it builds:
```bash
npm run dev    # should start on localhost:4321
npm run build  # should produce dist/
```

Commit:
```bash
git add -A
git commit -m "feat: scaffold Astro project with Tailwind dark mode"
git push
```

---

## Step 3: Initialize autoloop on the portfolio repo

```bash
# From wherever your patina repo is cloned:
python ~/Git/patina/autoloop/init.py \
 --repo Sanctum-Origo-Systems/andywidjaja.com \
 --target ~/Git/andywidjaja.com \
 --reviewer andywidjaja \
 --verify-cmd "npm run build"
```

This creates:
- `autoloop.toml` (config for the portfolio repo)
- `.github/workflows/autoloop-cleanup.yml` (post-merge CI)
- GitHub labels (`ready`, `rejected`, `needs-decomposition`, etc.)
- `.gitignore` entry for `autoloop/run_history.jsonl`

Commit and push:
```bash
cd ~/Git/andywidjaja.com
git add autoloop.toml .github/ .gitignore
git commit -m "feat: add autoloop pipeline"
git push
```

---

## Step 4: Build Phase 1 interactively (recommended)

Phase 1 is taste-work — visual design choices, content writing, layout tuning.
Build it yourself with Claude Code on the personal device rather than waiting
for the VPS builder's cron cycles.

Open Claude Code in the portfolio directory:
```bash
cd ~/Git/andywidjaja.com
claude
```

Reference the spec for content and design:
```
Read docs/features/portfolio-site.md from my patina repo at ~/Git/patina/
and help me implement the Phase 1 site — hero, Patina page, Autoloop page,
gallery teaser. Follow the Design & UX Spec section exactly.
```

Iterate until you're happy with how it looks. This should take 2-3 hours.

---

## Step 5: Deploy

### Option A: Vercel (fastest, free tier)

```bash
npm install -g vercel
cd ~/Git/andywidjaja.com
vercel --prod
```

Then point your domain's DNS to Vercel's nameservers (instructions in Vercel dashboard).

### Option B: VPS (existing Hostinger box)

Build locally and copy to VPS:
```bash
npm run build
scp -r dist/* andy@<vps-ip>:/var/www/portfolio/
```

Nginx config on VPS:
```nginx
server {
   listen 80;
   server_name yourdomain.com;
   root /var/www/portfolio;
   index index.html;


   location / {
       try_files $uri $uri/ /index.html;
   }
}
```

Then add SSL via certbot:
```bash
sudo certbot --nginx -d yourdomain.com
```

### Option C: GitHub Pages

In `astro.config.mjs`:
```javascript
export default defineConfig({
 site: 'https://yourdomain.com',
 output: 'static',
});
```

Enable GitHub Pages in the repo settings (deploy from `gh-pages` branch or GitHub Actions).

**Recommendation:** Vercel (Option A) for fastest deploy + automatic preview on every push.

---

## Step 6: Wire autoloop for ongoing improvements (Phase 2+)

Once Phase 1 is live and you're happy with the baseline, use `--from-spec`
to create issues from the remaining Enhancement sections (or file new issues
as the site evolves):

```bash
cd ~/Git/patina
uv run python autoloop/create_issue.py \
 --from-spec docs/features/portfolio-site.md \
 --repo Sanctum-Origo-Systems/andywidjaja.com
```

Then either:
- Point the VPS builder at this repo (add a second systemd service)
- Or run `autoloop triage` and `autoloop implement` locally as needed

For Phase 2 (live feedback pipeline), the VPS becomes more valuable — it runs
the scoring and variant-building pipeline autonomously.

---

## Step 7: Verify before sharing

Before adding the URL to your resume or outreach messages:

- [x] Site loads in <1 second
- [x] Dark mode renders correctly as default
- [x] Hero shows thesis + stats row
- [x] Hero has LinkedIn link
- [x] Patina page has architecture diagram + repo link
- [x] Autoloop page has pipeline diagram + repo link
- [x] Mobile responsive (checked on iOS)
- [x] No Amazon/AWS branding anywhere
- [ ] Lighthouse score >95
- [x] URL works with and without `www`
- [x] SSL certificate valid (HTTPS + HSTS via Vercel)

Once all checked: add to resume, LinkedIn (profile link only, no post), and
include in follow-up messages to Sarah/Dan when they respond.

---

## What NOT to do

- ❌ Don't build this on the work device
- ❌ Don't use any Amazon branding, logos, or customer names
- ❌ Don't post the URL on LinkedIn publicly (colleagues will see)
- ❌ Don't wait for Phase 2-4 before deploying — Phase 1 is enough for interviews
- ❌ Don't let autoloop build Phase 1 autonomously — it's taste-work, do it interactively
- ❌ Don't spend more than 1 day on Phase 1 — ship fast, iterate later