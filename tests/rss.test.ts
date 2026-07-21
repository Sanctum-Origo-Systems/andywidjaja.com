import { describe, it, expect, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

vi.mock('@astrojs/rss', () => ({
  default: vi.fn((opts: any) => opts),
}));

vi.mock('astro:content', () => ({
  getCollection: vi.fn(() => [
    {
      id: 'first-post',
      data: {
        title: 'First Post',
        description: 'A first post',
        date: new Date('2026-01-01'),
      },
    },
    {
      id: 'second-post',
      data: {
        title: 'Second Post',
        description: 'A second post',
        date: new Date('2026-02-01'),
      },
    },
  ]),
}));

describe('RSS endpoint', () => {
  it('throws when context.site is undefined', async () => {
    const { GET } = await import('../src/pages/rss.xml.ts');
    await expect(GET({ site: undefined } as any)).rejects.toThrow(
      'Missing "site" in astro.config.mjs'
    );
  });

  it('returns rss() result with correct feed metadata', async () => {
    const { GET } = await import('../src/pages/rss.xml.ts');
    const site = new URL('https://example.com');
    const result = await GET({ site } as any);

    expect(result).toMatchObject({
      title: 'Andy Widjaja',
      description: 'I build AI systems that improve themselves under human oversight.',
      site,
    });
  });

  it('declares the Atom namespace', async () => {
    const { GET } = await import('../src/pages/rss.xml.ts');
    const result: any = await GET({ site: new URL('https://example.com') } as any);

    expect(result.xmlns).toEqual({ atom: 'http://www.w3.org/2005/Atom' });
  });

  it('includes atom:link rel="self" derived from context.site', async () => {
    const { GET } = await import('../src/pages/rss.xml.ts');
    const site = new URL('https://example.com');
    const result: any = await GET({ site } as any);

    expect(result.customData).toContain('atom:link');
    expect(result.customData).toContain('rel="self"');
    expect(result.customData).toContain('type="application/rss+xml"');
    expect(result.customData).toContain('href="https://example.com/rss.xml"');
  });

  it('maps blog posts to RSS items with title, description, pubDate, and link', async () => {
    const { GET } = await import('../src/pages/rss.xml.ts');
    const result: any = await GET({ site: new URL('https://example.com') } as any);

    expect(result.items).toHaveLength(2);
    expect(result.items[0]).toEqual({
      title: 'First Post',
      description: 'A first post',
      pubDate: new Date('2026-01-01'),
      link: '/blog/first-post/',
    });
    expect(result.items[1]).toEqual({
      title: 'Second Post',
      description: 'A second post',
      pubDate: new Date('2026-02-01'),
      link: '/blog/second-post/',
    });
  });
});

describe('RSS auto-discovery', () => {
  const baseAstro = readFileSync(
    resolve(__dirname, '../src/layouts/Base.astro'),
    'utf-8'
  );

  it('Base.astro includes RSS alternate link in head', () => {
    expect(baseAstro).toContain(
      '<link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml" />'
    );
  });
});

describe('Footer RSS link', () => {
  const footerAstro = readFileSync(
    resolve(__dirname, '../src/components/Footer.astro'),
    'utf-8'
  );

  it('Footer contains an anchor linking to /rss.xml', () => {
    expect(footerAstro).toContain('href="/rss.xml"');
  });

  it('Footer RSS link wraps an SVG icon', () => {
    const rssLinkMatch = footerAstro.match(
      /<a[^>]*href="\/rss\.xml"[^>]*>[\s\S]*?<svg[\s\S]*?<\/svg>[\s\S]*?<\/a>/
    );
    expect(rssLinkMatch).not.toBeNull();
  });

  it('Footer RSS link has an aria-label', () => {
    const rssAnchor = footerAstro.match(/<a[^>]*href="\/rss\.xml"[^>]*>/);
    expect(rssAnchor?.[0]).toContain('aria-label');
  });
});
