import { Component, Input } from '@angular/core';
import { formatStrategyParameters } from '../../utils/strategy-parameters';
import { StrategyComparisonResult } from '../../models';

@Component({
  selector: 'app-strategy-comparison',
  imports: [],
  templateUrl: './strategy-comparison.html',
  styleUrl: './strategy-comparison.css'
})
export class StrategyComparisonComponent {
  @Input() compareResults: StrategyComparisonResult[] = [];
  @Input() bestStrategy: StrategyComparisonResult | null = null;

  readonly formatParameters = formatStrategyParameters;

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
