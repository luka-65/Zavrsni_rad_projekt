import { TestBed } from '@angular/core/testing';
import { jsPDF } from 'jspdf';
import { afterEach, vi } from 'vitest';

import { PdfService } from './pdf.service';
import { BacktestResponse, BacktestResult } from '../models';

describe('PDF izvještaj (PdfService)', () => {
  afterEach(() => vi.restoreAllMocks());

  const result = (parameters: Record<string, number> | null, flags: Partial<BacktestResult> = {}): BacktestResponse => ({
    strategy: 'Moving Average Crossover',
    symbol: 'BTCUSDT',
    interval: '1d',
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    parameters,
    result: {
      initial_balance: 10000,
      final_balance: 12000,
      return_pct: 20,
      max_drawdown_pct: 8,
      win_rate_pct: 60,
      number_of_trades: 5,
      had_open_position_at_end: false,
      trades: [],
      ...flags
    }
  });

  async function writtenText(parameters: Record<string, number> | null, flags: Partial<BacktestResult> = {}) {
    const doc = new jsPDF();
    const text = vi.spyOn(doc, 'text');
    const save = vi.spyOn(doc, 'save').mockImplementation(() => doc);
    const service = TestBed.inject(PdfService);
    vi.spyOn(service as any, 'createDocument').mockResolvedValue(doc);

    await service.downloadSimulationPdf(result(parameters, flags), 'moving-average');

    expect(save).toHaveBeenCalledWith('izvjestaj_BTCUSDT_moving-average.pdf');
    return text.mock.calls.flatMap((call) => (Array.isArray(call[0]) ? call[0] : [String(call[0])]));
  }

  it('upisuje spremljene parametre strategije u izvještaj', async () => {
    const lines = await writtenText({ short_window: 10, long_window: 40 });

    expect(lines).toContain('Parametri strategije');
    expect(lines).toEqual(expect.arrayContaining(['Kratki prozor', '10', 'Dugi prozor', '40']));
  });

  it('opisuje model izvršenja i izostanak transakcijskih troškova', async () => {
    const text = (await writtenText({ short_window: 10, long_window: 40 })).join(' ');

    expect(text).toContain('Pretpostavke modela:');
    expect(text).toContain('cijeni zatvaranja (close) istog OHLCV zapisa');
    expect(text).toContain('Nisu ukljucene transakcijske naknade, spread ni slippage');
    expect(text).not.toMatch(/[čćđČĆĐ]/);
  });

  it('označava prisilno zatvorenu poziciju, i kod starijih rezultata', async () => {
    expect(await writtenText(null, { had_open_position_at_end: true }))
      .toContain('Da (zatvorena po zadnjoj cijeni)');
    expect(await writtenText(null, { had_open_position_at_end: undefined, open_position: true }))
      .toContain('Da (zatvorena po zadnjoj cijeni)');
  });

  it('navodi da starije simulacije nemaju spremljene parametre', async () => {
    const lines = await writtenText(null);

    expect(lines).toContain('Nisu spremljeni (starija simulacija)');
  });
});
