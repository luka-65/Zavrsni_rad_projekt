import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StrategyComparisonComponent } from './strategy-comparison';

describe('Usporedba strategija (StrategyComparisonComponent)', () => {
  let fixture: ComponentFixture<StrategyComparisonComponent>;

  const row = (strategy: string, parameters: Record<string, number>, returnPct: number) => ({
    strategy, parameters, return_pct: returnPct, final_balance: 10000 + returnPct * 100,
    max_drawdown_pct: 5, win_rate_pct: 50, number_of_trades: 2
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrategyComparisonComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(StrategyComparisonComponent);
    await fixture.whenStable();
  });

  it('prikazuje fiksne referentne parametre i precizan naziv za najveći povrat', async () => {
    const results = [
      row('Moving Average Crossover', { short_window: 20, long_window: 50 }, -3),
      row('Relative Strength Index', { period: 14, oversold: 30, overbought: 70 }, -1.5),
      row('Bollinger Bands', { window: 20, num_std: 2 }, -8)
    ];
    fixture.componentRef.setInput('compareResults', results);
    fixture.componentRef.setInput('bestStrategy', results[1]);
    await fixture.whenStable();

    const element = fixture.nativeElement as HTMLElement;
    const parameterCells = Array.from(element.querySelectorAll('td.parameters')).map((cell) => cell.textContent?.trim());
    expect(parameterCells).toEqual([
      'Kratki prozor: 20, Dugi prozor: 50',
      'RSI period: 14, Granica preprodanosti: 30, Granica prekupljenosti: 70',
      'Prozor: 20, Broj standardnih devijacija: 2'
    ]);
    expect(element.textContent).toContain('a ne parametre iz obrasca');
    expect(element.textContent).toContain('Najveći povrat u ovoj usporedbi');
    expect(element.textContent).not.toContain('Najbolja strategija');
  });
});
