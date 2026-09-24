import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { RecruitmentJob, RecruitmentJobInput, RecruitmentTaxonomy } from './recruitment.models';
@Injectable({ providedIn: 'root' })
export class RecruitmentService {
  private readonly http = inject(HttpClient);
  list(query = ''): Observable<RecruitmentJob[]> { const params = query ? new HttpParams().set('q', query) : undefined; return this.http.get<RecruitmentJob[]>('/api/recruitment/', { params }); }
  create(payload: RecruitmentJobInput): Observable<RecruitmentJob> { return this.http.post<RecruitmentJob>('/api/recruitment/', payload); }
  update(id: number, payload: RecruitmentJobInput): Observable<RecruitmentJob> { return this.http.patch<RecruitmentJob>(`/api/recruitment/${id}/`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`/api/recruitment/${id}/`); }
  departments(): Observable<RecruitmentTaxonomy[]> { return this.http.get<RecruitmentTaxonomy[]>('/api/recruitment/departments/'); }
  tags(): Observable<RecruitmentTaxonomy[]> { return this.http.get<RecruitmentTaxonomy[]>('/api/products/tags/'); }
  regions(): Observable<RecruitmentTaxonomy[]> { return this.http.get<RecruitmentTaxonomy[]>('/api/recruitment/locations/regions/'); }
  areas(regionId: number): Observable<RecruitmentTaxonomy[]> { return this.http.get<RecruitmentTaxonomy[]>('/api/recruitment/locations/areas/', { params: { region_id: regionId } }); }
  businessUnits(areaId: number): Observable<RecruitmentTaxonomy[]> { return this.http.get<RecruitmentTaxonomy[]>('/api/recruitment/locations/business-units/', { params: { area_id: areaId } }); }
  createRegion(name: string): Observable<RecruitmentTaxonomy> { return this.http.post<RecruitmentTaxonomy>('/api/recruitment/locations/regions/', { name }); }
  updateRegion(id: number, name: string): Observable<RecruitmentTaxonomy> { return this.http.patch<RecruitmentTaxonomy>(`/api/recruitment/locations/regions/${id}/`, { name }); }
  deleteRegion(id: number): Observable<void> { return this.http.delete<void>(`/api/recruitment/locations/regions/${id}/`); }
  allAreas(): Observable<(RecruitmentTaxonomy & { region_id: number })[]> { return this.http.get<(RecruitmentTaxonomy & { region_id: number })[]>('/api/recruitment/locations/areas/'); }
  createArea(name: string, regionId: number): Observable<RecruitmentTaxonomy> { return this.http.post<RecruitmentTaxonomy>('/api/recruitment/locations/areas/', { name, region_id: regionId }); }
  updateArea(id: number, name: string, regionId: number): Observable<RecruitmentTaxonomy> { return this.http.patch<RecruitmentTaxonomy>(`/api/recruitment/locations/areas/${id}/`, { name, region_id: regionId }); }
  deleteArea(id: number): Observable<void> { return this.http.delete<void>(`/api/recruitment/locations/areas/${id}/`); }
  createDepartment(name: string): Observable<RecruitmentTaxonomy> { return this.http.post<RecruitmentTaxonomy>('/api/recruitment/departments/', { name }); }
  updateDepartment(id: number, name: string): Observable<RecruitmentTaxonomy> { return this.http.patch<RecruitmentTaxonomy>(`/api/recruitment/departments/${id}/`, { name }); }
  deleteDepartment(id: number): Observable<void> { return this.http.delete<void>(`/api/recruitment/departments/${id}/`); }
}
