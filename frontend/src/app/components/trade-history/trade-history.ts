import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-trade-history',
  imports: [],
  templateUrl: './trade-history.html',
  styleUrl: './trade-history.css'
})
export class TradeHistoryComponent {
  @Input() result: any = null;

  formatTradeType(type: string) {
    if (type === 'BUY' || type === 'buy') {
      return 'Kupnja';
    }

    if (type === 'SELL' || type === 'sell') {
      return 'Prodaja';
    }

    return type;
  }
}
