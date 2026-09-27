import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { API_URL } from '../api.config';
import { BacktestRequest, BacktestResponse, StrategyComparisonResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class BacktestService {
  private apiUrl = `${API_URL}/backtests`;

  constructor(private http: HttpClient) {}

  runBacktest(request: BacktestRequest) {
    return this.http.post<BacktestResponse>(this.apiUrl, request);
  }

  compareStrategies(
    symbol: string,
    interval: string,
    initialBalance: number,
    startDate: string,
    endDate: string
  ) {
    let params = new HttpParams()
      .set('symbol', symbol)
      .set('interval', interval)
      .set('initial_balance', initialBalance);

    if (startDate && endDate) {
      params = params.set('start_date', startDate).set('end_date', endDate);
    }

    return this.http.get<StrategyComparisonResponse>(`${this.apiUrl}/compare`, { params });
  }
}
