// Adds one "salute" to a wall message.
const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

export async function onRequestPost({ env, request }) {
  if (!env.DB) return json({ error: "unavailable" }, 503);
  let d;
  try { d = await request.json(); } catch { return json({ error: "bad request" }, 400); }
  const id = parseInt(d.id);
  if (!id) return json({ error: "bad request" }, 400);
  await env.DB.prepare("UPDATE messages SET salutes = salutes + 1 WHERE id = ? AND hidden = 0").bind(id).run();
  const { results } = await env.DB.prepare("SELECT salutes FROM messages WHERE id = ?").bind(id).all();
  return json({ ok: true, salutes: results[0] ? results[0].salutes : 0 });
}
