import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ActivityLogFilters, ActivityLogResponse } from './audit.models';

@Injectable({ providedIn: 'root' })
export class AuditService {
  private readonly http = inject(HttpClient);

  list(filters: ActivityLogFilters): Observable<ActivityLogResponse> {
    let params = new HttpParams()
      .set('page', filters.page)
      .set('limit', filters.limit);
    for (const [key, value] of Object.entries(filters)) {
      if (key !== 'page' && key !== 'limit' && value) params = params.set(key, value);
    }
    return this.http.get<ActivityLogResponse>('/api/audit/logs/', { params });
  }
}
