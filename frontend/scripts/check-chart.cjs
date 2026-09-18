// PLAYWRIGHT_MODULE can point to a separate installation of the browser test tool.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const path = require('node:path');

const times = Array.from({ length: 150 }, (_, i) => Date.UTC(2024, 0, 1) + i * 86400000);
const prices = times.map((_, i) => 100 + i / 3 + Math.sin(i / 5) * 12);
const trades = [20, 50, 80, 149].map((i, n) => ({
  type: n % 2 ? 'SELL' : 'BUY', price: prices[i], timestamp: times[i], candle_index: i,
  profit_pct: n % 2 ? 12.34 : null, is_final_close: n === 3
}));
const result = {
  initial_balance: 10000, final_balance: 12000, return_pct: 20,
  max_drawdown_pct: 5, win_rate_pct: 100, number_of_trades: 2, trades,
  chart_data: { timestamps: times, prices, ma_short: prices.map(p => p - 2), ma_long: prices.map(p => p - 5) }
};
let simulation = { id: 1, strategy: 'Moving Average Crossover', symbol: 'ETHUSDT', interval: '1d',
  start_date: '2024-01-01', end_date: '2024-05-29', created_at: '2024-06-01', ...result, result };
let legacyRequests = 0;
let failLegacy = false;

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error' && message.text().includes('NG0')) errors.push(message.text()); });
    await page.route('**/api/**', route => {
      const url = new URL(route.request().url());
      let response;
      if (url.pathname === '/api/dashboard-stats') response = { data: { total_simulations: 1, best_roi: 20, most_traded_symbol: 'ETHUSDT', most_used_strategy: simulation.strategy } };
      else if (url.pathname === '/api/best-backtest') response = { data: simulation };
      else if (url.pathname === '/api/simulations') response = { data: [simulation] };
      else if (url.pathname === '/api/simulations/1') response = { data: simulation };
      else if (url.pathname.startsWith('/api/chart/')) {
        legacyRequests++;
        if (failLegacy) return route.fulfill({ status: 500, json: { message: 'Test failure' } });
        response = result.chart_data;
      } else response = {};
      return route.fulfill({ json: response, headers: { 'Access-Control-Allow-Origin': '*' } });
    });
    const chart = page.locator('app-strategy-chart');
    const getBounds = () => chart.evaluate(el => {
      const c = window.ng.getComponent(el).chart;
      return { min: c.scales.x.min, max: c.scales.x.max, datasets: c.data.datasets.length };
    });
    const openResult = async () => {
      await page.getByRole('button', { name: 'Povijest', exact: true }).click();
      await page.getByRole('button', { name: 'Detalji', exact: true }).click();
      await page.getByRole('button', { name: 'Približi', exact: true }).waitFor();
      await page.waitForFunction(() => !document.querySelector('button[aria-label="Približi"]')?.disabled);
      await chart.scrollIntoViewIfNeeded();
    };
    await page.goto('http://127.0.0.1:4201');
    await openResult();
    const original = await getBounds();
    assert.equal(original.min, times[0]);
    assert.equal(original.max, times.at(-1));
    assert.equal(original.datasets, 6);
    await page.getByRole('button', { name: 'Približi', exact: true }).click();
    const zoomed = await getBounds();
    assert.ok(zoomed.max - zoomed.min < original.max - original.min);
    await page.getByRole('button', { name: 'Cijelo razdoblje' }).click();
    assert.deepEqual(await getBounds(), original);
    await page.locator('#chart-trade').selectOption('1');
    assert.match(await chart.locator('.trade-detail').innerText(), /12.34%/);
    assert.ok((await getBounds()).max - (await getBounds()).min < original.max - original.min);
    await page.getByRole('button', { name: 'Sljedeća transakcija' }).click();
    assert.equal(await page.locator('#chart-trade').inputValue(), '2');
    await page.getByRole('button', { name: 'Prethodna transakcija' }).click();
    assert.equal(await page.locator('#chart-trade').inputValue(), '1');
    await page.getByRole('button', { name: 'Cijelo razdoblje' }).click();
    const point = await chart.evaluate(el => {
      const c = window.ng.getComponent(el).chart;
      const idx = c.data.datasets.findIndex(d => d.label === 'Kupnja');
      const p = c.getDatasetMeta(idx).data[0];
      const rect = c.canvas.getBoundingClientRect();
      return { x: rect.x + p.x, y: rect.y + p.y };
    });
    await page.mouse.click(point.x, point.y);
    await page.waitForFunction(() => document.querySelector('#chart-trade')?.value === '0');
    assert.equal(await page.locator('#chart-trade').inputValue(), '0');
    const canvas = chart.locator('canvas');
    const rect = await canvas.boundingBox();
    await page.mouse.move(rect.x + rect.width / 2, rect.y + rect.height / 2);
    await page.mouse.wheel(0, -400);
    await page.waitForTimeout(300);
    const wheelZoomed = await getBounds();
    assert.ok(wheelZoomed.max - wheelZoomed.min < original.max - original.min);
    await page.mouse.down();
    await page.mouse.move(rect.x + rect.width / 2 + 80, rect.y + rect.height / 2, { steps: 12 });
    await page.mouse.up();
    await page.waitForTimeout(100);
    assert.notEqual((await getBounds()).min, wheelZoomed.min);
    const coloredPixels = await canvas.evaluate(el => {
      const data = el.getContext('2d').getImageData(0, 0, el.width, el.height).data;
      let pixels = 0;
      for (let i = 3; i < data.length; i += 4) if (data[i] > 0) pixels++;
      return pixels;
    });
    assert.ok(coloredPixels > 1000);
    assert.equal(await page.locator('app-trade-history td').first().evaluate(el => getComputedStyle(el).color), 'rgb(248, 250, 252)');
    await chart.screenshot({ path: path.join(process.env.TEMP, 'crypto-chart-desktop.png') });
    await page.getByRole('button', { name: 'Usporedba strategija', exact: true }).click();
    await page.getByRole('button', { name: 'Rezultati', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('button[aria-label="Približi"]')?.disabled);
    assert.equal((await getBounds()).datasets, 6);
    assert.equal(legacyRequests, 0);

    for (const width of [800, 390]) {
      await page.setViewportSize({ width, height: 900 });
      await chart.scrollIntoViewIfNeeded();
      await page.waitForTimeout(300);
      const box = await canvas.boundingBox();
      assert.ok(box.width > 200 && box.x >= 0 && box.x + box.width <= width + 1);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
      await page.locator('#chart-trade').selectOption('3');
      assert.match(await chart.locator('.trade-detail').innerText(), /Prodaja na kraju razdoblja/);
      await chart.screenshot({ path: path.join(process.env.TEMP, 'crypto-chart-' + width + '.png') });
    }
    await page.setViewportSize({ width: 1440, height: 1000 });
    for (const [strategy, series, expectedAxis] of [
      ['Relative Strength Index', { rsi: prices.map((_, i) => 50 + Math.sin(i / 5) * 35), oversold: times.map(() => 30), overbought: times.map(() => 70) }, true],
      ['Bollinger Bands', { upper_band: prices.map(p => p + 10), middle_band: prices, lower_band: prices.map(p => p - 10) }, false]
    ]) {
      simulation = { ...simulation, strategy, result: { ...result, chart_data: { timestamps: times, prices, ...series } } };
      await openResult();
      assert.equal(await chart.evaluate(el => !!window.ng.getComponent(el).chart.scales.rsi), expectedAxis);
    }
    simulation = { ...simulation, result: { ...result, trades: [], chart_data: result.chart_data } };
    await openResult();
    assert.match(await chart.innerText(), /nema izvršenih transakcija/);

    simulation = { ...simulation, result: { ...result, chart_data: undefined, trades: trades.map(({ timestamp, candle_index, ...trade }) => trade) } };
    await openResult();
    assert.match(await chart.locator('.notice').innerText(), /Starija simulacija/);
    assert.equal(await page.locator('#chart-trade').count(), 0);
    assert.equal((await getBounds()).datasets, 3);
    failLegacy = true;
    await page.getByRole('button', { name: 'Povijest', exact: true }).click();
    await page.getByRole('button', { name: 'Detalji', exact: true }).click();
    await page.getByRole('button', { name: 'Pokušaj ponovno' }).waitFor();
    failLegacy = false;
    await page.getByRole('button', { name: 'Pokušaj ponovno' }).click();
    await page.waitForFunction(() => !document.querySelector('button[aria-label="Približi"]')?.disabled);
    assert.deepEqual(errors, []);
    console.log('PASS: zoom, wheel, pan, markers, transaction navigation, tab remount, all strategies, empty/legacy/error states, desktop/mobile canvas and text contrast.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
