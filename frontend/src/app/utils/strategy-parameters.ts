import type { StrategyParameters } from '../models';

const PARAMETER_LABELS: Record<string, string> = {
  short_window: 'Kratki prozor',
  long_window: 'Dugi prozor',
  period: 'RSI period',
  oversold: 'Granica preprodanosti',
  overbought: 'Granica prekupljenosti',
  window: 'Prozor',
  num_std: 'Broj standardnih devijacija'
};

export const MISSING_PARAMETERS_TEXT = 'Nisu spremljeni (starija simulacija)';

export function strategyParameterRows(parameters: StrategyParameters | null | undefined): [string, string][] {
  if (!parameters) {
    return [];
  }

  const known = Object.keys(PARAMETER_LABELS).filter((key) => key in parameters);
  const unknown = Object.keys(parameters).filter((key) => !(key in PARAMETER_LABELS));

  return [...known, ...unknown].map((key) => [PARAMETER_LABELS[key] ?? key, String(parameters[key])]);
}

export function formatStrategyParameters(parameters: StrategyParameters | null | undefined): string {
  const rows = strategyParameterRows(parameters);

  if (rows.length === 0) {
    return MISSING_PARAMETERS_TEXT;
  }

  return rows.map(([label, value]) => `${label}: ${value}`).join(', ');
}
