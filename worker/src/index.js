// boggsfiles-dailies: hands out short-lived signed links for the Dailies pages and streams the
// files from the private bucket. Two routes:
//   GET /sign?key=<r2 key>          -> {"url": ".../v/<key>?e=<expiry>&s=<sig>"}   (page must come from boggsfiles.com)
//   GET|HEAD /v/<key>?e=&s=          -> the video, with Range support so seeking works
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return cors(new Response(null, { status: 204 }), request, env);
    if (url.pathname === "/sign") return sign(request, env, url);
    if (url.pathname.startsWith("/v/")) return serve(request, env, url);
    return new Response("not found", { status: 404 });
  },
};

const allowed = (env) => env.ALLOWED_ORIGINS.split(",").map((s) => s.trim());
const originOf = (request) => {
  const o = request.headers.get("Origin"); if (o) return o;
  const r = request.headers.get("Referer"); if (!r) return null;
  try { return new URL(r).origin; } catch { return null; }
};
function cors(res, request, env) {
  const o = originOf(request);
  if (o && allowed(env).includes(o)) {
    res.headers.set("Access-Control-Allow-Origin", o);
    res.headers.set("Vary", "Origin");
    res.headers.set("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
  }
  return res;
}

async function hmac(env, msg) {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.SIGNING_SECRET), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(msg));
  return btoa(String.fromCharCode(...new Uint8Array(sig))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sign(request, env, url) {
  const o = originOf(request);
  if (!o || !allowed(env).includes(o)) return new Response("forbidden", { status: 403 });
  const key = url.searchParams.get("key");
  if (!key || key.includes("..")) return new Response("bad key", { status: 400 });
  const exp = Math.floor(Date.now() / 1000) + parseInt(env.LINK_TTL_SECONDS || "21600", 10);
  const s = await hmac(env, `${key}|${exp}`);
  const signed = `${url.origin}/v/${key.split("/").map(encodeURIComponent).join("/")}?e=${exp}&s=${s}`;
  return cors(new Response(JSON.stringify({ url: signed, expires: exp }), { headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } }), request, env);
}

async function serve(request, env, url) {
  if (request.method !== "GET" && request.method !== "HEAD") return new Response("method", { status: 405 });
  const key = decodeURIComponent(url.pathname.slice(3));
  const exp = parseInt(url.searchParams.get("e") || "0", 10), s = url.searchParams.get("s") || "";
  if (!exp || exp < Date.now() / 1000) return new Response("link expired", { status: 410 });
  if (s !== await hmac(env, `${key}|${exp}`)) return new Response("bad signature", { status: 403 });
  // hotlink guard: if the browser tells us where the request came from, it must be the site
  const o = originOf(request);
  if (o && !allowed(env).includes(o)) return new Response("forbidden", { status: 403 });

  const obj = await env.DAILIES.get(key, { range: request.headers, onlyIf: request.headers });
  if (!obj) return new Response("not found", { status: 404 });
  const h = new Headers();
  obj.writeHttpMetadata(h);
  h.set("ETag", obj.httpEtag);
  h.set("Accept-Ranges", "bytes");
  h.set("Cache-Control", "private, max-age=0");
  h.set("Content-Disposition", "inline");
  if (!h.get("Content-Type")) h.set("Content-Type", "video/mp4");
  if (!("body" in obj)) return new Response(null, { status: 304, headers: h });   // onlyIf precondition failed
  let status = 200;
  if (request.headers.has("Range") && obj.range && "offset" in obj.range) {
    const start = obj.range.offset, len = obj.range.length ?? obj.size - start;
    h.set("Content-Range", `bytes ${start}-${start + len - 1}/${obj.size}`);
    h.set("Content-Length", String(len));
    status = 206;
  } else h.set("Content-Length", String(obj.size));
  return new Response(request.method === "HEAD" ? null : obj.body, { status, headers: h });
}
