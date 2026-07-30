# andywidjaja.com

Personal portfolio — built and continuously improved by [autoloop](https://github.com/Sanctum-Origo-Systems/autoloop).

## Stack

- [Astro](https://astro.build/) — static site generator
- [Tailwind CSS](https://tailwindcss.com/) — styling
- [MDX](https://mdxjs.com/) — blog content via Astro content collections
- [Vercel](https://vercel.com/) — hosting, auto-deploys on merge to main
- [autoloop](https://github.com/Sanctum-Origo-Systems/autoloop) — AI pipeline for triaging issues, implementing changes, and opening PRs

## Development

```sh
npm install
npm run dev       # localhost:4321
npm run build     # static output to dist/
```

## How It Works

Issues filed on this repo are triaged and implemented by autoloop running on a VPS. The pipeline creates feature branches, implements changes, runs `npm run build` to verify, and opens PRs. A human reviews and merges — that's the gate.

Blog posts are MDX files in `src/content/blog/`. Adding a new post is one file — the blog index and [RSS feed](/rss.xml) update automatically on deploy.
