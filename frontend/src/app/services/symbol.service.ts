import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SymbolService {
  private apiUrl = 'http://127.0.0.1:5000/api/symbols/search';

  constructor(private http: HttpClient) {}

  searchSymbols(query: string) {
    return this.http.get<any>(
      `${this.apiUrl}?query=${query}`
    );
  }
}