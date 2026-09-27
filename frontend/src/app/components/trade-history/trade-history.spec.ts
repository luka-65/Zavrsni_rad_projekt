import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TradeHistoryComponent } from './trade-history';

describe('Popis transakcija (TradeHistoryComponent)', () => {
  let fixture: ComponentFixture<TradeHistoryComponent>;

  const rows = () => Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('tbody tr'))
    .map((row) => Array.from(row.querySelectorAll('td')).map((cell) => cell.textContent?.trim()));

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TradeHistoryComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TradeHistoryComponent);
    await fixture.whenStable();
  });

  it('prikazuje kupnje, prodaje i prisilno zatvaranje na kraju razdoblja u UTC vremenu', async () => {
    fixture.componentRef.setInput('result', { result: { trades: [
      { type: 'BUY', price: 100, profit_pct: null, timestamp: Date.UTC(2025, 0, 6, 23, 59), is_final_close: false },
      { type: 'SELL', price: 110, profit_pct: 10, timestamp: Date.UTC(2025, 0, 13, 23, 59), is_final_close: false },
      { type: 'BUY', price: 105, profit_pct: null, timestamp: Date.UTC(2025, 0, 20, 23, 59), is_final_close: false },
      { type: 'SELL', price: 99, profit_pct: -5.71, timestamp: Date.UTC(2025, 0, 27, 23, 59), is_final_close: true }
    ] } });
    await fixture.whenStable();

    expect(rows()).toEqual([
      ['Kupnja', '06.01.2025. 23:59', '100', '-'],
      ['Prodaja', '13.01.2025. 23:59', '110', '10'],
      ['Kupnja', '20.01.2025. 23:59', '105', '-'],
      ['Prodaja na kraju razdoblja', '27.01.2025. 23:59', '99', '-5.71']
    ]);
  });

  it('ne prikazuje tablicu kad simulacija nema transakcija', async () => {
    fixture.componentRef.setInput('result', { result: { trades: [] } });
    await fixture.whenStable();

    expect((fixture.nativeElement as HTMLElement).querySelector('table')).toBeNull();
  });
});
