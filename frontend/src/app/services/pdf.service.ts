import { Injectable } from '@angular/core';
import jsPDF from 'jspdf';

@Injectable({
  providedIn: 'root'
})
export class PdfService {

  downloadSimulationPdf(result: any, strategy: string) {
    if (!result) {
      return;
    }

    const doc = new jsPDF();
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

    doc.text(`Datum izrade: ${today}`, 10, 40);
    doc.text(`Strategija: ${this.formatStrategyName(result.strategy)}`, 10, 52);
    doc.text(`Simbol: ${result.symbol}`, 10, 64);
    doc.text(`Interval: ${result.interval}`, 10, 76);

    if (result.start_date && result.end_date) {
      doc.text(`Razdoblje: ${result.start_date} - ${result.end_date}`, 10, 88);
    }

    doc.setFontSize(14);
    doc.text('Rezultati simulacije', 10, 100);

    const rows = [
      ['Pocetni kapital', `${result.result.initial_balance} USDT`],
      ['Završni kapital', `${result.result.final_balance} USDT`],
      ['Ukupni povrat', `${result.result.return_pct}%`],
      ['Najveci pad', `${result.result.max_drawdown_pct}%`],
      ['Stopa dobitnih transakcija', `${result.result.win_rate_pct}%`],
      ['Broj zatvorenih transakcija', `${result.result.number_of_trades}`],
      ['Otvorena pozicija', result.result.open_position ? 'Da' : 'Ne']
    ];

    let y = 113;

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
      205,
      { maxWidth: 185 }
    );

    doc.save(`izvjestaj_${result.symbol}_${strategy}.pdf`);
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
