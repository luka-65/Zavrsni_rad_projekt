import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StrategyComparison } from './strategy-comparison';

describe('StrategyComparison', () => {
  let component: StrategyComparison;
  let fixture: ComponentFixture<StrategyComparison>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrategyComparison],
    }).compileComponents();

    fixture = TestBed.createComponent(StrategyComparison);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
