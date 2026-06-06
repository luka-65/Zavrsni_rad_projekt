import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-simulation-form',
  imports: [FormsModule],
  templateUrl: './simulation-form.html',
  styleUrl: './simulation-form.css'
})
export class SimulationFormComponent {
  @Input() symbolSearch = '';
  @Input() symbolResults: any[] = [];

  @Input() strategy = 'moving-average';
  @Input() interval = '1d';
  @Input() initialBalance = 10000;

  @Input() shortWindow = 20;
  @Input() longWindow = 50;

  @Input() rsiPeriod = 14;
  @Input() oversold = 30;
  @Input() overbought = 70;

  @Input() bollingerWindow = 20;
  @Input() numStd = 2;

  @Output() symbolSearchChange = new EventEmitter<string>();
  @Output() strategyChange = new EventEmitter<string>();
  @Output() intervalChange = new EventEmitter<string>();
  @Output() initialBalanceChange = new EventEmitter<number>();

  @Output() shortWindowChange = new EventEmitter<number>();
  @Output() longWindowChange = new EventEmitter<number>();

  @Output() rsiPeriodChange = new EventEmitter<number>();
  @Output() oversoldChange = new EventEmitter<number>();
  @Output() overboughtChange = new EventEmitter<number>();

  @Output() bollingerWindowChange = new EventEmitter<number>();
  @Output() numStdChange = new EventEmitter<number>();

  @Output() searchSymbolsEvent = new EventEmitter<void>();
  @Output() selectSymbolEvent = new EventEmitter<string>();
  @Output() runBacktestEvent = new EventEmitter<void>();
  @Output() compareStrategiesEvent = new EventEmitter<void>();
  @Output() downloadPdfEvent = new EventEmitter<void>();

  @Input() hasResult = false;
}