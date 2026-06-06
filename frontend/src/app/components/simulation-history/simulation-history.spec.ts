import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimulationHistory } from './simulation-history';

describe('SimulationHistory', () => {
  let component: SimulationHistory;
  let fixture: ComponentFixture<SimulationHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimulationHistory],
    }).compileComponents();

    fixture = TestBed.createComponent(SimulationHistory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
