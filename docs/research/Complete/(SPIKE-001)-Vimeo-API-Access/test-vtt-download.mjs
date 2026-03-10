// SPIKE-001: Vimeo VTT download - player embed approach
// Load the Vimeo player embed with texttrack=en, intercept ALL network requests

import { chromium } from 'playwright';

const VIMEO_ID = '1152242786';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const allRequests = [];
  const interestingResponses = [];

  page.on('response', async (response) => {
    const url = response.url();
    const ct = response.headers()['content-type'] || '';
    allRequests.push({ url: url.substring(0, 120), status: response.status(), ct: ct.substring(0, 40) });

    // Capture anything that looks like it might have text track / VTT info
    if (url.includes('.vtt') || url.includes('text') || url.includes('caption') ||
        url.includes('subtitle') || url.includes('config') || url.includes('master.json')) {
      try {
        const text = await response.text();
        interestingResponses.push({
          url: url.substring(0, 150),
          status: response.status(),
          bodyPreview: text.substring(0, 300),
          hasTextTracks: text.includes('text_tracks'),
          hasWebvtt: text.includes('WEBVTT'),
        });
      } catch {}
    }
  });

  // Load player embed with texttrack=en to force captions
  const playerUrl = `https://player.vimeo.com/video/${VIMEO_ID}?texttrack=en`;
  console.log(`Loading: ${playerUrl}`);
  try {
    await page.goto(playerUrl, { waitUntil: 'domcontentloaded', timeout: 20000 });
    console.log('Page loaded, waiting 10s for player JS to initialize...');
    await page.waitForTimeout(10000);

    // Try clicking play to trigger caption loading
    try {
      await page.click('[aria-label="Play"]', { timeout: 3000 });
      console.log('Clicked play button, waiting 5s more...');
      await page.waitForTimeout(5000);
    } catch {
      console.log('No play button found or click failed. Trying alternative selectors...');
      try {
        await page.click('button.play', { timeout: 2000 });
        await page.waitForTimeout(5000);
      } catch {
        console.log('Could not click play. Continuing with what we have.');
      }
    }

    console.log(`\n--- All ${allRequests.length} requests ---`);
    for (const r of allRequests) {
      console.log(`  [${r.status}] ${r.ct} | ${r.url}`);
    }

    console.log(`\n--- ${interestingResponses.length} interesting responses ---`);
    for (const r of interestingResponses) {
      console.log(`\n  URL: ${r.url}`);
      console.log(`  Status: ${r.status}`);
      console.log(`  hasTextTracks: ${r.hasTextTracks}`);
      console.log(`  hasWebvtt: ${r.hasWebvtt}`);
      console.log(`  Preview: ${r.bodyPreview.substring(0, 200)}`);
    }

    // Also extract any config embedded in the player page HTML
    const pageContent = await page.content();
    const configMatch = pageContent.match(/window\.playerConfig\s*=\s*(\{[\s\S]*?\});/);
    if (configMatch) {
      console.log('\n--- Found window.playerConfig ---');
      try {
        const config = JSON.parse(configMatch[1]);
        const tt = config?.request?.text_tracks;
        if (tt) console.log('text_tracks:', JSON.stringify(tt, null, 2));
        else console.log('No text_tracks in playerConfig. Keys:', Object.keys(config?.request || {}));
      } catch {
        console.log('Could not parse playerConfig JSON');
      }
    }

    // Try another pattern - Vimeo sometimes uses a different variable name
    const altMatch = pageContent.match(/"text_tracks"\s*:\s*(\[[\s\S]*?\])/);
    if (altMatch) {
      console.log('\n--- Found text_tracks in page source ---');
      console.log(altMatch[0].substring(0, 500));
    }

  } catch (err) {
    console.log(`Error: ${err.message}`);
  }

  await browser.close();
})();
