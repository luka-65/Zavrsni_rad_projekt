import { Component, Input } from '@angular/core';
import { MISSING_PARAMETERS_TEXT, strategyParameterRows } from '../../utils/strategy-parameters';
import { SIMULATION_ASSUMPTIONS, hadOpenPositionAtEnd } from '../../utils/simulation-model';
import { BacktestResponse } from '../../models';

@Component({
  selector: 'app-result-cards',
  imports: [],
  templateUrl: './result-cards.html',
  styleUrl: './result-cards.css'
})
export class ResultCardsComponent {
  @Input() result: BacktestResponse | null = null;

  readonly missingParametersText = MISSING_PARAMETERS_TEXT;
  readonly assumptions = SIMULATION_ASSUMPTIONS;

  get hadOpenPositionAtEnd() {
    return hadOpenPositionAtEnd(this.result?.result);
  }

  get parameterRows() {
    return strategyParameterRows(this.result?.parameters);
  }

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
