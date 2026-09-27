import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BestBacktestComponent } from './best-backtest';

describe('Simulacija s najvećim povratom (BestBacktestComponent)', () => {
  let fixture: ComponentFixture<BestBacktestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BestBacktestComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(BestBacktestComponent);
    await fixture.whenStable();
  });

  it('ne prikazuje ništa dok nema spremljenih simulacija', () => {
    expect((fixture.nativeElement as HTMLElement).textContent?.trim()).toBe('');
  });

  it('prikazuje simulaciju s preciznim naslovom, razdobljem i parametrima', async () => {
    fixture.componentRef.setInput('bestBacktest', {
      strategy: 'Moving Average Crossover', symbol: 'ETHUSDT', interval: '1d',
      start_date: '2024-05-02', end_date: '2025-06-10', return_pct: 50.62,
      created_at: '2026-09-26 10:00:00', parameters: { short_window: 20, long_window: 50 }
    });
    await fixture.whenStable();

    const text = (fixture.nativeElement as HTMLElement).textContent?.replace(/\s+/g, ' ') ?? '';
    expect(text).toContain('Simulacija s najvećim zabilježenim povratom');
    expect(text).not.toContain('Najbolje testiranje');
    expect(text).toContain('Križanje pomičnih prosjeka');
    expect(text).toContain('1d, 2024-05-02 – 2025-06-10');
    expect(text).toContain('Parametri: Kratki prozor: 20, Dugi prozor: 50');
  });
});
