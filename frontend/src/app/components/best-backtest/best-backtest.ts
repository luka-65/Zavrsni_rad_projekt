import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-best-backtest',
  imports: [],
  templateUrl: './best-backtest.html',
  styleUrl: './best-backtest.css'
})
export class BestBacktestComponent {
  @Input() bestBacktest: any = null;

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
