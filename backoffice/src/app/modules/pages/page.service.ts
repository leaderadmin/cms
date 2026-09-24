import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DynamicForm, DynamicFormInput, Page, PageComponentDefinition, PageComponentDefinitionInput, PageInput, PageTemplate, PageTemplateInput, ReusablePageComponent, ReusablePageComponentInput } from './page.models';

export interface ContentArticle { id: number; name: string; title?: string; status: number; categories?: Array<{ id: number; title: string; name: string }>; }
export interface ContentCategory { id: number; name: string; title: string; status: number; }
export interface ContentPage { id: number; name: string; slug: string; template_key: string; status: string; }
export interface ContentProduct { id: number; name: string; slug: string; kind: string; title?: string; }

@Injectable({ providedIn: 'root' })
export class PageService {
  private readonly http = inject(HttpClient);

  list(query = '', status = ''): Observable<Page[]> {
    let params = new HttpParams();
    if (query) params = params.set('q', query);
    if (status) params = params.set('status', status);
    return this.http.get<Page[]>('/api/pages/', { params });
  }

  create(payload: PageInput): Observable<Page> { return this.http.post<Page>('/api/pages/', payload); }
  update(id: number, payload: PageInput): Observable<Page> { return this.http.patch<Page>(`/api/pages/${id}/`, payload); }
  archive(id: number): Observable<void> { return this.http.delete<void>(`/api/pages/${id}/`); }
  draft(slug: string): Observable<{ page: Page; version: { regions: Record<string, unknown[]> } }> { return this.http.get<{ page: Page; version: { regions: Record<string, unknown[]> } }>(`/api/pages/${slug}/draft/`); }
  updateDraft(slug: string, regions: Record<string, unknown[]>): Observable<{ page: Page; version: { regions: Record<string, unknown[]> } }> { return this.http.patch<{ page: Page; version: { regions: Record<string, unknown[]> } }>(`/api/pages/${slug}/draft/`, { regions }); }
  publish(slug: string): Observable<{ page: Page; version: { regions: Record<string, unknown[]> } }> { return this.http.post<{ page: Page; version: { regions: Record<string, unknown[]> } }>(`/api/pages/${slug}/publish/`, {}); }

  templates(query = ''): Observable<PageTemplate[]> {
    const params: Record<string, string> = {};
    if (query) params['q'] = query;
    return this.http.get<PageTemplate[]>('/api/pages/templates/', { params });
  }

  createTemplate(payload: PageTemplateInput): Observable<PageTemplate> { return this.http.post<PageTemplate>('/api/pages/templates/', payload); }

  updateTemplate(id: number, payload: PageTemplateInput): Observable<PageTemplate> { return this.http.patch<PageTemplate>(`/api/pages/templates/${id}/`, payload); }

  components(query = ''): Observable<ReusablePageComponent[]> {
    const params: Record<string, string> = {};
    if (query) params['q'] = query;
    return this.http.get<ReusablePageComponent[]>('/api/pages/components/', { params });
  }

  createComponent(payload: ReusablePageComponentInput): Observable<ReusablePageComponent> { return this.http.post<ReusablePageComponent>('/api/pages/components/', payload); }
  updateComponent(id: number, payload: ReusablePageComponentInput): Observable<ReusablePageComponent> { return this.http.patch<ReusablePageComponent>(`/api/pages/components/${id}/`, payload); }
  deleteComponent(id: number): Observable<void> { return this.http.delete<void>(`/api/pages/components/${id}/`); }

  componentDefinitions(query = ''): Observable<PageComponentDefinition[]> {
    const params: Record<string, string> = {};
    if (query) params['q'] = query;
    return this.http.get<PageComponentDefinition[]>('/api/pages/component-definitions/', { params });
  }

  createComponentDefinition(payload: PageComponentDefinitionInput): Observable<PageComponentDefinition> { return this.http.post<PageComponentDefinition>('/api/pages/component-definitions/', payload); }
  updateComponentDefinition(id: number, payload: PageComponentDefinitionInput): Observable<PageComponentDefinition> { return this.http.patch<PageComponentDefinition>(`/api/pages/component-definitions/${id}/`, payload); }
  deleteComponentDefinition(id: number): Observable<void> { return this.http.delete<void>(`/api/pages/component-definitions/${id}/`); }

  forms(query = ''): Observable<DynamicForm[]> {
    const params: Record<string, string> = {};
    if (query) params['q'] = query;
    return this.http.get<DynamicForm[]>('/api/pages/forms/', { params });
  }
  createForm(payload: DynamicFormInput): Observable<DynamicForm> { return this.http.post<DynamicForm>('/api/pages/forms/', payload); }
  updateForm(id: number, payload: DynamicFormInput): Observable<DynamicForm> { return this.http.patch<DynamicForm>(`/api/pages/forms/${id}/`, payload); }
  deleteForm(id: number): Observable<void> { return this.http.delete<void>(`/api/pages/forms/${id}/`); }

  articles(query = '', page = 1, pageSize = 25): Observable<{ count: number; page: number; page_size: number; next: number | null; previous: number | null; results: ContentArticle[] }> {
    let params = new HttpParams().set('status', 1).set('page', page).set('page_size', pageSize);
    if (query) params = params.set('q', query);
    return this.http.get<{ count: number; page: number; page_size: number; next: number | null; previous: number | null; results: ContentArticle[] }>('/api/articles/', { params });
  }
  categories(): Observable<ContentCategory[]> { return this.http.get<ContentCategory[]>('/api/articles/categories/?status=1'); }
  contentPages(): Observable<Page[]> { return this.http.get<Page[]>('/api/pages/?status=published'); }
  products(): Observable<{ results: ContentProduct[] }> { return this.http.get<{ results: ContentProduct[] }>('/api/products/?status=1&page_size=100&language=vi'); }
}
