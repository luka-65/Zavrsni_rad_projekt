import { afterNextRender, Component, ElementRef, Inject, Input, OnChanges, OnDestroy, PLATFORM_ID, ViewChild, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Chart, ChartDataset, ChartOptions } from 'chart.js/auto';
import { Subscription } from 'rxjs';
import { LucideAngularModule, ZoomIn, ZoomOut, RotateCcw, ChevronLeft, ChevronRight } from 'lucide-angular';
import { ChartDataService } from '../../services/chart.service';
import type {} from 'chartjs-plugin-zoom';

interface ChartData {
  timestamps: number[];
  prices: number[];
  [key: string]: (number | null)[];
}
interface Trade {
  type: string;
  price: number;
  timestamp?: number;
  candle_index?: number;
  profit_pct: number | null;
  is_final_close?: boolean;
}
interface PlotPoint { x: number; y: number | null; tradeIndex?: number; }

@Component({
  selector: 'app-strategy-chart',
  imports: [LucideAngularModule],
  templateUrl: './strategy-chart.html',
  styleUrl: './strategy-chart.css'
})
export class StrategyChartComponent implements OnChanges, OnDestroy {
  @Input() strategy = '';
  @Input() result: any = null;
  @ViewChild('canvas') canvas!: ElementRef<HTMLCanvasElement>;
  readonly icons = { ZoomIn, ZoomOut, RotateCcw, ChevronLeft, ChevronRight };
  readonly loading = signal(true);
  readonly error = signal('');
  readonly selectedIndex = signal(-1);
  readonly visibleRange = signal('');
  readonly ready = signal(false);
  readonly legacy = signal(false);
  private chart?: Chart<'line', PlotPoint[]>;
  private data?: ChartData;
  private request?: Subscription;
  private viewReady = false;
  private generation = 0;
  private readonly dateFormat = new Intl.DateTimeFormat('hr-HR', {
    timeZone: 'UTC', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });

  constructor(private chartService: ChartDataService, @Inject(PLATFORM_ID) private platformId: object) {
    afterNextRender(() => { this.viewReady = true; this.load(); });
  }
  get trades(): Trade[] { return this.result?.result?.trades ?? []; }
  get selectedTrade(): Trade | undefined { return this.trades[this.selectedIndex()]; }
  get timedTrades() {
    return this.trades.map((trade, index) => ({ trade, index })).filter(item => Number.isFinite(item.trade.timestamp));
  }
  ngOnChanges() { if (this.viewReady) this.load(); }
  ngOnDestroy() {
    this.generation++;
    this.request?.unsubscribe();
    this.chart?.destroy();
  }

  load() {
    if (!isPlatformBrowser(this.platformId)) return;
    const generation = ++this.generation;
    this.request?.unsubscribe();
    this.chart?.destroy();
    this.chart = undefined;
    this.ready.set(false);
    this.loading.set(true);
    this.error.set('');
    this.visibleRange.set('');
    this.selectedIndex.set(-1);
    const snapshot = this.result?.result?.chart_data;
    this.legacy.set(!snapshot);
    if (snapshot) {
      void this.render(snapshot, generation);
      return;
    }
    const params = new URLSearchParams();
    for (const name of ['start_date', 'end_date', 'short_window', 'long_window', 'period', 'oversold', 'overbought', 'window', 'num_std']) {
      if (this.result?.[name] != null) params.set(name, String(this.result[name]));
    }
    this.request = this.chartService.getChartData(this.strategy, this.result.symbol, this.result.interval, '&' + params).subscribe({
      next: data => { void this.render(data, generation); },
      error: () => {
        this.loading.set(false);
        this.error.set('Podatke grafa nije moguće učitati.');
      }
    });
  }

  private async render(data: ChartData, generation: number) {
    try {
      const { default: zoomPlugin } = await import('chartjs-plugin-zoom');
      if (generation !== this.generation) return;
      if (!data.prices?.length || data.timestamps?.length !== data.prices.length) throw new Error('Missing chart timeline');
      Chart.register(zoomPlugin);
      this.data = data;
      const datasets: ChartDataset<'line', PlotPoint[]>[] = [];
      const addLine = (key: string, label: string, color: string, axis = 'y', dashed = false) => {
        if (!data[key]) return;
        datasets.push({
          label, data: data[key].map((y, i) => ({ x: data.timestamps[i], y })),
          borderColor: color, backgroundColor: color, borderWidth: 1.5,
          pointRadius: 0, pointHitRadius: 8, yAxisID: axis,
          borderDash: dashed ? [5, 5] : [], spanGaps: false, order: 2
        });
      };
      addLine('prices', 'Cijena', '#7dd3fc');
      addLine('ma_short', 'Kratki pomični prosjek', '#fbbf24');
      addLine('ma_long', 'Dugi pomični prosjek', '#c4b5fd');
      addLine('upper_band', 'Gornja ovojnica', '#c4b5fd');
      addLine('middle_band', 'Srednja ovojnica', '#fbbf24');
      addLine('lower_band', 'Donja ovojnica', '#5eead4');
      addLine('rsi', 'RSI', '#fbbf24', 'rsi');
      addLine('oversold', 'Granica preprodanosti', '#86efac', 'rsi', true);
      addLine('overbought', 'Granica prekupljenosti', '#fda4af', 'rsi', true);
      for (const [type, final, label, color] of [
        ['BUY', false, 'Kupnja', '#4ade80'],
        ['SELL', false, 'Prodaja', '#fb7185'],
        ['SELL', true, 'Prodaja na kraju razdoblja', '#fda4af']
      ] as const) {
        const points = this.timedTrades.filter(({ trade }) => trade.type.toUpperCase() === type && !!trade.is_final_close === final);
        if (!points.length) continue;
        datasets.push({
          label, data: points.map(({ trade, index }) => ({ x: trade.timestamp!, y: trade.price, tradeIndex: index })),
          showLine: false, pointRadius: 6, pointHoverRadius: 9, pointHitRadius: 12,
          pointStyle: final ? 'rectRot' : 'triangle', pointRotation: type === 'SELL' ? 180 : 0,
          backgroundColor: color, borderColor: '#ffffff', pointBorderWidth: 1, order: 0, yAxisID: 'y'
        });
      }
      const min = data.timestamps[0];
      const max = data.timestamps[data.timestamps.length - 1];
      const span = Math.max(max - min, 1);
      const zoom: NonNullable<NonNullable<ChartOptions<'line'>['plugins']>['zoom']> = {
        limits: { x: { min, max: Math.max(max, min + 1), minRange: Math.min(span, Math.max((data.timestamps[1] ?? min + 1) - min, 1) * 2) } },
        pan: { enabled: true, mode: 'x', onPanComplete: () => this.updateRange() },
        zoom: {
          mode: 'x', wheel: { enabled: true }, pinch: { enabled: true },
          onZoomComplete: () => this.updateRange()
        }
      };
      this.chart = new Chart<'line', PlotPoint[]>(this.canvas.nativeElement, {
        type: 'line', data: { datasets },
        options: {
          responsive: true, maintainAspectRatio: false, animation: false,
          parsing: false, color: '#f8fafc',
          interaction: { mode: 'nearest', intersect: false },
          onClick: (_event, elements) => {
            const element = elements.find(item => datasets[item.datasetIndex].data[item.index].tradeIndex !== undefined);
            if (element) this.selectTrade(datasets[element.datasetIndex].data[element.index].tradeIndex!, false);
          },
          plugins: {
            zoom,
            legend: { labels: { color: '#f8fafc', boxWidth: 12, padding: 16 } },
            tooltip: {
              titleColor: '#ffffff', bodyColor: '#ffffff', backgroundColor: '#111827',
              callbacks: {
                title: items => this.formatTime(items[0]?.parsed.x),
                label: context => {
                  const point = context.raw as PlotPoint;
                  if (point.tradeIndex !== undefined) {
                    const trade = this.trades[point.tradeIndex];
                    return [this.tradeLabel(trade), 'Cijena: ' + this.formatPrice(trade.price) + ' USDT',
                      ...(trade.profit_pct == null ? [] : ['Dobit: ' + trade.profit_pct + '%'])];
                  }
                  return context.dataset.label + ': ' + this.formatPrice(point.y) + (context.dataset.yAxisID === 'rsi' ? '' : ' USDT');
                }
              }
            }
          },
          scales: {
            x: {
              type: 'linear', min, max: Math.max(max, min + 1),
              title: { display: true, text: 'Vrijeme (UTC)', color: '#f8fafc' },
              ticks: { color: '#e2e8f0', maxTicksLimit: 6, maxRotation: 0, callback: value => this.formatTime(Number(value)) },
              grid: { color: '#334155' }
            },
            y: {
              title: { display: true, text: 'Cijena (USDT)', color: '#f8fafc' },
              ticks: { color: '#e2e8f0' }, grid: { color: '#334155' }
            },
            ...(data['rsi'] ? { rsi: {
              type: 'linear' as const, position: 'right' as const, min: 0, max: 100,
              title: { display: true, text: 'RSI', color: '#fbbf24' },
              ticks: { color: '#fbbf24', maxTicksLimit: 5 }, grid: { drawOnChartArea: false }
            } } : {})
          }
        }
      });
      this.ready.set(true);
      this.loading.set(false);
      this.updateRange();
    } catch {
      if (generation !== this.generation) return;
      this.loading.set(false);
      this.error.set('Graf nije dostupan za ovu simulaciju.');
    }
  }

  zoom(factor: number) { this.chart?.zoom({ x: factor }); this.updateRange(); }
  reset() { this.chart?.resetZoom(); this.updateRange(); }
  selectTrade(index: number, focus = true) {
    this.selectedIndex.set(index);
    const trade = this.trades[index];
    if (!focus || !this.chart || !this.data || !Number.isFinite(trade?.timestamp)) return;
    const times = this.data.timestamps;
    const first = times[0];
    const last = times[times.length - 1];
    const width = Math.max(1, Math.min(last - first, Math.max((last - first) / 10, ((times[1] ?? first + 1) - first) * 10)));
    const min = Math.max(first, Math.min(trade.timestamp! - width / 2, last - width));
    this.chart.zoomScale('x', { min, max: min + width });
    this.updateRange();
  }
  stepTrade(direction: number) {
    const items = this.timedTrades;
    const current = items.findIndex(item => item.index === this.selectedIndex());
    const next = current < 0 ? (direction > 0 ? 0 : items.length - 1) : (current + direction + items.length) % items.length;
    if (items[next]) this.selectTrade(items[next].index);
  }
  private updateRange() {
    if (!this.chart) return;
    const x = this.chart.scales['x'];
    this.visibleRange.set(this.formatTime(x.min) + ' - ' + this.formatTime(x.max) + ' UTC');
  }
  formatTime(value?: number | null) { return typeof value === 'number' && Number.isFinite(value) ? this.dateFormat.format(value) : '-'; }
  formatPrice(value: number | null) { return value == null ? '-' : value.toLocaleString('hr-HR', { maximumFractionDigits: 8 }); }
  tradeLabel(trade: Trade) { return trade.is_final_close ? 'Prodaja na kraju razdoblja' : trade.type.toUpperCase() === 'BUY' ? 'Kupnja' : 'Prodaja'; }
}
