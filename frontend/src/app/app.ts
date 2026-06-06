import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Chart } from 'chart.js/auto';
import { OnInit } from '@angular/core';
import jsPDF from 'jspdf';

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {

  result: any = null;
  chart: any = null;
  simulations: any[] = [];
  compareResults: any[] = [];
  compareChart: any = null;
  interval = '1d';
  bestStrategy: any = null;
  symbolSearch = '';
  symbolResults: any[] = [];

  symbol = 'BTCUSDT';
  strategy = 'moving-average';
  initialBalance = 10000;

  constructor(private http: HttpClient) {}

  ngOnInit() {
  this.loadSimulations();
}

  runBacktest() {

    let endpoint = 'moving-average';

    if (this.strategy === 'rsi') {
      endpoint = 'rsi';
    }

    if (this.strategy === 'bollinger') {
      endpoint = 'bollinger';
    }

    this.http
      .get(
        `http://127.0.0.1:5000/api/backtest/${endpoint}?symbol=${this.symbol}&interval=${this.interval}&initial_balance=${this.initialBalance}`
      )
      .subscribe((data) => {
  this.result = data;
  this.loadSimulations();

  if (
  this.strategy === 'moving-average' ||
  this.strategy === 'rsi' ||
  this.strategy === 'bollinger'
) {
  setTimeout(() => {
    this.loadChart();
  }, 300);
} else {
  if (this.chart) {
    this.chart.destroy();
    this.chart = null;
  }
}
});
  }

  compareStrategies() {
  this.http
    .get<any>(
      `http://127.0.0.1:5000/api/backtest/compare?symbol=${this.symbol}&interval=${this.interval}&initial_balance=${this.initialBalance}`
    )
    .subscribe((response) => {
      this.compareResults = response.results;
      this.bestStrategy = this.compareResults.reduce((best, current) =>
  current.return_pct > best.return_pct ? current : best
);
      setTimeout(() => {
  this.loadCompareChart();
}, 1000);
    });
}

loadCompareChart() {
  const canvas = document.getElementById('compareChart') as HTMLCanvasElement | null;

  if (!canvas) {
    return;
  }

  if (this.compareChart) {
    this.compareChart.destroy();
  }

  this.compareChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: this.compareResults.map((item) => item.strategy),
      datasets: [
        {
          label: 'ROI (%)',
          data: this.compareResults.map((item) => item.return_pct)
        }
      ]
    }
  });
}

  loadSimulations() {
  this.http
    .get<any>('http://127.0.0.1:5000/api/simulations')
    .subscribe((response) => {
      this.simulations = response.data;
    });
}

 loadChart() {

  let chartEndpoint = 'moving-average';

if (this.strategy === 'rsi') {
  chartEndpoint = 'rsi';
}

if (this.strategy === 'bollinger') {
  chartEndpoint = 'bollinger';
}

  this.http
    .get<any>(
      `http://127.0.0.1:5000/api/chart/${chartEndpoint}?symbol=${this.symbol}&interval=${this.interval}`
    )
    .subscribe((chartData) => {

      const canvas = document.getElementById('priceChart') as HTMLCanvasElement | null;

if (!canvas) {
  return;
}

if (this.chart) {
  this.chart.destroy();
}

      if (this.strategy === 'moving-average') {

        this.chart = new Chart(canvas, {
          type: 'line',
          data: {
            labels: chartData.prices.map((_: any, i: number) => i + 1),
            datasets: [
              {
                label: 'Cijena',
                data: chartData.prices
              },
              {
                label: 'MA Short',
                data: chartData.ma_short
              },
              {
                label: 'MA Long',
                data: chartData.ma_long
              }
            ]
          }
        });

      } else if (this.strategy === 'rsi') {

        this.chart = new Chart(canvas, {
          type: 'line',
          data: {
            labels: chartData.rsi.map((_: any, i: number) => i + 1),
            datasets: [
              {
                label: 'RSI',
                data: chartData.rsi
              },
              {
                label: 'Oversold (30)',
                data: chartData.oversold
              },
              {
                label: 'Overbought (70)',
                data: chartData.overbought
              }
            ]
          }
          
        });
        

      }else if (this.strategy === 'bollinger') {

  this.chart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: chartData.prices.map((_: any, i: number) => i + 1),
      datasets: [
        {
          label: 'Cijena',
          data: chartData.prices
        },
        {
          label: 'Upper Band',
          data: chartData.upper_band
        },
        {
          label: 'Middle Band',
          data: chartData.middle_band
        },
        {
          label: 'Lower Band',
          data: chartData.lower_band
        }
      ]
    }
  });

}

    });
}

downloadPdf() {
  if (!this.result) {
    return;
  }

  const doc = new jsPDF();

  const today = new Date().toLocaleString('hr-HR');

  doc.setFillColor(15, 23, 42);
  doc.rect(0, 0, 210, 28, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(18);
  doc.text('Crypto Trading Simulator', 10, 12);

  doc.setFontSize(11);
  doc.text('Izvještaj simulacije trgovanja kriptovalutama', 10, 20);

  doc.setTextColor(0, 0, 0);
  doc.setFontSize(12);

  doc.text(`Datum izrade: ${today}`, 10, 40);
  doc.text(`Vrijeme generiranja izvjestaja: ${today}`, 10, 40);
  doc.text(`Strategija: ${this.result.strategy}`, 10, 52);
  doc.text(`Simbol: ${this.result.symbol}`, 10, 64);
  doc.text(`Interval: ${this.result.interval}`, 10, 76);

  doc.setFontSize(14);
  doc.text('Rezultati simulacije', 10, 95);

  doc.setFontSize(12);

  const rows = [
    ['Pocetni kapital', `${this.result.result.initial_balance} USDT`],
    ['Zavrsni kapital', `${this.result.result.final_balance} USDT`],
    ['Ukupni povrat', `${this.result.result.return_pct}%`],
    ['Max Drawdown', `${this.result.result.max_drawdown_pct}%`],
    ['Win Rate', `${this.result.result.win_rate_pct}%`],
    ['Broj transakcija', `${this.result.result.number_of_trades}`]
  ];

  let y = 108;

  rows.forEach((row) => {
    doc.setFillColor(241, 245, 249);
    doc.rect(10, y - 7, 90, 10, 'F');

    doc.setFillColor(226, 232, 240);
    doc.rect(100, y - 7, 90, 10, 'F');

    doc.text(row[0], 13, y);
    doc.text(row[1], 103, y);

    y += 12;
  });

  doc.setFontSize(10);
  doc.setTextColor(90, 90, 90);
  doc.text(
    'Napomena: Rezultati predstavljaju simulacijsko testiranje nad povijesnim podacima i ne predstavljaju financijski savjet.',
    10,
    190,
    { maxWidth: 185 }
  );

  const fileName = `izvjestaj_${this.result.symbol}_${this.strategy}.pdf`;

  doc.save(fileName);
}


searchSymbols() {
  if (this.symbolSearch.length < 2) {
    this.symbolResults = [];
    return;
  }

  this.http
    .get<any>(
      `http://127.0.0.1:5000/api/symbols/search?query=${this.symbolSearch}`
    )
    .subscribe((response) => {
      this.symbolResults = response.data;
    });
}

selectSymbol(symbol: string) {
  this.symbol = symbol;
  this.symbolSearch = symbol;
  this.symbolResults = [];
}

}

