import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { StrategyChartComponent } from './strategy-chart';

describe('Graf strategije (StrategyChartComponent)', () => {
  let component: StrategyChartComponent;
  let fixture: ComponentFixture<StrategyChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrategyChartComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()]
    }).compileComponents();

    fixture = TestBed.createComponent(StrategyChartComponent);
    component = fixture.componentInstance;
  });

  it('za stariju simulaciju bez snimke grafa dohvaća podatke sa spremljenim parametrima', async () => {
    fixture.componentRef.setInput('strategy', 'rsi');
    fixture.componentRef.setInput('result', {
      symbol: 'BTCUSDT', interval: '1w', start_date: '2025-05-18', end_date: '2026-05-19',
      parameters: { period: 10, oversold: 20, overbought: 80 },
      result: { trades: [] }
    });
    await fixture.whenStable();

    const call = TestBed.inject(HttpTestingController).expectOne((request) => request.url.includes('/api/chart/rsi'));
    const url = new URL(call.request.url);
    expect(url.searchParams.get('symbol')).toBe('BTCUSDT');
    expect(url.searchParams.get('period')).toBe('10');
    expect(url.searchParams.get('oversold')).toBe('20');
    expect(url.searchParams.get('overbought')).toBe('80');
    expect(url.searchParams.get('end_date')).toBe('2026-05-19');

    call.flush({ message: 'Binance nije dostupan' }, { status: 502, statusText: 'Bad Gateway' });
    await fixture.whenStable();
    expect(component.legacy()).toBe(true);
    expect(component.error()).toBe('Podatke grafa nije moguće učitati.');
  });

  it('označava prisilno zatvaranje na kraju razdoblja drugačije od obične prodaje', () => {
    const trade = { type: 'SELL', price: 100, profit_pct: 5 } as any;
    expect(component.tradeLabel({ ...trade, is_final_close: false })).toBe('Prodaja');
    expect(component.tradeLabel({ ...trade, is_final_close: true })).toBe('Prodaja na kraju razdoblja');
    expect(component.tradeLabel({ ...trade, type: 'BUY' })).toBe('Kupnja');
  });
});
