import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Chart } from 'chart.js/auto';

import { BacktestService } from './services/backtest.service';
import { ChartDataService } from './services/chart.service';
import { SimulationService } from './services/simulation.service';
import { SymbolService } from './services/symbol.service';
import { PdfService } from './services/pdf.service';
import { ResultCardsComponent } from './components/result-cards/result-cards';
import { TradeHistoryComponent } from './components/trade-history/trade-history';
import { StrategyComparisonComponent } from './components/strategy-comparison/strategy-comparison';
import { StrategyChartComponent } from './components/strategy-chart/strategy-chart';
import { SimulationHistoryComponent } from './components/simulation-history/simulation-history';
import { SimulationFormComponent } from './components/simulation-form/simulation-form';
import { DashboardStatsComponent } from './components/dashboard-stats/dashboard-stats';
import { BestBacktestComponent } from './components/best-backtest/best-backtest';


@Component({
  selector: 'app-root',
  imports: [FormsModule, FormsModule,
  ResultCardsComponent,
  TradeHistoryComponent, StrategyComparisonComponent,
StrategyChartComponent,
SimulationHistoryComponent, SimulationFormComponent,DashboardStatsComponent,
BestBacktestComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  result: any = null;
  chart: any = null;
  simulations: any[] = [];

  compareResults: any[] = [];
  compareChart: any = null;
  bestStrategy: any = null;
  dashboardStats: any = null;
  bestBacktest: any = null;

  symbolSearch = '';
  symbolResults: any[] = [];

  symbol = 'BTCUSDT';
  strategy = 'moving-average';
  interval = '1d';
  initialBalance = 10000;

  activeTab = 'simulation';

  shortWindow = 20;
  longWindow = 50;

  rsiPeriod = 14;
  oversold = 30;
  overbought = 70;

  bollingerWindow = 20;
  numStd = 2;

  constructor(
    private backtestService: BacktestService,
    private chartDataService: ChartDataService,
    private simulationService: SimulationService,
    private symbolService: SymbolService,
    private pdfService: PdfService
  ) {}

  ngOnInit() {
    this.loadSimulations();
    this.loadDashboardStats();
    this.loadBestBacktest();
  }

  getStrategyEndpoint() {
    if (this.strategy === 'rsi') {
      return 'rsi';
    }

    if (this.strategy === 'bollinger') {
      return 'bollinger';
    }

    return 'moving-average';
  }

  getStrategyParams() {
    if (this.strategy === 'moving-average') {
      return `&short_window=${this.shortWindow}&long_window=${this.longWindow}`;
    }

    if (this.strategy === 'rsi') {
      return `&period=${this.rsiPeriod}&oversold=${this.oversold}&overbought=${this.overbought}`;
    }

    if (this.strategy === 'bollinger') {
      return `&window=${this.bollingerWindow}&num_std=${this.numStd}`;
    }

    return '';
  }

  runBacktest() {
    const endpoint = this.getStrategyEndpoint();
    const params = this.getStrategyParams();

    this.backtestService
      .runBacktest(
        endpoint,
        this.symbol,
        this.interval,
        this.initialBalance,
        params
      )
      .subscribe((data) => {
        this.result = data;
        this.activeTab = 'results';
        this.loadSimulations();
        this.loadDashboardStats();
        this.loadBestBacktest();

        setTimeout(() => {
          this.loadChart();
        }, 300);
      });
  }

  compareStrategies() {
    this.backtestService
      .compareStrategies(this.symbol, this.interval, this.initialBalance)
      .subscribe((response) => {
        this.compareResults = response.results;
        this.activeTab = 'compare';

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

  loadBestBacktest() {
  this.simulationService
    .getBestBacktest()
    .subscribe((response) => {
      this.bestBacktest = response.data;
    });
}

  loadDashboardStats() {
  this.simulationService
    .getDashboardStats()
    .subscribe((response) => {
      this.dashboardStats = response.data;
    });
}

  loadSimulations() {
    this.simulationService.getSimulations().subscribe((response) => {
      this.simulations = response.data;
    });
  }

  loadChart() {
    const endpoint = this.getStrategyEndpoint();
    const params = this.getStrategyParams();

    this.chartDataService
      .getChartData(endpoint, this.symbol, this.interval, params)
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
                { label: 'Cijena', data: chartData.prices },
                { label: 'MA Short', data: chartData.ma_short },
                { label: 'MA Long', data: chartData.ma_long }
              ]
             },
            options: {
              responsive: false,
              maintainAspectRatio: false
            }
          });
        }

        if (this.strategy === 'rsi') {
          this.chart = new Chart(canvas, {
            type: 'line',
            data: {
              labels: chartData.rsi.map((_: any, i: number) => i + 1),
              datasets: [
                { label: 'RSI', data: chartData.rsi },
                { label: 'Oversold', data: chartData.oversold },
                { label: 'Overbought', data: chartData.overbought }
              ]
             },
            options: {
              responsive: false,
              maintainAspectRatio: false
            }
          });
        }

        if (this.strategy === 'bollinger') {
          this.chart = new Chart(canvas, {
            type: 'line',
            data: {
              labels: chartData.prices.map((_: any, i: number) => i + 1),
              datasets: [
                { label: 'Cijena', data: chartData.prices },
                { label: 'Upper Band', data: chartData.upper_band },
                { label: 'Middle Band', data: chartData.middle_band },
                { label: 'Lower Band', data: chartData.lower_band }
              ]
             },
            options: {
              responsive: false,
              maintainAspectRatio: false
            }
          });
        }
      });
  }


  downloadPdf() {
    this.pdfService.downloadSimulationPdf(this.result, this.strategy);
  }

  searchSymbols() {
    if (this.symbolSearch.length < 2) {
      this.symbolResults = [];
      return;
    }

    this.symbolService.searchSymbols(this.symbolSearch).subscribe((response) => {
      this.symbolResults = response.data;
    });
  }

  selectSymbol(symbol: string) {
    this.symbol = symbol;
    this.symbolSearch = symbol;
    this.symbolResults = [];
  }

  loadSimulationDetails(id: number) {
  this.simulationService
    .getSimulationById(id)
    .subscribe((response) => {
      const simulation = response.data;

      if (!simulation.result) {
        alert('Detalji nisu dostupni za ovu stariju simulaciju.');
        return;
      }

      this.result = {
        status: 'success',
        strategy: simulation.strategy,
        symbol: simulation.symbol,
        interval: simulation.interval,
        result: simulation.result
      };
    
      this.symbol = simulation.symbol;
      this.interval = simulation.interval;
      this.strategy = this.mapStrategyToFrontend(simulation.strategy);

      this.activeTab = 'results';

      setTimeout(() => {
        this.loadChart();
      }, 600);
    });
}

mapStrategyToFrontend(strategyName: string): string {
  if (strategyName === 'Moving Average Crossover') {
    return 'moving-average';
  }

  if (strategyName === 'Relative Strength Index') {
    return 'rsi';
  }

  if (strategyName === 'Bollinger Bands') {
    return 'bollinger';
  }

  return 'moving-average';
}
}