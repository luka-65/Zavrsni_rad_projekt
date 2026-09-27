import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultCardsComponent } from './result-cards';

describe('Rezultati simulacije (ResultCardsComponent)', () => {
  let component: ResultCardsComponent;
  let fixture: ComponentFixture<ResultCardsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResultCardsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ResultCardsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  const result = (flags: Record<string, boolean>) => ({
    strategy: 'Relative Strength Index',
    symbol: 'BTCUSDT',
    parameters: { period: 14, oversold: 30, overbought: 70 },
    result: {
      initial_balance: 10000,
      final_balance: 8467,
      return_pct: -15.33,
      max_drawdown_pct: 20,
      win_rate_pct: 0,
      number_of_trades: 1,
      ...flags
    }
  });

  const text = () => (fixture.nativeElement as HTMLElement).textContent?.replace(/\s+/g, ' ') ?? '';

  it('objašnjava poziciju prisilno zatvorenu na kraju razdoblja', async () => {
    fixture.componentRef.setInput('result', result({ had_open_position_at_end: true }));
    await fixture.whenStable();

    expect(text()).toContain('Pozicija otvorena na kraju razdoblja');
    expect(text()).toContain('Zatvorena po posljednjoj dostupnoj cijeni');
  });

  it('čita stari naziv open_position kod ranije spremljenih simulacija', async () => {
    fixture.componentRef.setInput('result', result({ open_position: true }));
    await fixture.whenStable();
    expect(component.hadOpenPositionAtEnd).toBe(true);

    fixture.componentRef.setInput('result', result({ had_open_position_at_end: false }));
    await fixture.whenStable();
    expect(component.hadOpenPositionAtEnd).toBe(false);
    expect(text()).not.toContain('Zatvorena po posljednjoj dostupnoj cijeni');
  });

  it('prikazuje pretpostavke modela simulacije', async () => {
    fixture.componentRef.setInput('result', result({ had_open_position_at_end: false }));
    await fixture.whenStable();

    expect(text()).toContain('Pretpostavke simulacije');
    expect(text()).toContain('istog OHLCV zapisa na kojem je signal nastao');
    expect(text()).toContain('Nisu uključene transakcijske naknade, spread ni slippage');
  });

  it('prikazuje početni kapital i parametre strategije', async () => {
    fixture.componentRef.setInput('result', {
      strategy: 'Bollinger Bands',
      symbol: 'ETHUSDT',
      parameters: { window: 15, num_std: 2.5 },
      result: {
        initial_balance: 5000,
        final_balance: 5200,
        return_pct: 4,
        max_drawdown_pct: 3,
        win_rate_pct: 50,
        number_of_trades: 2,
        had_open_position_at_end: false
      }
    });
    await fixture.whenStable();

    const text = (fixture.nativeElement as HTMLElement)
      .querySelector('.parameters-card')?.textContent?.replace(/\s+/g, ' ');

    expect(text).toContain('Početni kapital: 5000 USDT');
    expect(text).toContain('Prozor: 15');
    expect(text).toContain('Broj standardnih devijacija: 2.5');
  });
});
