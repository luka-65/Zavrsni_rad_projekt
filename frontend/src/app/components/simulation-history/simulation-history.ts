import { Component, EventEmitter, Input, Output } from '@angular/core';
@Component({
  selector: 'app-simulation-history',
  imports: [],
  templateUrl: './simulation-history.html',
  styleUrl: './simulation-history.css'
})
export class SimulationHistoryComponent {
  @Input() simulations: any[] = [];
  @Output() selectSimulationEvent = new EventEmitter<number>();
  @Output() deleteSimulationEvent = new EventEmitter<number>();

  exportCsv() {
    const headers = [
      'ID',
      'Datum',
      'Strategija',
      'Simbol',
      'Interval',
      'Razdoblje od',
      'Razdoblje do',
      'Početni kapital',
      'Završni kapital',
      'Povrat (%)',
      'Najveći pad (%)',
      'Stopa dobitnih transakcija (%)',
      'Broj zatvorenih transakcija'
    ];

    const rows = this.simulations.map((simulation) => [
      simulation.id,
      simulation.created_at,
      this.formatStrategyName(simulation.strategy),
      simulation.symbol,
      simulation.interval,
      simulation.start_date,
      simulation.end_date,
      simulation.initial_balance,
      simulation.final_balance,
      simulation.return_pct,
      simulation.max_drawdown_pct,
      simulation.win_rate_pct,
      simulation.number_of_trades
    ]);

    const csv = [headers, ...rows]
      .map((row) => row.map((value) => this.escapeCsvValue(value)).join(','))
      .join('\r\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = `povijest-simulacija-${this.getToday()}.csv`;
    link.click();

    URL.revokeObjectURL(url);
  }

  private escapeCsvValue(value: any) {
    if (value === null || value === undefined) {
      return '';
    }

    const stringValue = String(value);
    const escapedValue = stringValue.replace(/"/g, '""');

    if (/[",\r\n]/.test(escapedValue)) {
      return `"${escapedValue}"`;
    }

    return escapedValue;
  }

  private getToday() {
    return new Date().toISOString().slice(0, 10);
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
