import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { SchemaTable } from './entity.models';

@Injectable({ providedIn: 'root' })
export class EntityService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/entities/';

  catalog(): Observable<SchemaTable[]> {
    return this.http.get<SchemaTable[]>(this.endpoint);
  }

  table(name: string): Observable<SchemaTable> {
    return this.http.get<SchemaTable>(`${this.endpoint}schema/${name}/`);
  }

  addColumn(table: string, payload: { name: string; type: string; nullable: boolean; default?: string }): Observable<SchemaTable> {
    return this.http.post<SchemaTable>(`${this.endpoint}schema/${table}/`, payload);
  }

  updateColumn(table: string, column: string, payload: { name?: string; type?: string; length?: number | null; precision?: number | null; scale?: number | null; nullable?: boolean; default?: string }): Observable<SchemaTable> {
    return this.http.patch<SchemaTable>(`${this.endpoint}schema/${table}/columns/${column}/`, payload);
  }

  dropColumn(table: string, column: string): Observable<SchemaTable> {
    return this.http.delete<SchemaTable>(`${this.endpoint}schema/${table}/columns/${column}/`);
  }
}
