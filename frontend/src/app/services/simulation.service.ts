import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from '../api.config';
import { ApiResponse, DashboardStats, Simulation, SimulationDetails } from '../models';

@Injectable({
  providedIn: 'root'
})
export class SimulationService {
  private apiUrl = `${API_URL}/simulations`;

  constructor(private http: HttpClient) {}

  getSimulations() {
    return this.http.get<ApiResponse<Simulation[]>>(this.apiUrl);
  }

  getDashboardStats() {
  return this.http.get<ApiResponse<DashboardStats>>(
    `${API_URL}/dashboard-stats`
  );
}

getBestBacktest() {
  return this.http.get<ApiResponse<Simulation | null>>(
    `${API_URL}/best-backtest`
  );
}

getSimulationById(id: number) {
  return this.http.get<ApiResponse<SimulationDetails>>(
    `${this.apiUrl}/${id}`
  );
}

deleteSimulation(id: number) {
  return this.http.delete<{ status: string; message: string }>(
    `${this.apiUrl}/${id}`
  );
}
}
