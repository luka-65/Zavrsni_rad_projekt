import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-strategy-comparison',
  imports: [],
  templateUrl: './strategy-comparison.html',
  styleUrl: './strategy-comparison.css'
})
export class StrategyComparisonComponent {
  @Input() compareResults: any[] = [];
  @Input() bestStrategy: any = null;
}