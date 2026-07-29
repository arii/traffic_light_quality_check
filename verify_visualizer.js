const { chromium } = require('@playwright/test');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    recordVideo: {
      dir: '/home/jules/verification/videos',
      size: { width: 1280, height: 800 }
    },
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  const reportPath = path.resolve('traffic_light_quality_check/results/report_output.html');
  const fileUrl = `file://${reportPath}`;
  console.log(`Opening visualizer report at ${fileUrl}`);

  await page.goto(fileUrl);
  await page.waitForTimeout(1500);

  // 1. Click on the first finding card
  const firstFinding = page.locator('#findings-list-container > div').first();
  if (await firstFinding.isVisible()) {
    console.log('Clicking first finding card to highlight the bounding box.');
    await firstFinding.click();
    await page.waitForTimeout(1000);
  }

  // 2. Switch to the Boxes & Attributes tab
  console.log('Switching to Boxes & Attributes tab.');
  await page.locator('#tab-btn-boxes').click();
  await page.waitForTimeout(1000);

  // 3. Click on the first annotation card
  const firstAnn = page.locator('#pane-boxes > div').first();
  if (await firstAnn.isVisible()) {
    console.log('Clicking first annotation card.');
    await firstAnn.click();
    await page.waitForTimeout(1000);
  }

  // 4. Switch to the Task JSON tab
  console.log('Switching to Task JSON tab.');
  await page.locator('#tab-btn-raw').click();
  await page.waitForTimeout(1000);

  // 5. Switch back to Quality Findings tab
  console.log('Switching back to Quality Findings tab.');
  await page.locator('#tab-btn-findings').click();
  await page.waitForTimeout(1000);

  // 6. Apply filter to show only Warnings
  console.log('Filtering to warnings only.');
  await page.locator('#filter-warning-btn').click();
  await page.waitForTimeout(1000);

  // Take screenshot of the final filtered state
  const screenshotPath = '/home/jules/verification/screenshots/verification.png';
  await page.screenshot({ path: screenshotPath });
  console.log(`Screenshot saved to ${screenshotPath}`);
  await page.waitForTimeout(1000);

  await context.close();
  await browser.close();
  console.log('Verification run complete.');
})();
