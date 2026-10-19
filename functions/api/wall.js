// The Yousef Wall: GET lists recent messages, POST adds one.
// Needs a D1 database bound to this Pages project as DB.
const KINDS = { checkin: "Check-in", appreciation: "Appreciation", message: "Message to a Yousef" };
const BLOCKED = /\b(fuck|shit|cunt|nigg|fag|retard|whore|slut|kill yourself|kys)\w*/i;
const LINKS = /(https?:\/\/|www\.|\.(com|net|org|io|ru|xyz|info|biz|co)\b)/i;

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

async function ipHash(request) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("ytube-salt:" + ip));
  return [...new Uint8Array(buf)].slice(0, 12).map(b => b.toString(16).padStart(2, "0")).join("");
}

async function ensure(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, place TEXT, kind TEXT NOT NULL,
    body TEXT NOT NULL, created TEXT NOT NULL, ip_hash TEXT, hidden INTEGER DEFAULT 0, salutes INTEGER DEFAULT 0)`).run();
}

const clean = (s, max) => String(s || "").replace(/[\u0000-\u001f\u007f<>]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);

export async function onRequestGet({ env, request }) {
  if (!env.DB) return json({ error: "The wall is warming up. Try again soon." }, 503);
  await ensure(env.DB);
  const limit = Math.min(100, Math.max(1, parseInt(new URL(request.url).searchParams.get("limit")) || 50));
  const { results } = await env.DB.prepare(
    "SELECT id, name, place, kind, body, created, salutes FROM messages WHERE hidden = 0 ORDER BY id DESC LIMIT ?"
  ).bind(limit).all();
  const { results: c } = await env.DB.prepare("SELECT COUNT(*) AS n FROM messages WHERE hidden = 0").all();
  return json({ messages: results, total: c[0].n });
}

export async function onRequestPost({ env, request }) {
  if (!env.DB) return json({ error: "The wall is warming up. Try again soon." }, 503);
  let d;
  try { d = await request.json(); } catch { return json({ error: "Something went wrong. Please try again." }, 400); }
  if (d.website) return json({ ok: true }); // honeypot: bots fill hidden fields
  const name = clean(d.name, 40), place = clean(d.place, 40), body = clean(d.body, 280);
  const kind = KINDS[d.kind] ? d.kind : "checkin";
  if (!name) return json({ error: "Add a name (first name is fine)." }, 400);
  if (body.length < 3) return json({ error: "Write a few words for the wall." }, 400);
  if (LINKS.test(body + " " + name + " " + place)) return json({ error: "Links aren't allowed on the wall." }, 400);
  if (BLOCKED.test(body + " " + name + " " + place)) return json({ error: "Let's keep the wall friendly. Please rephrase." }, 400);
  await ensure(env.DB);
  const h = await ipHash(request);
  const since = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const { results } = await env.DB.prepare("SELECT COUNT(*) AS n FROM messages WHERE ip_hash = ? AND created > ?").bind(h, since).all();
  if (results[0].n >= 3) return json({ error: "You're posting fast. Take a breather and try again in a few minutes." }, 429);
  const created = new Date().toISOString();
  const r = await env.DB.prepare("INSERT INTO messages (name, place, kind, body, created, ip_hash) VALUES (?, ?, ?, ?, ?, ?)")
    .bind(name, place, kind, body, created, h).run();
  return json({ ok: true, message: { id: r.meta.last_row_id, name, place, kind, body, created, salutes: 0 } });
}
