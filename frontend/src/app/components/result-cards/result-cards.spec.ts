import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultCards } from './result-cards';

describe('ResultCards', () => {
  let component: ResultCards;
  let fixture: ComponentFixture<ResultCards>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResultCards],
    }).compileComponents();

    fixture = TestBed.createComponent(ResultCards);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
