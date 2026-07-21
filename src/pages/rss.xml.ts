import type { APIContext } from 'astro';
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context: APIContext) {
  if (!context.site) {
    throw new Error('Missing "site" in astro.config.mjs — required for RSS feed generation');
  }
  const posts = await getCollection('blog');
  return rss({
    title: 'Andy Widjaja',
    description: 'I build AI systems that improve themselves under human oversight.',
    site: context.site,
    xmlns: { atom: 'http://www.w3.org/2005/Atom' },
    customData: `<atom:link href="${new URL('rss.xml', context.site)}" rel="self" type="application/rss+xml"/>`,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: `/blog/${post.id}/`,
    })),
  });
}
