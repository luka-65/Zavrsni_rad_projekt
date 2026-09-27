import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { vi } from 'vitest';
import { App } from './app';
import { Simulation } from './models';

describe('Aplikacija (App)', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  const simulation = (id: number): Simulation => ({
    id, strategy: 'Relative Strength Index', symbol: 'BTCUSDT', interval: '1d',
    initial_balance: 10000, final_balance: 10500, return_pct: 5, max_drawdown_pct: 2,
    win_rate_pct: 100, number_of_trades: 1, start_date: '2025-01-01', end_date: '2025-02-01',
    parameters: { period: 14, oversold: 30, overbought: 70 }, created_at: '2026-09-26 10:00:00'
  });

  async function answerStartupRequests() {
    await new Promise((resolve) => setTimeout(resolve));
    const http = TestBed.inject(HttpTestingController);
    const urls = http.match(() => true).map((request) => {
      request.flush({ status: 'success', data: request.request.url.endsWith('/simulations') ? [] : null });
      return request.request.url;
    });
    http.verify();
    return urls;
  }

  it('pri pokretanju učitava povijest, sažetak i simulaciju s najvećim povratom', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    expect(fixture.componentInstance).toBeTruthy();
    expect(await answerStartupRequests()).toEqual([
      'http://127.0.0.1:5000/api/simulations',
      'http://127.0.0.1:5000/api/dashboard-stats',
      'http://127.0.0.1:5000/api/best-backtest'
    ]);
  });

  it('prikazuje naslov aplikacije', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Simulator trgovanja kriptovalutama');
    await answerStartupRequests();
  });

  it('prikazuje poruku backenda kad Binance ne odgovori tijekom usporedbe', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await answerStartupRequests();

    const alert = vi.spyOn(window, 'alert').mockImplementation(() => {});
    const app = fixture.componentInstance;
    app.result = {
      strategy: 'Relative Strength Index', symbol: 'BTCUSDT', interval: '1d',
      result: { initial_balance: 10000, final_balance: 10000, return_pct: 0, max_drawdown_pct: 0,
                win_rate_pct: 0, number_of_trades: 0, trades: [] }
    };
    app.symbol = 'BTCUSDT';
    app.compareStrategies();

    const message = 'Binance nije odgovorio na vrijeme. Pokušajte ponovno za nekoliko trenutaka.';
    TestBed.inject(HttpTestingController)
      .expectOne((request) => request.url.includes('/api/backtests/compare'))
      .flush({ status: 'error', message }, { status: 504, statusText: 'Gateway Timeout' });

    expect(alert).toHaveBeenCalledWith(message);
    expect(app.compareResults).toEqual([]);
    alert.mockRestore();
    await answerStartupRequests();
  });

  it('šalje odabranu strategiju i njezine parametre jednim POST zahtjevom', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await answerStartupRequests();

    const app = fixture.componentInstance;
    Object.assign(app, {
      symbol: 'ETHUSDT', strategy: 'rsi', interval: '1w', initialBalance: 2500,
      startDate: '2025-01-01', endDate: '2025-12-31', rsiPeriod: 10, oversold: 20, overbought: 80
    });
    app.runBacktest();

    const call = TestBed.inject(HttpTestingController).expectOne('http://127.0.0.1:5000/api/backtests');
    expect(call.request.method).toBe('POST');
    expect(call.request.body).toEqual({
      strategy: 'rsi', symbol: 'ETHUSDT', interval: '1w', initial_balance: 2500,
      start_date: '2025-01-01', end_date: '2025-12-31',
      parameters: { period: 10, oversold: 20, overbought: 80 }
    });
    call.flush({
      status: 'success', id: 5, strategy: 'Relative Strength Index', symbol: 'ETHUSDT', interval: '1w',
      parameters: { period: 10, oversold: 20, overbought: 80 },
      result: {
        initial_balance: 2500, final_balance: 2600, return_pct: 4, max_drawdown_pct: 3, win_rate_pct: 100,
        number_of_trades: 1, had_open_position_at_end: false, trades: [],
        chart_data: { timestamps: [1, 2], prices: [100, 104] }
      }
    },
      { status: 201, statusText: 'Created' });

    expect(app.result?.id).toBe(5);
    expect(app.activeTab).toBe('results');
    await answerStartupRequests();
  });

  it('ne šalje zahtjev dok obrazac nije ispravan', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await answerStartupRequests();

    const alert = vi.spyOn(window, 'alert').mockImplementation(() => {});
    const app = fixture.componentInstance;
    Object.assign(app, { symbol: '', startDate: '2025-01-01', endDate: '2025-02-01' });
    expect(app.formValidationMessage).toBe('Prvo odaberi kriptovalutu iz pretrage.');

    app.symbol = 'BTCUSDT';
    Object.assign(app, { startDate: '2025-03-01', endDate: '2025-02-01' });
    expect(app.formValidationMessage).toBe('Datum do ne može biti prije datuma od.');

    Object.assign(app, { interval: '1h', startDate: '2025-01-01', endDate: '2025-06-01' });
    expect(app.formValidationMessage).toBe('Za interval 1h moguće je odabrati najviše 90 dana.');

    app.runBacktest();
    expect(alert).toHaveBeenCalledWith('Za interval 1h moguće je odabrati najviše 90 dana.');
    TestBed.inject(HttpTestingController).expectNone('http://127.0.0.1:5000/api/backtests');
    alert.mockRestore();
    await answerStartupRequests();
  });

  it('briše simulaciju tek nakon potvrde i ponovno učitava povijest', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await answerStartupRequests();

    const http = TestBed.inject(HttpTestingController);
    const app = fixture.componentInstance;
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false);
    app.simulations = [simulation(1), simulation(2)];

    app.deleteSimulation(1);
    http.expectNone('http://127.0.0.1:5000/api/simulations/1');
    expect(app.simulations.length).toBe(2);

    confirm.mockReturnValue(true);
    app.deleteSimulation(1);
    expect(app.simulations).toEqual([simulation(2)]);
    const call = http.expectOne('http://127.0.0.1:5000/api/simulations/1');
    expect(call.request.method).toBe('DELETE');
    call.flush({ status: 'success' });

    expect(await answerStartupRequests()).toEqual([
      'http://127.0.0.1:5000/api/simulations',
      'http://127.0.0.1:5000/api/dashboard-stats',
      'http://127.0.0.1:5000/api/best-backtest'
    ]);
    confirm.mockRestore();
  });

  it('pri otvaranju simulacije iz povijesti vraća spremljene parametre u obrazac', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await answerStartupRequests();

    const app = fixture.componentInstance;
    app.loadSimulationDetails(7);
    TestBed.inject(HttpTestingController).expectOne('http://127.0.0.1:5000/api/simulations/7').flush({
      status: 'success',
      data: {
        id: 7,
        strategy: 'Relative Strength Index',
        symbol: 'ETHUSDT',
        interval: '1w',
        initial_balance: 2500,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        parameters: { period: 10, oversold: 20, overbought: 80 },
        result: { initial_balance: 2500, trades: [], chart_data: null }
      }
    });

    expect(app.strategy).toBe('rsi');
    expect(app.initialBalance).toBe(2500);
    expect([app.rsiPeriod, app.oversold, app.overbought]).toEqual([10, 20, 80]);
    expect(app.result?.parameters).toEqual({ period: 10, oversold: 20, overbought: 80 });
    await answerStartupRequests();
  });
});
