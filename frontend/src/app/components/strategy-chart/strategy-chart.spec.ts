import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StrategyChart } from './strategy-chart';

describe('StrategyChart', () => {
  let component: StrategyChart;
  let fixture: ComponentFixture<StrategyChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrategyChart],
    }).compileComponents();

    fixture = TestBed.createComponent(StrategyChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
