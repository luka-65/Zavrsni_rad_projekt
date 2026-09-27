import { Injectable } from '@angular/core';
import type jsPDF from 'jspdf';
import type { BacktestResponse } from '../models';
import { MISSING_PARAMETERS_TEXT, strategyParameterRows } from '../utils/strategy-parameters';
import { SIMULATION_ASSUMPTIONS, hadOpenPositionAtEnd } from '../utils/simulation-model';

@Injectable({
  providedIn: 'root'
})
export class PdfService {

  async downloadSimulationPdf(result: BacktestResponse | null, strategy: string) {
    if (!result) {
      return;
    }

    const doc = await this.createDocument();
    const today = new Date().toLocaleString('hr-HR');

    doc.setFillColor(15, 23, 42);
    doc.rect(0, 0, 210, 28, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.text('Simulator trgovanja kriptovalutama', 10, 12);

    doc.setFontSize(11);
    doc.text('Izvještaj simulacije trgovanja kriptovalutama', 10, 20);

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(12);

    doc.text(`Datum izrade: ${today}`, 10, 38);
    doc.text(`Strategija: ${this.formatStrategyName(result.strategy)}`, 10, 46);
    doc.text(`Simbol: ${result.symbol}`, 10, 54);
    doc.text(`Interval: ${result.interval}`, 10, 62);

    let y = 70;

    if (result.start_date && result.end_date) {
      doc.text(`Razdoblje: ${result.start_date} - ${result.end_date}`, 10, y);
      y += 8;
    }

    y += 4;

    doc.setFontSize(14);
    doc.text('Parametri strategije', 10, y);
    y += 13;

    const parameterRows = strategyParameterRows(result.parameters);

    if (parameterRows.length === 0) {
      parameterRows.push(['Parametri', MISSING_PARAMETERS_TEXT]);
    }

    y = this.drawTable(doc, parameterRows, y);

    doc.setFontSize(14);
    doc.text('Rezultati simulacije', 10, y);
    y += 13;

    const rows: [string, string][] = [
      ['Pocetni kapital', `${result.result.initial_balance} USDT`],
      ['Završni kapital', `${result.result.final_balance} USDT`],
      ['Ukupni povrat', `${result.result.return_pct}%`],
      ['Najveci pad', `${result.result.max_drawdown_pct}%`],
      ['Stopa dobitnih transakcija', `${result.result.win_rate_pct}%`],
      ['Broj zatvorenih transakcija', `${result.result.number_of_trades}`],
      [
        'Pozicija otvorena na kraju',
        hadOpenPositionAtEnd(result.result) ? 'Da (zatvorena po zadnjoj cijeni)' : 'Ne'
      ]
    ];

    y = this.drawTable(doc, rows, y);

    const notes = [
      'Pretpostavke modela:',
      ...SIMULATION_ASSUMPTIONS.map((assumption) => `- ${assumption}`),
      'Napomena: Rezultati predstavljaju simulacijsko testiranje nad povijesnim podacima i ne predstavljaju financijski savjet.'
    ];

    doc.setFontSize(9);
    doc.setTextColor(90, 90, 90);

    notes.forEach((note) => {
      const lines: string[] = doc.splitTextToSize(this.toPdfText(note), 190);

      if (y + lines.length * 4 > 290) {
        doc.addPage();
        y = 20;
      }

      doc.text(lines, 10, y);
      y += lines.length * 4 + 1.5;
    });

    doc.save(`izvjestaj_${result.symbol}_${strategy}.pdf`);
  }

  private toPdfText(text: string) {
    return text.replace(/[čć]/g, 'c').replace(/[ČĆ]/g, 'C').replace(/đ/g, 'd').replace(/Đ/g, 'D');
  }

  private async createDocument() {
    const { default: JsPdf } = await import('jspdf');
    return new JsPdf();
  }

  private drawTable(doc: jsPDF, rows: [string, string][], y: number) {
    doc.setFontSize(12);

    rows.forEach((row) => {
      doc.setFillColor(241, 245, 249);
      doc.rect(10, y - 7, 90, 10, 'F');

      doc.setFillColor(226, 232, 240);
      doc.rect(100, y - 7, 90, 10, 'F');

      doc.text(row[0], 13, y);
      doc.text(row[1], 103, y);

      y += 11;
    });

    return y + 3;
  }

  private formatStrategyName(strategyName: string) {
    if (strategyName === 'Moving Average Crossover') {
      return 'Križanje pomicnih prosjeka';
    }

    if (strategyName === 'Relative Strength Index') {
      return 'Indeks relativne snage';
    }

    if (strategyName === 'Bollinger Bands') {
      return 'Bollingerove ovojnice';
    }

    return strategyName;
  }
}
