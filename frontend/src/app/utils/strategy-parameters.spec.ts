import {
  MISSING_PARAMETERS_TEXT,
  formatStrategyParameters,
  strategyParameterRows
} from './strategy-parameters';

describe('Oblikovanje parametara strategije', () => {
  it('oblikuje prozore pomičnih prosjeka', () => {
    expect(formatStrategyParameters({ short_window: 20, long_window: 50 }))
      .toBe('Kratki prozor: 20, Dugi prozor: 50');
  });

  it('oblikuje RSI period i granice uvijek istim redom', () => {
    expect(strategyParameterRows({ overbought: 80, period: 10, oversold: 20 })).toEqual([
      ['RSI period', '10'],
      ['Granica preprodanosti', '20'],
      ['Granica prekupljenosti', '80']
    ]);
  });

  it('zadržava decimalni broj standardnih devijacija', () => {
    expect(formatStrategyParameters({ window: 15, num_std: 2.5 }))
      .toBe('Prozor: 15, Broj standardnih devijacija: 2.5');
  });

  it('označava starije simulacije bez spremljenih parametara', () => {
    expect(strategyParameterRows(null)).toEqual([]);
    expect(formatStrategyParameters(undefined)).toBe(MISSING_PARAMETERS_TEXT);
  });
});
