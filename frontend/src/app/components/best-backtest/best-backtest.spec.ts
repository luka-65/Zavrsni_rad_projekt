import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BestBacktestComponent } from './best-backtest';

describe('BestBacktestComponent', () => {
  let component: BestBacktestComponent;
  let fixture: ComponentFixture<BestBacktestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BestBacktestComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(BestBacktestComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
