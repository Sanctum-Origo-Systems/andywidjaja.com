# RSS Feed for andywidjaja.com

> Allow visitors and existing readers to subscribe to site updates via their
> preferred RSS reader. The feed should work with popular readers (Feedly,
> NetNewsWire, Inoreader, etc.) and support auto-discovery.
>
> New blog posts should automatically appear in both the blog index and RSS
> feed by simply adding a file — no manual registry updates.

---

## Context

The site is built with Astro 7.x. Blog posts are currently `.astro` files in
`src/pages/blog/` using a `BlogPost` layout. Post metadata (title, description,
date) is passed as props to the layout component. A manual `posts` array in
`src/pages/blog/index.astro` drives the blog index.

## Design Decision: Content Collection

Migrate blog posts to an Astro content collection so that:
- Adding a new post = dropping one `.mdx` file in `src/content/blog/`
- Blog index and RSS feed both query `getCollection('blog')` automatically
- No manual registry to update — autoloop can create a blog post in one step

---

## Implementation

### 1. Install dependencies

```bash
npm install @astrojs/rss @astrojs/mdx
```

Add MDX integration to `astro.config.mjs`:
```javascript
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://andywidjaja.com',
  integrations: [mdx()],
});
```

### 2. Create content collection

`src/content.config.ts`:
```typescript
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
  }),
});

export const collections = { blog };
```

### 3. Migrate existing blog post

Move `src/pages/blog/110-pipeline.astro` content to:

`src/content/blog/110-pipeline.mdx`:
```mdx
---
title: "The $110/month self-improving pipeline"
description: "Self-improving software is no longer a funded-startup problem. It's a solo-builder problem."
date: 2026-07-14
---

I got tired of implementing my own backlog manually...
(convert HTML content to markdown/MDX)
```

Delete the original `.astro` file after migration.

### 4. Create dynamic blog post route

`src/pages/blog/[slug].astro`:
```astro
---
import { getCollection } from 'astro:content';
import BlogPost from '../../layouts/BlogPost.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ());
  return posts.map(post => ({
    params: { slug: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await post.render();
---

<BlogPost title={post.data.title} description={post.data.description} date={post.data.date.toISOString().split('T')[0]}>
  <Content />
</BlogPost>
```

### 5. Update blog index

`src/pages/blog/index.astro` — replace the manual `posts` array with:
```astro
---
import { getCollection } from 'astro:content';
// ...existing imports

const posts = (await getCollection('blog', ()))
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
---
```

Update the template to use `post.data.title`, `post.data.description`,
`post.data.date`, and `href={`/blog/${post.id}`}`.

### 6. Create RSS endpoint

`src/pages/rss.xml.ts`:
```typescript
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const posts = (await getCollection('blog', ()))
    .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

  return rss({
    title: "Andy Widjaja",
    description: "I build AI systems that improve themselves under human oversight.",
    site: context.site,
    items: posts.map(post => ({
      title: post.data.title,
      description: post.data.description,
      link: `/blog/${post.id}`,
      pubDate: post.data.date,
    })),
  });
}
```

### 7. Add auto-discovery link to `<head>`

`src/layouts/Base.astro` — add inside `<head>`:
```html
<link rel="alternate" type="application/rss+xml" title="Andy Widjaja" href="/rss.xml" />
```

### 8. Add RSS link to footer

`src/components/Footer.astro` — add an RSS link alongside the existing Email
and Resume links, using the standard RSS icon (SVG) or text label:
```html
<a href="/rss.xml" class="text-text-secondary hover:text-accent transition-colors" aria-label="RSS Feed">
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <circle cx="3.5" cy="20.5" r="2.5"/>
    <path d="M1 1c12.7 0 23 10.3 23 23h-4C20 13.5 11.5 5 1 5V1z"/>
    <path d="M1 8c8.8 0 16 7.2 16 16h-4c0-6.6-5.4-12-12-12V8z"/>
  </svg>
</a>
```

---

## Adding a New Blog Post (after implementation)

Just create one file:

`src/content/blog/my-new-post.mdx`:
```mdx
---
title: "My New Post"
description: "A brief description."
date: 2026-07-20
---

Post content in markdown here.
```

That's it. The blog index and RSS feed pick it up automatically on next build.

---

## Testing

**Build validation** (`npm run build`):
- Build succeeds without errors
- `dist/rss.xml` exists in the output
- `dist/blog/110-pipeline/index.html` exists (migrated post renders)

**RSS validation:**
```bash
npm run build && head -5 dist/rss.xml | grep '<rss'
```

**Manual verification:**
- Open `http://localhost:4321/rss.xml` during dev
- Paste the URL into an RSS reader and confirm it parses
- Verify the migrated blog post appears with correct title, date, and link
- Add a test `.mdx` file, rebuild, confirm it appears in both blog index and feed

**Auto-discovery:**
- View page source, confirm `<link rel="alternate" ...>` is present
- Use an RSS reader's "add by URL" with just `https://andywidjaja.com` —
  should auto-discover the feed

---

## Acceptance Criteria

- [ ] `@astrojs/rss` and `@astrojs/mdx` installed
- [ ] Content collection defined in `src/content.config.ts`
- [ ] Existing blog post migrated to `src/content/blog/110-pipeline.mdx`
- [ ] Dynamic route `src/pages/blog/[slug].astro` renders collection posts
- [ ] Blog index queries content collection (no manual posts array)
- [ ] RSS endpoint at `src/pages/rss.xml.ts` generates valid RSS 2.0 XML
- [ ] `site` field set in `astro.config.mjs`
- [ ] MDX integration configured in `astro.config.mjs`
- [ ] Auto-discovery `<link rel="alternate">` tag in `<head>`
- [ ] RSS icon/link visible in footer alongside existing links
- [ ] `dist/rss.xml` exists after `npm run build`
- [ ] Feed contains all non-draft posts with title, description, link, and date
- [ ] `npm run build` succeeds
- [ ] New posts only require adding one `.mdx` file — no registry update needed

---

## Non-Goals

- Full-text content in RSS items (description only for now)
- Atom feed support
- Category/tag filtering
- Comments or social sharing
