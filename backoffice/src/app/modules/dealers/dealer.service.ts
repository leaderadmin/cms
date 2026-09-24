import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Dealer, DealerInput } from './dealer.models';
@Injectable({ providedIn: 'root' })
export class DealerService {
  regions(): Observable<{ id: number; name: string }[]> { return this.http.get<{ id: number; name: string }[]>('/api/recruitment/locations/regions/'); }
  areas(regionId?: number): Observable<{ id: number; name: string; region_id: number }[]> { let params = new HttpParams(); if (regionId) params = params.set('region_id', regionId); return this.http.get<{ id: number; name: string; region_id: number }[]>('/api/recruitment/locations/areas/', { params }); }
  private readonly http = inject(HttpClient);
  list(query = '', type = ''): Observable<Dealer[]> { let params = new HttpParams(); if (query) params = params.set('q', query); if (type) params = params.set('type', type); return this.http.get<Dealer[]>('/api/dealers/', { params }); }
  create(payload: DealerInput): Observable<Dealer> { return this.http.post<Dealer>('/api/dealers/', payload); }
  update(id: number, payload: DealerInput): Observable<Dealer> { return this.http.patch<Dealer>(`/api/dealers/${id}/`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`/api/dealers/${id}/`); }
}
