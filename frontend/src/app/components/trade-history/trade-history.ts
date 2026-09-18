import { Component, Input } from '@angular/core';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-trade-history',
  imports: [DatePipe],
  templateUrl: './trade-history.html',
  styleUrl: './trade-history.css'
})
export class TradeHistoryComponent {
  @Input() result: any = null;

  formatTradeType(trade: any) {
    if (trade?.is_final_close) {
      return 'Prodaja na kraju razdoblja';
    }

    const type = trade?.type;

    if (type === 'BUY' || type === 'buy') {
      return 'Kupnja';
    }

    if (type === 'SELL' || type === 'sell') {
      return 'Prodaja';
    }

    return type;
  }

  isBuyTrade(trade: any) {
    return trade?.type === 'BUY' || trade?.type === 'buy';
  }

  isSellTrade(trade: any) {
    return trade?.type === 'SELL' || trade?.type === 'sell';
  }
}
