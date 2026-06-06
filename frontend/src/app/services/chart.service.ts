import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChartDataService {
  private apiUrl = 'http://127.0.0.1:5000/api/chart';

  constructor(private http: HttpClient) {}

  getChartData(
    endpoint: string,
    symbol: string,
    interval: string,
    params: string
  ) {
    return this.http.get<any>(
      `${this.apiUrl}/${endpoint}?symbol=${symbol}&interval=${interval}${params}`
    );
  }
}