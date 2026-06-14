import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SimulationService {
  private apiUrl = 'http://127.0.0.1:5000/api/simulations';

  constructor(private http: HttpClient) {}

  getSimulations() {
    return this.http.get<any>(this.apiUrl);
  }

  getDashboardStats() {
  return this.http.get<any>(
    'http://127.0.0.1:5000/api/dashboard-stats'
  );
}

getBestBacktest() {
  return this.http.get<any>(
    'http://127.0.0.1:5000/api/best-backtest'
  );
}

getSimulationById(id: number) {
  return this.http.get<any>(
    `http://127.0.0.1:5000/api/simulations/${id}`
  );
}

deleteSimulation(id: number) {
  return this.http.delete<any>(
    `http://127.0.0.1:5000/api/simulations/${id}`
  );
}
}
