import type { BacktestResult } from '../models';

export const SIMULATION_ASSUMPTIONS = [
  'Kupnja i prodaja izvršavaju se po cijeni zatvaranja (close) istog OHLCV zapisa na kojem je signal nastao. ' +
    'Indikatori ne koriste buduće podatke, ali ova pretpostavka može dati optimističnije rezultate od izvršenja u sljedećem intervalu.',
  'Pri kupnji se ulaže cijeli raspoloživi kapital, a prodajom se zatvara cijela pozicija. Trguje se samo long pozicijama.',
  'Nisu uključene transakcijske naknade, spread ni slippage, pa povrat predstavlja teorijski rezultat modela, ' +
    'a ne očekivani rezultat stvarnog trgovanja.',
  'Pozicija otvorena na kraju razdoblja zatvara se po posljednjoj dostupnoj cijeni radi izračuna konačne vrijednosti.'
];

export function hadOpenPositionAtEnd(result: BacktestResult | null | undefined): boolean {
  return Boolean(result?.had_open_position_at_end ?? result?.open_position);
}
