// Vercel serverless function: GET /api/extract?url=https://company.com
// Fetches the company's site server-side (browsers cannot, because of CORS),
// extracts what the deal-fit scanner needs, and returns JSON.
//
// Two modes:
//   - "claude":    when ANTHROPIC_API_KEY is set, the page text goes to Claude with a
//                  strict output schema and comes back as structured fields.
//   - "heuristic": otherwise, plain regex/keyword extraction. Less precise, no key needed.

import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";

const SECTORS = [
  "AI & SaaS",
  "Consumer & D2C",
  "FinTech",
  "DeepTech & Climate",
  "HealthTech",
  "Gaming & Media",
  "B2B Commerce & Logistics",
  "EdTech & HR",
];

const SECTOR_KEYWORDS = {
  "AI & SaaS": ["saas", "software", "platform", "workflow", "enterprise", "api", "automation", "agent", "agentic", "copilot", "analytics", "devops", "cloud", "b2b software", "crm", "erp", "productivity"],
  "Consumer & D2C": ["d2c", "brand", "skincare", "beauty", "fashion", "apparel", "snack", "food", "beverage", "consumer", "retail", "fitness", "wellness", "lifestyle", "jewellery", "jewelry", "furniture", "shop"],
  "FinTech": ["fintech", "payments", "lending", "credit", "insurance", "insurtech", "wealth", "investing", "brokerage", "neobank", "kyc", "loan", "bnpl", "mutual fund", "trading"],
  "DeepTech & Climate": ["satellite", "space", "orbit", "robot", "robotics", "battery", "ev", "electric vehicle", "climate", "carbon", "solar", "energy storage", "semiconductor", "motor", "recycling", "hardware", "iot", "drone", "materials", "manufacturing", "modular"],
  "HealthTech": ["health", "healthcare", "hospital", "clinic", "doctor", "patient", "medical", "diagnostic", "pharma", "biotech", "therapeutic", "emr", "surgery", "surgical", "nutrition"],
  "Gaming & Media": ["game", "games", "gaming", "esports", "creator", "fan", "fandom", "content", "media", "streaming", "social", "community", "entertainment", "video", "podcast", "nft"],
  "B2B Commerce & Logistics": ["marketplace", "wholesale", "kirana", "logistics", "supply chain", "fulfilment", "fulfillment", "procurement", "distribution", "warehouse", "freight", "agri-input", "sourcing", "b2b commerce"],
  "EdTech & HR": ["edtech", "learning", "students", "upskilling", "course", "bootcamp", "hiring", "recruit", "recruiting", "talent", "hr", "career", "assessment", "school", "college"],
};

const INDIAN_CITIES = ["bengaluru", "bangalore", "mumbai", "delhi", "gurugram", "gurgaon", "noida", "hyderabad", "chennai", "pune", "kolkata", "ahmedabad", "jaipur", "kochi", "thiruvananthapuram", "trivandrum", "chandigarh", "mohali", "indore", "lucknow", "surat", "coimbatore", "bhubaneswar"];

const Extracted = z.object({
  name: z.string().describe("Company name as the site presents it"),
  oneLiner: z.string().describe("One sentence: what the company does and for whom, in plain words"),
  sector: z.enum(SECTORS).describe("Closest sector bucket"),
  keywords: z.array(z.string()).describe("5 to 10 lowercase keywords describing product, customer and market"),
  hqCity: z.string().describe("Headquarters city if stated, else empty string"),
  geo: z.enum(["india", "global", "other"]).describe("india = India-based serving India; global = India-based serving global customers; other = not India-based"),
  foundedYear: z.number().nullable().describe("Founding year if stated, else null"),
  founders: z.array(z.object({ name: z.string(), role: z.string() })).describe("Founders named on the site, with role"),
  founderProfile: z.enum(["first", "repeat", "operator", "unknown"]).describe("first = first-time founders; repeat = previously founded a company; operator = senior big-company operators; unknown if no evidence"),
  womenLed: z.boolean().describe("True only if a woman is clearly the CEO or a founder"),
  aiNative: z.boolean().describe("True if AI/ML is core to the product, not a bolt-on mention"),
  indiaMarket: z.boolean().describe("True if the primary customers are in India"),
  hasTraction: z.boolean().describe("True if the site cites customers, revenue, users or logos"),
  stageGuess: z.enum(["Pre-seed", "Seed", "Series A", "Series B", "Later", "unknown"]).describe("Most recent funding stage if mentioned"),
  roundSizeUsdM: z.number().nullable().describe("Most recent round size in USD millions if mentioned, else null"),
  evidence: z.array(z.string()).describe("3 to 6 short quotes or facts from the site that support the fields above"),
});

function isPrivateHost(host) {
  const h = host.toLowerCase();
  if (h === "localhost" || h.endsWith(".local") || h.endsWith(".internal")) return true;
  const m = h.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
  if (m) {
    const [a, b] = [Number(m[1]), Number(m[2])];
    if (a === 10 || a === 127 || a === 0 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 169 && b === 254)) return true;
  }
  if (h.includes(":")) return true; // IPv6 literal
  return false;
}

async function fetchText(url, ms = 8000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try {
    const r = await fetch(url, {
      redirect: "follow",
      signal: ctrl.signal,
      headers: { "User-Agent": "Mozilla/5.0 (compatible; KalaariDecoded/1.0; +https://github.com/modiparv/Kalaari_decoded)", Accept: "text/html,application/xhtml+xml" },
    });
    if (!r.ok) return { error: `HTTP ${r.status}` };
    const ct = r.headers.get("content-type") || "";
    if (!/html|xml|text/i.test(ct)) return { error: `not HTML (${ct})` };
    const buf = await r.arrayBuffer();
    const text = new TextDecoder("utf-8", { fatal: false }).decode(buf.slice(0, 1_500_000));
    return { html: text, finalUrl: r.url };
  } catch (e) {
    return { error: e.name === "AbortError" ? "timed out" : String(e.message || e) };
  } finally {
    clearTimeout(t);
  }
}

const decode = (s) => String(s || "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'").replace(/&nbsp;/g, " ").replace(/&#(\d+);/g, (_, n) => String.fromCharCode(n));
const strip = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<noscript[\s\S]*?<\/noscript>/gi, " ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

function meta(html, name) {
  const re = new RegExp(`<meta[^>]+(?:name|property)=["']${name}["'][^>]*content=["']([^"']*)["']`, "i");
  const re2 = new RegExp(`<meta[^>]+content=["']([^"']*)["'][^>]*(?:name|property)=["']${name}["']`, "i");
  const m = html.match(re) || html.match(re2);
  return m ? decode(m[1]).trim() : "";
}

function parsePage(html, url) {
  const title = decode((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [, ""])[1]).replace(/\s+/g, " ").trim();
  const headings = [...html.matchAll(/<h[12][^>]*>([\s\S]*?)<\/h[12]>/gi)].map((m) => strip(m[1])).filter(Boolean).slice(0, 12);
  const jsonld = [];
  for (const m of html.matchAll(/<script[^>]+application\/ld\+json[^>]*>([\s\S]*?)<\/script>/gi)) {
    try { jsonld.push(JSON.parse(m[1])); } catch {}
  }
  const aboutLink = (html.match(/href=["']([^"']*(?:about|team|company)[^"']*)["']/i) || [])[1];
  return { url, title, description: meta(html, "description") || meta(html, "og:description"), ogTitle: meta(html, "og:title"), siteName: meta(html, "og:site_name"), headings, jsonld, text: strip(html).slice(0, 12000), aboutLink };
}

function heuristic(pages, hostname) {
  const p = pages[0];
  const all = pages.map((x) => [x.title, x.description, x.headings.join(" "), x.text].join(" ")).join(" ");
  const low = all.toLowerCase();
  const count = (re) => (low.match(re) || []).length;

  const scores = Object.fromEntries(SECTORS.map((s) => [s, 0]));
  for (const [sector, words] of Object.entries(SECTOR_KEYWORDS)) for (const w of words) scores[sector] += count(new RegExp(`\\b${w.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")}\\b`, "g"));
  const sector = SECTORS.slice().sort((a, b) => scores[b] - scores[a])[0];

  const org = [].concat(...pages.map((x) => x.jsonld)).flatMap((j) => (Array.isArray(j) ? j : [j])).flatMap((j) => (j && j["@graph"] ? j["@graph"] : [j])).find((j) => j && /Organization|Corporation|LocalBusiness/i.test(String(j["@type"])));
  let name = (org && org.name) || p.siteName || p.ogTitle || p.title.split(/[|\-–—:]/)[0].trim() || hostname;
  name = name.replace(/\s*(home|official site)\s*$/i, "").trim();

  const founders = [];
  const seen = new Set();
  const addF = (n, role) => { n = n.trim(); if (n && n.split(" ").length >= 2 && n.split(" ").length <= 4 && !seen.has(n)) { seen.add(n); founders.push({ name: n, role }); } };
  if (org && org.founder) (Array.isArray(org.founder) ? org.founder : [org.founder]).forEach((f) => addF(typeof f === "string" ? f : f.name || "", "Founder"));
  for (const m of all.matchAll(/([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}),?\s*(?:\(|-|–|—|,)?\s*(Co-?Founder(?:\s*&\s*CEO| and CEO| & CTO)?|Founder(?:\s*&\s*CEO| and CEO)?|CEO)\b/g)) addF(m[1], m[2]);
  for (const m of all.matchAll(/[Ff]ounded (?:in \d{4} )?by ([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})(?:,? (?:and|&) ([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}))?/g)) { addF(m[1], "Founder"); if (m[2]) addF(m[2], "Founder"); }

  const fy = (org && org.foundingDate && String(org.foundingDate).match(/(20\d\d|19\d\d)/)) || all.match(/(?:founded|established|since|started)\s+(?:in\s+)?((?:19|20)\d\d)/i);
  const city = INDIAN_CITIES.find((c) => low.includes(c));
  const indiaMentions = count(/\bindia\b/g);
  const geo = city || hostname.endsWith(".in") || indiaMentions >= 2 ? (count(/\b(global|worldwide|us customers|united states|europe)\b/g) >= 2 ? "global" : "india") : "other";
  const ai = count(/\b(ai|artificial intelligence|machine learning|llm|agentic|ai-powered|ai-native|copilot)\b/g);
  const stageM = all.match(/\b(pre-seed|seed|series [abc])\b/i);
  const roundM = all.match(/\$\s?([\d.]+)\s?(million|mn|m)\b/i);
  const traction = count(/\b(customers|revenue|users|paying|enterprises trust|trusted by|clients)\b/g) >= 2;

  const evidence = [];
  if (p.description) evidence.push(`Meta description: "${p.description.slice(0, 160)}"`);
  if (p.headings[0]) evidence.push(`H1: "${p.headings[0].slice(0, 120)}"`);
  if (city) evidence.push(`Mentions ${city[0].toUpperCase() + city.slice(1)}`);
  if (fy) evidence.push(`Founded ${fy[1]}`);
  if (stageM) evidence.push(`Funding stage mentioned: ${stageM[1]}`);
  evidence.push(`Sector keyword hits: ${SECTORS.map((s) => `${s} ${scores[s]}`).filter((x) => !/ 0$/.test(x)).slice(0, 4).join(", ") || "none"}`);

  return {
    name, oneLiner: p.description || p.headings[0] || p.title, sector,
    keywords: [...new Set((low.match(/[a-z][a-z-]{3,}/g) || []).filter((w) => Object.values(SECTOR_KEYWORDS).flat().includes(w)))].slice(0, 10),
    hqCity: city ? city[0].toUpperCase() + city.slice(1) : "", geo,
    foundedYear: fy ? Number(fy[1]) : null, founders: founders.slice(0, 5), founderProfile: "unknown",
    womenLed: false, aiNative: ai >= 2, indiaMarket: geo === "india", hasTraction: traction,
    stageGuess: stageM ? stageM[1].replace(/^\w/, (c) => c.toUpperCase()).replace(/series (\w)/i, (_, l) => "Series " + l.toUpperCase()) : "unknown",
    roundSizeUsdM: roundM ? Number(roundM[1]) : null, evidence,
  };
}

async function withClaude(pages, hostname) {
  const client = new Anthropic();
  const bundle = pages.map((p) => `URL: ${p.url}\nTITLE: ${p.title}\nDESCRIPTION: ${p.description}\nHEADINGS: ${p.headings.join(" | ")}\nTEXT: ${p.text.slice(0, 7000)}`).join("\n\n-----\n\n");
  const response = await client.messages.parse({
    model: "claude-opus-5",
    max_tokens: 4000,
    output_config: { format: zodOutputFormat(Extracted), effort: "low" },
    system: "You extract startup facts from website text for a venture-capital screening tool. Use only what the text supports; leave fields empty, null, false or 'unknown' when there is no evidence. Founders must be named on the page. Keep the one-liner concrete: product, customer, market.",
    messages: [{ role: "user", content: `Website host: ${hostname}\n\n${bundle}` }],
  });
  if (response.stop_reason === "refusal" || !response.parsed_output) throw new Error("no structured output");
  return response.parsed_output;
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  const raw = (req.query && req.query.url) || "";
  let target;
  try {
    target = new URL(/^https?:\/\//i.test(raw) ? raw : "https://" + raw);
  } catch {
    return res.status(400).json({ ok: false, error: "That does not look like a website address." });
  }
  if (!/^https?:$/.test(target.protocol) || isPrivateHost(target.hostname)) return res.status(400).json({ ok: false, error: "Only public http(s) websites are supported." });

  const first = await fetchText(target.href);
  if (first.error) return res.status(502).json({ ok: false, error: `Could not read ${target.hostname}: ${first.error}.` });
  const pages = [parsePage(first.html, first.finalUrl || target.href)];
  if (pages[0].aboutLink) {
    try {
      const about = new URL(pages[0].aboutLink, first.finalUrl || target.href);
      if (about.hostname === target.hostname && !isPrivateHost(about.hostname)) {
        const second = await fetchText(about.href, 6000);
        if (second.html) pages.push(parsePage(second.html, about.href));
      }
    } catch {}
  }

  const hostname = target.hostname.replace(/^www\./, "");
  let company, mode = "heuristic", warning = "";
  if (process.env.ANTHROPIC_API_KEY) {
    try { company = await withClaude(pages, hostname); mode = "claude"; }
    catch (e) { warning = `Claude extraction failed (${e.message || e}); used heuristic extraction.`; }
  }
  if (!company) company = heuristic(pages, hostname);
  return res.status(200).json({ ok: true, mode, warning, pagesRead: pages.map((p) => p.url), company });
}
