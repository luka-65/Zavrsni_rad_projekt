import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from '../api.config';
import { ChartData } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ChartDataService {
  private apiUrl = `${API_URL}/chart`;

  constructor(private http: HttpClient) {}

  getChartData(
    endpoint: string,
    symbol: string,
    interval: string,
    params: string
  ) {
    return this.http.get<ChartData>(
      `${this.apiUrl}/${endpoint}?symbol=${symbol}&interval=${interval}${params}`
    );
  }
}