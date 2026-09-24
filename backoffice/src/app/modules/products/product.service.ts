import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Product, ProductInput, ProductMetadata, ProductPage, ProductTag } from './product.models';

@Injectable({ providedIn: 'root' })
export class ProductService {
  private readonly http = inject(HttpClient);

  list(query: string, kind: string, status: string, page: number, pageSize: number): Observable<ProductPage> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (query) params = params.set('q', query);
    if (kind) params = params.set('kind', kind);
    if (status) params = params.set('status', status);
    params = params.set('language', 'vi');
    return this.http.get<ProductPage>('/api/products/', { params });
  }

  metadata(): Observable<ProductMetadata> { return this.http.get<ProductMetadata>('/api/products/metadata/'); }
  createMetadata(kind: string, name: string, slug: string, extra: Record<string, unknown> = {}): Observable<unknown> {
    return this.http.post('/api/products/metadata/', { kind, name, slug, ...extra });
  }
  updateMetadata(kind: string, id: number, name: string, slug: string, extra: Record<string, unknown> = {}): Observable<unknown> {
    return this.http.patch(`/api/products/metadata/${id}/`, { kind, name, slug, ...extra });
  }
  get(id: number): Observable<Product> { return this.http.get<Product>(`/api/products/${id}/`); }
  create(payload: ProductInput): Observable<Product> { return this.http.post<Product>('/api/products/', payload); }
  update(id: number, payload: ProductInput): Observable<Product> { return this.http.patch<Product>(`/api/products/${id}/`, payload); }
  tags(query = ''): Observable<ProductTag[]> { let params = new HttpParams(); if (query) params = params.set('q', query); return this.http.get<ProductTag[]>('/api/products/tags/', { params }); }
  createTag(payload: { name: string; slug?: string }): Observable<ProductTag> { return this.http.post<ProductTag>('/api/products/tags/', payload); }
  updateTag(id: number, payload: { name: string; slug?: string }): Observable<ProductTag> { return this.http.patch<ProductTag>(`/api/products/tags/${id}/`, payload); }
  deleteTag(id: number): Observable<void> { return this.http.delete<void>(`/api/products/tags/${id}/`); }
  publish(id: number): Observable<Product> { return this.http.post<Product>(`/api/products/${id}/publish/`, { language: 'vi' }); }
  archive(id: number): Observable<void> { return this.http.delete<void>(`/api/products/${id}/`); }
}
