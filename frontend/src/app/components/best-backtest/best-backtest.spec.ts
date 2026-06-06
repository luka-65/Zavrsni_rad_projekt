import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BestBacktest } from './best-backtest';

describe('BestBacktest', () => {
  let component: BestBacktest;
  let fixture: ComponentFixture<BestBacktest>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BestBacktest],
    }).compileComponents();

    fixture = TestBed.createComponent(BestBacktest);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
