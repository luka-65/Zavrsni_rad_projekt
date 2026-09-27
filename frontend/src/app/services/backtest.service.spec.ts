import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { BacktestService } from './backtest.service';
import { BacktestRequest } from '../models';

describe('Servis simulacija (BacktestService)', () => {
  let service: BacktestService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(BacktestService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('pokreće simulaciju POST zahtjevom s JSON tijelom', () => {
    const request: BacktestRequest = {
      strategy: 'rsi',
      symbol: 'BTCUSDT',
      interval: '1d',
      initial_balance: 10000,
      start_date: '2025-01-01',
      end_date: '2025-12-31',
      parameters: { period: 14, oversold: 30, overbought: 70 }
    };

    service.runBacktest(request).subscribe();

    const call = http.expectOne('http://127.0.0.1:5000/api/backtests');
    expect(call.request.method).toBe('POST');
    expect(call.request.body).toEqual(request);
    call.flush({ status: 'success' });
  });

  it('traži usporedbu GET zahtjevom s parametrima u URL-u', () => {
    service.compareStrategies('ETHUSDT', '1w', 5000, '2025-01-01', '2025-06-30').subscribe();

    const call = http.expectOne((req) => req.url === 'http://127.0.0.1:5000/api/backtests/compare');
    expect(call.request.method).toBe('GET');
    expect(call.request.params.get('symbol')).toBe('ETHUSDT');
    expect(call.request.params.get('interval')).toBe('1w');
    expect(call.request.params.get('initial_balance')).toBe('5000');
    expect(call.request.params.get('start_date')).toBe('2025-01-01');
    expect(call.request.params.get('end_date')).toBe('2025-06-30');
    call.flush({ results: [] });
  });
});
