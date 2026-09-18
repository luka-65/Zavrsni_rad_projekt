import { FormsModule } from '@angular/forms';
import { Chart } from 'chart.js/auto';
import { Component, OnInit, ChangeDetectorRef, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

import { BacktestService } from './services/backtest.service';
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
import { finalize } from 'rxjs';


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
  dashboardChart: any = null;
  simulations: any[] = [];

  compareResults: any[] = [];
  compareChart: any = null;
  bestStrategy: any = null;
  dashboardStats: any = null;
  bestBacktest: any = null;

  symbolSearch = '';
  symbolResults: any[] = [];

  symbol = '';
  strategy = 'moving-average';
  interval = '1d';
  initialBalance = 10000;
  startDate = '';
  endDate = '';

  activeTab = 'dashboard';
  isLoading = false;
  isBrowser = false;

  shortWindow = 20;
  longWindow = 50;

  rsiPeriod = 14;
  oversold = 30;
  overbought = 70;

  bollingerWindow = 20;
  numStd = 2;

  constructor(
  private backtestService: BacktestService,
  private simulationService: SimulationService,
  private symbolService: SymbolService,
  private pdfService: PdfService,
  private cdr: ChangeDetectorRef,
  @Inject(PLATFORM_ID) private platformId: Object
) {
  this.isBrowser = isPlatformBrowser(this.platformId);
  Chart.defaults.color = '#f8fafc';
  Chart.defaults.borderColor = '#475569';
}

  ngOnInit() {
  if (this.isBrowser) {
    const savedStrategy = localStorage.getItem('strategy');
    const savedInterval = localStorage.getItem('interval');

    localStorage.removeItem('lastResult');
    localStorage.removeItem('activeTab');

    if (savedStrategy) {
      this.strategy = savedStrategy;
    }

    if (savedInterval) {
      this.interval = savedInterval;
    }

    setTimeout(() => {
      this.loadSimulations();
      this.loadDashboardStats();
      this.loadBestBacktest();
    });
  }
}

setActiveTab(tab: string) {
  this.activeTab = tab;

  if (tab === 'dashboard') {
    setTimeout(() => {
      this.loadDashboardChart();
    });
  }


  if (tab === 'compare' && this.compareResults.length > 0) {
    setTimeout(() => {
      this.loadCompareChart();
    });
  }
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
    const dateParams = this.getDateParams();

    if (this.strategy === 'moving-average') {
      return `&short_window=${this.shortWindow}&long_window=${this.longWindow}${dateParams}`;
    }

    if (this.strategy === 'rsi') {
      return `&period=${this.rsiPeriod}&oversold=${this.oversold}&overbought=${this.overbought}${dateParams}`;
    }

    if (this.strategy === 'bollinger') {
      return `&window=${this.bollingerWindow}&num_std=${this.numStd}${dateParams}`;
    }

    return dateParams;
  }

  getDateParams() {
    if (!this.startDate || !this.endDate) {
      return '';
    }

    return `&start_date=${this.startDate}&end_date=${this.endDate}`;
  }

  runBacktest() {
  if (this.isLoading) {
    return;
  }

  if (!this.canRunBacktest) {
    alert(this.formValidationMessage);
    return;
  }

  this.isLoading = true;

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
    .pipe(
      finalize(() => {
        this.isLoading = false;
      })
    )
    .subscribe({
      next: (data) => {
        this.isLoading = false;
        this.result = data;
        this.activeTab = 'results';

        if (this.isBrowser) {
          localStorage.setItem('strategy', this.strategy);
          localStorage.setItem('interval', this.interval);
        }

        this.loadSimulations();
        this.loadDashboardStats();
        this.loadBestBacktest();
        this.cdr.detectChanges();

      },
      error: (error) => {
        console.error(error);
        alert('Došlo je do greške pri pokretanju simulacije.');
      }
    });
}



  compareStrategies() {
      if (!this.result) {
    alert('Prvo pokreni simulaciju.');
    return;
  }
    this.backtestService
      .compareStrategies(
        this.symbol,
        this.interval,
        this.initialBalance,
        this.startDate,
        this.endDate
      )
      .subscribe((response) => {
        this.compareResults = response.results;
        this.bestStrategy = this.compareResults.reduce((best, current) =>
          current.return_pct > best.return_pct ? current : best
        );

        this.activeTab = 'compare';
        this.cdr.detectChanges();
        setTimeout(() => {
          this.loadCompareChart();
        });
      });
  }

  loadCompareChart() {
    const canvas = document.getElementById('compareChart') as HTMLCanvasElement | null;

    if (!canvas) {
        console.warn('compareChart canvas nije pronađen');
        return;
    }

    if (this.compareChart) {
      this.compareChart.destroy();
    }

    this.compareChart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: this.compareResults.map((item) => this.formatStrategyName(item.strategy)),
        datasets: [
          {
            label: 'Povrat (%)',
            data: this.compareResults.map((item) => item.return_pct),
            backgroundColor: '#38bdf8',
            borderColor: '#bae6fd',
            borderWidth: 1,
            hoverBackgroundColor: '#7dd3fc'
          }
        ]
      },
      options: {
        color: '#f8fafc',
        plugins: {
          legend: { labels: { color: '#f8fafc' } },
          tooltip: {
            backgroundColor: '#111827',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: '#64748b',
            borderWidth: 1
          }
        },
        scales: {
          x: {
            ticks: { color: '#f8fafc' },
            grid: { color: '#475569' },
            border: { color: '#94a3b8' }
          },
          y: {
            beginAtZero: true,
            ticks: { color: '#f8fafc' },
            grid: { color: '#475569' },
            border: { color: '#94a3b8' }
          }
        }
      }
    });
  }

  loadBestBacktest() {
  this.simulationService
    .getBestBacktest()
    .subscribe((response) => {
      this.bestBacktest = response.data;
      this.cdr.markForCheck();
    });
}

  loadDashboardStats() {
  this.simulationService
    .getDashboardStats()
    .subscribe((response) => {
      this.dashboardStats = response.data;
      this.cdr.markForCheck();
    });
}

  loadSimulations() {
    this.simulationService.getSimulations().subscribe((response) => {
      this.simulations = response.data;

      if (this.activeTab === 'dashboard') {
        this.cdr.detectChanges();
        setTimeout(() => {
          this.loadDashboardChart();
        });
      }
    });
  }

  get topSimulations() {
    return [...this.simulations]
      .sort((first, second) => second.return_pct - first.return_pct)
      .slice(0, 5);
  }

  get roiTrendSimulations() {
    return [...this.simulations]
      .sort((first, second) =>
        new Date(first.created_at).getTime() - new Date(second.created_at).getTime()
      )
      .slice(-10);
  }

  get averageRoiByStrategy() {
    const grouped = new Map<string, { total: number; count: number }>();

    this.simulations.forEach((simulation) => {
      const current = grouped.get(simulation.strategy) || {
        total: 0,
        count: 0
      };

      current.total += Number(simulation.return_pct);
      current.count += 1;

      grouped.set(simulation.strategy, current);
    });

    return Array.from(grouped.entries())
      .map(([strategy, values]) => ({
        strategy,
        averageRoi: Number((values.total / values.count).toFixed(2)),
        count: values.count
      }))
      .sort((first, second) => second.averageRoi - first.averageRoi);
  }

  getAverageRoiBarWidth(averageRoi: number) {
    const maxAverage = Math.max(
      ...this.averageRoiByStrategy.map((item) => Math.abs(item.averageRoi)),
      1
    );

    return `${Math.max((Math.abs(averageRoi) / maxAverage) * 100, 6)}%`;
  }

  formatStrategyName(strategyName: string) {
    if (strategyName === 'Moving Average Crossover' || strategyName === 'moving-average') {
      return 'Križanje pomičnih prosjeka';
    }

    if (strategyName === 'Relative Strength Index' || strategyName === 'rsi') {
      return 'Indeks relativne snage';
    }

    if (strategyName === 'Bollinger Bands' || strategyName === 'bollinger') {
      return 'Bollingerove ovojnice';
    }

    return strategyName;
  }

  getRankLabel(index: number) {
    if (index === 0) {
      return '1';
    }

    if (index === 1) {
      return '2';
    }

    if (index === 2) {
      return '3';
    }

    return String(index + 1);
  }

  getRankClass(index: number) {
    if (index === 0) {
      return 'gold';
    }

    if (index === 1) {
      return 'silver';
    }

    if (index === 2) {
      return 'bronze';
    }

    return 'default';
  }

  loadDashboardChart(attempt = 0) {
    if (!this.isBrowser || this.roiTrendSimulations.length === 0) {
      if (this.dashboardChart) {
        this.dashboardChart.destroy();
        this.dashboardChart = null;
      }

      return;
    }

    const canvas = document.getElementById('dashboardRoiChart') as HTMLCanvasElement | null;

    if (!canvas) {
      if (attempt < 5) {
        setTimeout(() => {
          this.loadDashboardChart(attempt + 1);
        }, 100);
      }

      return;
    }

    if (this.dashboardChart) {
      this.dashboardChart.destroy();
    }

    this.dashboardChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: this.roiTrendSimulations.map((simulation) => simulation.created_at),
        datasets: [
          {
            label: 'Povrat (%)',
            data: this.roiTrendSimulations.map((simulation) => simulation.return_pct),
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.18)',
            fill: true,
            tension: 0.35
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#cbd5e1'
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#94a3b8',
              maxRotation: 0,
              autoSkip: true
            },
            grid: {
              color: '#334155'
            }
          },
          y: {
            ticks: {
              color: '#94a3b8'
            },
            grid: {
              color: '#334155'
            }
          }
        }
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

  updateSymbolSearch(value: string) {
    this.symbolSearch = value;

    if (value !== this.symbol) {
      this.symbol = '';
    }
  }

  get dateRangeError() {
    if (!this.startDate || !this.endDate) {
      return 'Odaberi datum od i datum do.';
    }

    const start = new Date(this.startDate);
    const end = new Date(this.endDate);

    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      return 'Odabrani datumi nisu ispravni.';
    }

    if (end < start) {
      return 'Datum do ne može biti prije datuma od.';
    }

    const today = new Date();
    today.setHours(23, 59, 59, 999);

    if (end > today) {
      return 'Datum do ne može biti u budućnosti.';
    }

    const days = Math.ceil(
      (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
    );
    const maxDays = this.getMaxRangeDays(this.interval);

    if (maxDays !== null && days > maxDays) {
      return `Za interval ${this.interval} moguće je odabrati najviše ${maxDays} dana.`;
    }

    return '';
  }

  get formValidationMessage() {
    if (!this.symbol.trim()) {
      return 'Prvo odaberi kriptovalutu iz pretrage.';
    }

    if (this.dateRangeError) {
      return this.dateRangeError;
    }

    return '';
  }

  getMaxRangeDays(interval: string) {
    const limits: Record<string, number> = {
      '1h': 90,
      '4h': 365,
      '1d': 1825,
      '1w': 3650,
      '1M': 3650
    };

    return limits[interval] ?? null;
  }

  get canRunBacktest() {
    return this.symbol.trim().length > 0 && !this.dateRangeError;
  }

  newSimulation() {
  this.result = null;
  this.compareResults = [];
  this.bestStrategy = null;

  this.symbolSearch = '';
  this.symbolResults = [];

  this.symbol = '';
  this.strategy = 'moving-average';
  this.interval = '1d';
  this.initialBalance = 10000;
  this.startDate = '';
  this.endDate = '';

  this.shortWindow = 20;
  this.longWindow = 50;

  this.rsiPeriod = 14;
  this.oversold = 30;
  this.overbought = 70;

  this.bollingerWindow = 20;
  this.numStd = 2;


  if (this.compareChart) {
    this.compareChart.destroy();
    this.compareChart = null;
  }

  if (this.isBrowser) {
    localStorage.removeItem('lastResult');
    localStorage.removeItem('symbol');
    localStorage.removeItem('strategy');
    localStorage.removeItem('interval');
    localStorage.removeItem('activeTab');
  }

  this.activeTab = 'simulation';
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
        start_date: simulation.start_date,
        end_date: simulation.end_date,
        result: simulation.result
      };
    
      this.symbol = simulation.symbol;
      this.interval = simulation.interval;
      this.startDate = simulation.start_date || '';
      this.endDate = simulation.end_date || '';
      this.strategy = this.mapStrategyToFrontend(simulation.strategy);

      this.activeTab = 'results';
      this.cdr.detectChanges();

    });
}

deleteSimulation(id: number) {
  const confirmed = confirm('Zelite li obrisati ovu simulaciju iz povijesti?');

  if (!confirmed) {
    return;
  }

  const previousSimulations = [...this.simulations];

  this.simulations = this.simulations.filter(
    (simulation) => Number(simulation.id) !== Number(id)
  );
  this.cdr.detectChanges();

  this.simulationService
    .deleteSimulation(id)
    .subscribe({
      next: () => {
        this.loadSimulations();
        this.loadDashboardStats();
        this.loadBestBacktest();

        if (this.activeTab === 'dashboard') {
          this.cdr.detectChanges();
          setTimeout(() => {
            this.loadDashboardChart();
          });
        }
      },
      error: (error) => {
        console.error(error);
        this.simulations = previousSimulations;
        this.cdr.detectChanges();
        alert('Doslo je do greske pri brisanju simulacije.');
      }
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
