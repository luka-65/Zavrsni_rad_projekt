import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from '../api.config';
import { ApiResponse, SymbolSearchResult } from '../models';

@Injectable({
  providedIn: 'root'
})
export class SymbolService {
  private apiUrl = `${API_URL}/symbols/search`;

  constructor(private http: HttpClient) {}

  searchSymbols(query: string) {
    return this.http.get<ApiResponse<SymbolSearchResult[]>>(
      this.apiUrl, { params: { query } }
    );
  }
}