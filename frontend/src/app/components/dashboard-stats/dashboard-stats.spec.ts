import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardStatsComponent } from './dashboard-stats';

describe('DashboardStatsComponent', () => {
  let component: DashboardStatsComponent;
  let fixture: ComponentFixture<DashboardStatsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardStatsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardStatsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
