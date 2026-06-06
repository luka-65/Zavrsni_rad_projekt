import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-best-backtest',
  imports: [],
  templateUrl: './best-backtest.html',
  styleUrl: './best-backtest.css'
})
export class BestBacktestComponent {
  @Input() bestBacktest: any = null;
}