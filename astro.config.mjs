// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
 site: 'https://andywidjaja.com',
 output: 'static',
 integrations: [mdx()],
 markdown: {
   shikiConfig: {
     themes: {
       light: 'github-light',
       dark: 'github-dark',
     },
     defaultColor: false,
   },
 },
 vite: {
   plugins: [tailwindcss()],
 },
});