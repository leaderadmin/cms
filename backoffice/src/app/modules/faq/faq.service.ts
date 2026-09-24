import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { FAQCategory, FAQCategoryInput, FAQQuestion, FAQQuestionInput } from './faq.models';
@Injectable({ providedIn: 'root' })
export class FAQService {
  private readonly http = inject(HttpClient);
  list(query = ''): Observable<FAQCategory[]> { const params = query ? new HttpParams().set('q', query) : undefined; return this.http.get<FAQCategory[]>('/api/faq/categories/', { params }); }
  createCategory(payload: FAQCategoryInput): Observable<FAQCategory> { return this.http.post<FAQCategory>('/api/faq/categories/', payload); }
  updateCategory(id: number, payload: FAQCategoryInput): Observable<FAQCategory> { return this.http.patch<FAQCategory>(`/api/faq/categories/${id}/`, payload); }
  deleteCategory(id: number): Observable<void> { return this.http.delete<void>(`/api/faq/categories/${id}/`); }
  createQuestion(payload: FAQQuestionInput): Observable<FAQQuestion> { return this.http.post<FAQQuestion>('/api/faq/questions/', payload); }
  updateQuestion(id: number, payload: FAQQuestionInput): Observable<FAQQuestion> { return this.http.patch<FAQQuestion>(`/api/faq/questions/${id}/`, payload); }
  deleteQuestion(id: number): Observable<void> { return this.http.delete<void>(`/api/faq/questions/${id}/`); }
}
