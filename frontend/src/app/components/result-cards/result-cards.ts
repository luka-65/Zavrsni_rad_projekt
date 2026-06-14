import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-result-cards',
  imports: [],
  templateUrl: './result-cards.html',
  styleUrl: './result-cards.css'
})
export class ResultCardsComponent {
  @Input() result: any = null;

  formatStrategyName(strategyName: string) {
    if (strategyName === 'Moving Average Crossover') {
      return 'Križanje pomičnih prosjeka';
    }

    if (strategyName === 'Relative Strength Index') {
      return 'Indeks relativne snage';
    }

    if (strategyName === 'Bollinger Bands') {
      return 'Bollingerove ovojnice';
    }

    return strategyName;
  }
}
