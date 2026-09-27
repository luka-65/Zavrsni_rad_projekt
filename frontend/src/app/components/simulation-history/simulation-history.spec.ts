import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimulationHistoryComponent } from './simulation-history';

describe('Povijest simulacija (SimulationHistoryComponent)', () => {
  let fixture: ComponentFixture<SimulationHistoryComponent>;

  const simulation = (id: number, parameters: Record<string, number> | null) => ({
    id,
    created_at: '2026-09-26 10:00:00',
    strategy: 'Relative Strength Index',
    symbol: 'BTCUSDT',
    interval: '1d',
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    initial_balance: 10000,
    final_balance: 11000,
    return_pct: 10,
    win_rate_pct: 50,
    parameters
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimulationHistoryComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SimulationHistoryComponent);
    await fixture.whenStable();
  });

  it('prikazuje spremljene parametre svake simulacije', async () => {
    fixture.componentRef.setInput('simulations', [
      simulation(1, { period: 14, oversold: 30, overbought: 70 }),
      simulation(2, { period: 10, oversold: 20, overbought: 80 })
    ]);
    await fixture.whenStable();

    const cells = Array.from(
      (fixture.nativeElement as HTMLElement).querySelectorAll('td.parameters')
    ).map((cell) =>
      Array.from(cell.querySelectorAll('div')).map((line) => line.textContent?.trim())
    );

    expect(cells).toEqual([
      ['RSI period: 14', 'Granica preprodanosti: 30', 'Granica prekupljenosti: 70'],
      ['RSI period: 10', 'Granica preprodanosti: 20', 'Granica prekupljenosti: 80']
    ]);
  });

  it('označava starije simulacije spremljene bez parametara', async () => {
    fixture.componentRef.setInput('simulations', [simulation(3, null)]);
    await fixture.whenStable();

    const cell = (fixture.nativeElement as HTMLElement).querySelector('td.parameters');
    expect(cell?.textContent).toContain('Nisu spremljeni');
  });
});
