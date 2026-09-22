import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Article, ArticleCategory, ArticleCategoryInput, ArticleInput, ArticlePage, ArticleTag } from './article.models';

@Injectable({ providedIn: 'root' })
export class ArticleService {
  private readonly http = inject(HttpClient);

  list(query: string, status: string, language: string, page: number, pageSize: number): Observable<ArticlePage> {
    let params = new HttpParams();
    if (query) params = params.set('q', query);
    if (status) params = params.set('status', status);
    if (language) params = params.set('language', language);
    params = params.set('page', page).set('page_size', pageSize);
    return this.http.get<ArticlePage>('/api/articles/', { params });
  }

  categories(query = '', status = '', type = ''): Observable<ArticleCategory[]> {
    let params = new HttpParams();
    if (query) params = params.set('q', query);
    if (status) params = params.set('status', status);
    if (type) params = params.set('type', type);
    return this.http.get<ArticleCategory[]>('/api/articles/categories/', { params });
  }
  createCategory(payload: ArticleCategoryInput): Observable<ArticleCategory> { return this.http.post<ArticleCategory>('/api/articles/categories/', payload); }
  updateCategory(id: number, payload: ArticleCategoryInput): Observable<ArticleCategory> { return this.http.patch<ArticleCategory>(`/api/articles/categories/${id}/`, payload); }
  archiveCategory(id: number): Observable<void> { return this.http.delete<void>(`/api/articles/categories/${id}/`); }
  tags(query = ''): Observable<ArticleTag[]> {
    let params = new HttpParams();
    if (query) params = params.set('q', query);
    return this.http.get<ArticleTag[]>('/api/articles/tags/', { params });
  }
  createTag(payload: { name: string; slug?: string }): Observable<ArticleTag> { return this.http.post<ArticleTag>('/api/articles/tags/', payload); }
  updateTag(id: number, payload: { name: string; slug?: string }): Observable<ArticleTag> { return this.http.patch<ArticleTag>(`/api/articles/tags/${id}/`, payload); }
  deleteTag(id: number): Observable<void> { return this.http.delete<void>(`/api/articles/tags/${id}/`); }
  get(id: number): Observable<Article> { return this.http.get<Article>(`/api/articles/${id}/`); }
  create(payload: ArticleInput): Observable<Article> { return this.http.post<Article>('/api/articles/', payload); }
  update(id: number, payload: ArticleInput): Observable<Article> { return this.http.patch<Article>(`/api/articles/${id}/`, payload); }
  publish(id: number, language: string): Observable<Article> { return this.http.post<Article>(`/api/articles/${id}/publish/`, { language }); }
  archive(id: number): Observable<void> { return this.http.delete<void>(`/api/articles/${id}/`); }
}
