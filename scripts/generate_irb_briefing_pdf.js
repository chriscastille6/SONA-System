/*
 * Generates IRB_BRIEFING_JULIANN_JON.pdf from IRB_BRIEFING_JULIANN_JON.html
 * Mirrors the Psychological Assessments FERPA PDF workflow (Puppeteer).
 * Run: node scripts/generate_irb_briefing_pdf.js
 * Requires: npm install puppeteer (in scripts/ or repo root)
 */

const path = require('path');
const { pathToFileURL } = require('url');
const puppeteer = require('puppeteer');

const scriptDir = path.resolve(__dirname);
const repoRoot = path.resolve(scriptDir, '..');
const htmlPath = path.join(repoRoot, 'IRB_BRIEFING_JULIANN_JON.html');
const outputPath = path.join(repoRoot, 'IRB_BRIEFING_JULIANN_JON.pdf');
const fileUrl = pathToFileURL(htmlPath).href;

async function main() {
  const browser = await puppeteer.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });
    await new Promise((r) => setTimeout(r, 400));
    await page.pdf({
      path: outputPath,
      printBackground: true,
      margin: { top: '14mm', right: '14mm', bottom: '14mm', left: '14mm' },
    });
    console.log('Saved:', outputPath);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
