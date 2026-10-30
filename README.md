# YousefTube

Static site for youseftube.com, hosted on Cloudflare Pages (no build step; output directory is the repo root).

- `index.html` – the site
- `data/news.json` – the "Yousefs Winning" feed, refreshed daily by a scheduled task (newest first, max 8 stories, positive news only, every story links its source)
- `privacy.html` – privacy policy (needed for AdSense)

Logo: search for `LOGO SLOT` in index.html to swap in an image.

## Newsletter + Yousef Wall
- `functions/api/subscribe.js`, `functions/api/wall.js`, `functions/api/salute.js` are Cloudflare Pages Functions.
- They use the D1 database `youseftube` (bound as `DB` in `wrangler.toml`). Tables are created automatically.
- Export subscribers / moderate posts in Cloudflare → D1 → youseftube → Console, e.g.
  `SELECT email, created FROM subscribers ORDER BY id;`
  `UPDATE messages SET hidden = 1 WHERE id = 123;`

## Editing the news feed (Pages CMS)
Log in at https://app.pagescms.org with GitHub, open `liftologist/Youseftube`, then "Yousefs Winning (news feed)". Add new stories at the top; saving commits to `main` and Cloudflare Pages redeploys in a minute or two. Config: `.pages.yml`.
