import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimulationFormComponent } from './simulation-form';

describe('Obrazac simulacije (SimulationFormComponent)', () => {
  let fixture: ComponentFixture<SimulationFormComponent>;

  const labels = () =>
    Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('label')).map((label) => label.textContent?.trim());

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimulationFormComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SimulationFormComponent);
    await fixture.whenStable();
  });

  it('prikazuje samo polja parametara odabrane strategije', async () => {
    const cases: [string, string[], string[]][] = [
      ['moving-average', ['Kratki pomični prosjek', 'Dugi pomični prosjek'], ['Granica preprodanosti', 'Standardna devijacija']],
      ['rsi', ['Razdoblje indeksa relativne snage', 'Granica preprodanosti', 'Granica prekupljenosti'], ['Kratki pomični prosjek']],
      ['bollinger', ['Razdoblje Bollingerovih ovojnica', 'Standardna devijacija'], ['Granica prekupljenosti']]
    ];

    for (const [strategy, shown, hidden] of cases) {
      fixture.componentRef.setInput('strategy', strategy);
      await fixture.whenStable();
      expect(labels()).toEqual(expect.arrayContaining(shown));
      for (const label of hidden) {
        expect(labels()).not.toContain(label);
      }
    }
  });

  it('prikazuje poruku validacije i onemogućuje pokretanje', async () => {
    fixture.componentRef.setInput('formValidationMessage', 'Prvo odaberi kriptovalutu iz pretrage.');
    fixture.componentRef.setInput('canRunBacktest', false);
    await fixture.whenStable();

    const element = fixture.nativeElement as HTMLElement;
    const runButton = Array.from(element.querySelectorAll('button'))
      .find((button) => button.textContent?.includes('Pokreni simulaciju'));
    expect(element.querySelector('.form-help')?.textContent).toContain('Prvo odaberi kriptovalutu');
    expect(runButton?.disabled).toBe(true);
  });
});
