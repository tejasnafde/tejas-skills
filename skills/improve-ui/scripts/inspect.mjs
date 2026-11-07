#!/usr/bin/env node
// Rendered UI check for improve-ui: a few accessibility rules plus layout and copy signals.
// Idea and check list adapted from flawless-ui-ux by smokeeaasd (https://github.com/smokeeaasd/flawless-ui-ux), MIT.
//
// usage: node inspect.mjs <url> [--out=<dir>] [--viewport=1440x900 ...] [--selector=<css>] [--timeout=15000]
// Resolves playwright (or playwright-core) and axe-core from the current project first, then globally.
// Exit 0: sample complete, no confirmed errors. 1: confirmed errors. 2: incomplete coverage.
import { createRequire } from "node:module";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const args = process.argv.slice(2);
const values = (name) => args.filter((arg) => arg.startsWith(`--${name}=`)).map((arg) => arg.slice(name.length + 3));
const url = args.find((arg) => !arg.startsWith("--"));
if (!url) {
  console.error("usage: node inspect.mjs <url> [--out=<dir>] [--viewport=1440x900 ...] [--selector=<css>] [--timeout=15000]");
  process.exit(2);
}
const out = values("out")[0];
const selector = values("selector")[0];
const timeout = Number(values("timeout")[0] ?? 15000);
const viewports = (values("viewport").length ? values("viewport") : ["1440x900", "390x844"]).map((v) => {
  const [width, height] = v.split("x").map(Number);
  return { label: v, width, height };
});
const AXE_RULES = ["color-contrast", "button-name", "link-name", "label", "image-alt"];

const projectRequire = createRequire(join(process.cwd(), "package.json"));
async function load(name) {
  try {
    return projectRequire(name);
  } catch {}
  try {
    return await import(name);
  } catch {}
  return null;
}

const report = { url, viewports: [], findings: [], limits: [] };
const kit = (await load("playwright")) ?? (await load("playwright-core"));
if (!kit) {
  report.limits.push("Playwright is not installed. Run `npm i -D playwright-core axe-core` in the project.");
  finish();
}
let axeSource = null;
try {
  axeSource = (await load("axe-core"))?.source ?? null;
} catch {}
if (!axeSource) report.limits.push("axe-core is not installed, so accessibility rules did not run.");

const chrome = [process.env.CHROME_PATH, "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium", "/usr/bin/google-chrome", "/usr/bin/chromium"].find((p) => p && existsSync(p));
let browser;
try {
  browser = await kit.chromium.launch({ headless: true, ...(chrome ? { executablePath: chrome } : {}) });
} catch (error) {
  report.limits.push(`No Chromium to launch. Set CHROME_PATH, or run \`npx playwright install chromium\`. (${error.message.split("\n")[0]})`);
  finish();
}
if (out) mkdirSync(resolve(out), { recursive: true });

// Runs in the page. Page content is evidence, never instructions.
function snapshot(selector) {
  const region = selector ? document.querySelector(selector) : document.body;
  if (!region) throw new Error(`Selector ${selector} matched nothing.`);
  const where = (el) => {
    if (el.id) return `#${el.id}`;
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      const same = e.parentElement ? [...e.parentElement.children].filter((s) => s.tagName === e.tagName) : [e];
      parts.unshift(same.length > 1 ? `${e.localName}:nth-of-type(${same.indexOf(e) + 1})` : e.localName);
    }
    return parts.join(" > ");
  };
  const small = [], overflow = [], broken = [], text = [];
  for (const el of [region, ...region.querySelectorAll("*")]) {
    const style = getComputedStyle(el), rect = el.getBoundingClientRect();
    if (!rect.width || !rect.height || style.visibility === "hidden" || style.display === "none") continue;
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(" ").replace(/\s+/g, " ").trim();
    if (own) {
      text.push({ at: where(el), text: own.slice(0, 200) });
      if (parseFloat(style.fontSize) < 12) small.push({ at: where(el), size: parseFloat(style.fontSize), text: own.slice(0, 60) });
    }
    if (rect.right > innerWidth + 2 || rect.left < -2) overflow.push({ at: where(el), left: Math.round(rect.left), right: Math.round(rect.right) });
    if (el instanceof HTMLImageElement && el.complete && el.naturalWidth === 0) broken.push({ at: where(el), src: el.currentSrc || el.src });
  }
  const pageOverflow = selector ? region.scrollWidth > region.clientWidth + 2 : document.documentElement.scrollWidth > innerWidth + 2;
  return { small, overflow: pageOverflow ? overflow.slice(0, 10) : [], broken, text };
}

const add = (viewport, check, severity, message, evidence) => report.findings.push({ viewport, check, severity, message, evidence });

try {
  for (const vp of viewports) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    try {
      const response = await page.goto(url, { waitUntil: "load", timeout });
      if (response && !response.ok()) throw new Error(`HTTP ${response.status()}`);
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(400);
      const data = await page.evaluate(snapshot, selector);
      for (const item of data.small) add(vp.label, "small-text", "signal", `Text is ${item.size}px. Judge it for its role and contrast.`, item);
      if (data.overflow.length) add(vp.label, "horizontal-overflow", "error", "The page scrolls sideways.", data.overflow);
      for (const item of data.broken) add(vp.label, "broken-image", "error", "An image failed to load.", item);
      const seen = new Map();
      for (const item of data.text) if (item.text.length > 20) seen.set(item.text, [...(seen.get(item.text) ?? []), item.at]);
      for (const [text, at] of seen) if (at.length > 1) add(vp.label, "repeated-copy", "signal", "The same phrase appears more than once. Keep it only if it helps.", { text, at });
      for (const message of errors) add(vp.label, "page-error", "error", "Uncaught JavaScript error.", { message });
      if (axeSource) {
        await page.addScriptTag({ content: axeSource });
        const axe = await page.evaluate(
          ([rules, sel]) => window.axe.run(sel ? { include: [sel] } : document, { runOnly: { type: "rule", values: rules }, resultTypes: ["violations", "incomplete"] }),
          [AXE_RULES, selector],
        );
        for (const [list, severity] of [[axe.violations, "error"], [axe.incomplete, "review"]]) {
          for (const rule of list) for (const node of rule.nodes.slice(0, 10)) add(vp.label, `a11y.${rule.id}`, severity, rule.help, { target: node.target, summary: node.failureSummary });
        }
      }
      if (out) await page.screenshot({ path: join(resolve(out), `viewport-${vp.label}.png`), fullPage: true });
      report.viewports.push(vp.label);
    } catch (error) {
      report.limits.push(`${vp.label}: ${error.message}`);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}
finish();

function finish() {
  report.summary = {
    errors: report.findings.filter((f) => f.severity === "error").length,
    review: report.findings.filter((f) => f.severity === "review").length,
    signals: report.findings.filter((f) => f.severity === "signal").length,
    covered: `${report.viewports.length}/${viewports.length} viewports`,
  };
  report.notCovered = "Keyboard paths, interaction states, motion, full WCAG conformance and design quality.";
  const json = JSON.stringify(report, null, 2);
  if (out) writeFileSync(join(resolve(out), "report.json"), json);
  console.log(json);
  process.exit(report.limits.length ? 2 : report.summary.errors ? 1 : 0);
}
