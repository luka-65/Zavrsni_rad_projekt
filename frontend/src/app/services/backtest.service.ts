import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BacktestService {
  private apiUrl = 'http://127.0.0.1:5000/api/backtest';

  constructor(private http: HttpClient) {}

  runBacktest(
    endpoint: string,
    symbol: string,
    interval: string,
    initialBalance: number,
    params: string
  ) {
    return this.http.get(
      `${this.apiUrl}/${endpoint}?symbol=${symbol}&interval=${interval}&initial_balance=${initialBalance}${params}`
    );
  }

  compareStrategies(symbol: string, interval: string, initialBalance: number) {
    return this.http.get<any>(
      `${this.apiUrl}/compare?symbol=${symbol}&interval=${interval}&initial_balance=${initialBalance}`
    );
  }
}