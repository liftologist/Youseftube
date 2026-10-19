// Newsletter signup: stores the email in the D1 database bound as DB.
const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

export async function onRequestPost({ env, request }) {
  if (!env.DB) return json({ error: "Signups are warming up. Try again soon." }, 503);
  let d;
  try { d = await request.json(); } catch { return json({ error: "Something went wrong. Please try again." }, 400); }
  if (d.website) return json({ ok: true }); // honeypot
  const email = String(d.email || "").trim().toLowerCase().slice(0, 200);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return json({ error: "Enter an email address like you@example.com" }, 400);
  await env.DB.prepare(`CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, created TEXT NOT NULL, source TEXT)`).run();
  await env.DB.prepare("INSERT OR IGNORE INTO subscribers (email, created, source) VALUES (?, ?, ?)")
    .bind(email, new Date().toISOString(), String(d.source || "site").slice(0, 40)).run();
  return json({ ok: true });
}
