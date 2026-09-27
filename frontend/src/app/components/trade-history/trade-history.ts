import { Component, Input } from '@angular/core';
import { DatePipe } from '@angular/common';
import { BacktestResponse, Trade } from '../../models';

@Component({
  selector: 'app-trade-history',
  imports: [DatePipe],
  templateUrl: './trade-history.html',
  styleUrl: './trade-history.css'
})
export class TradeHistoryComponent {
  @Input() result: BacktestResponse | null = null;

  formatTradeType(trade: Trade) {
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

  isBuyTrade(trade: Trade) {
    return trade?.type === 'BUY' || trade?.type === 'buy';
  }

  isSellTrade(trade: Trade) {
    return trade?.type === 'SELL' || trade?.type === 'sell';
  }
}
