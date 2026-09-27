export type StrategyKey = 'moving-average' | 'rsi' | 'bollinger';

export type StrategyParameters = Record<string, number>;

export interface Trade {
  type: string;
  price: number;
  profit_pct: number | null;
  is_final_close?: boolean;
  candle_index?: number;
  timestamp?: number | null;
}

export interface ChartData {
  timestamps: number[];
  prices: number[];
  [indicator: string]: (number | null)[];
}

export interface BacktestResult {
  initial_balance: number;
  final_balance: number;
  return_pct: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  number_of_trades: number;
  had_open_position_at_end?: boolean;
  open_position?: boolean;
  trades: Trade[];
  chart_data?: ChartData;
}

export interface BacktestRequest {
  strategy: StrategyKey;
  symbol: string;
  interval: string;
  initial_balance: number;
  start_date?: string;
  end_date?: string;
  parameters: StrategyParameters;
}

export interface BacktestResponse {
  id?: number;
  strategy: string;
  symbol: string;
  interval: string;
  start_date?: string | null;
  end_date?: string | null;
  parameters?: StrategyParameters | null;
  result: BacktestResult;
}

export interface Simulation {
  id: number;
  strategy: string;
  symbol: string;
  interval: string;
  initial_balance: number;
  final_balance: number;
  return_pct: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  number_of_trades: number;
  start_date: string | null;
  end_date: string | null;
  parameters: StrategyParameters | null;
  created_at: string;
}

export interface SimulationDetails extends Simulation {
  result?: BacktestResult;
}

export interface StrategyComparisonResult {
  strategy: string;
  parameters: StrategyParameters;
  return_pct: number;
  final_balance: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  number_of_trades: number;
}

export interface StrategyComparisonResponse {
  symbol: string;
  interval: string;
  start_date: string | null;
  end_date: string | null;
  initial_balance: number;
  results: StrategyComparisonResult[];
}

export interface DashboardStats {
  total_simulations: number;
  best_roi: number;
  most_used_strategy: string;
  most_traded_symbol: string;
}

export interface SymbolSearchResult {
  symbol: string;
  base_asset: string;
  quote_asset: string;
}

export interface ApiResponse<T> {
  status: string;
  data: T;
  records?: number;
}
