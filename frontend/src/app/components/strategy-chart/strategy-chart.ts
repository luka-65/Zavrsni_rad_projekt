import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-strategy-chart',
  imports: [],
  templateUrl: './strategy-chart.html',
  styleUrl: './strategy-chart.css'
})
export class StrategyChartComponent {
  @Input() strategy = '';
  @Input() result: any = null;
}