import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardStatsComponent } from './dashboard-stats';

describe('Sažetak nadzorne ploče (DashboardStatsComponent)', () => {
  let fixture: ComponentFixture<DashboardStatsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardStatsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardStatsComponent);
    await fixture.whenStable();
  });

  it('prikazuje sažetak spremljenih simulacija s preciznim nazivima', async () => {
    fixture.componentRef.setInput('dashboardStats', {
      total_simulations: 12, best_roi: 50.62,
      most_used_strategy: 'Relative Strength Index', most_traded_symbol: 'BTCUSDT'
    });
    await fixture.whenStable();

    const cards = Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('.dashboard-card'))
      .map((card) => [card.querySelector('h3')?.textContent?.trim(), card.querySelector('p')?.textContent?.trim()]);

    expect(cards).toEqual([
      ['Ukupno simulacija', '12'],
      ['Najčešća strategija', 'Indeks relativne snage'],
      ['Najveći zabilježeni povrat', '50.62%'],
      ['Najtrgovaniji simbol', 'BTCUSDT']
    ]);
  });
});
