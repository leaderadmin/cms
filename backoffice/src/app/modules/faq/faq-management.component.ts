import { CommonModule } from '@angular/common';
import { Component, inject, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { FAQCategory, FAQCategoryInput, FAQQuestion, FAQQuestionInput } from './faq.models';
import { FAQService } from './faq.service';
@Component({ selector: 'app-faq-management', imports: [CommonModule, FormsModule, BackofficePageComponent, RichEditorComponent], templateUrl: './faq-management.component.html', styleUrl: './faq-management.component.css' })
export class FAQManagementComponent {
  protected readonly math = Math;
  @Input() mode: 'categories' | 'questions' = 'questions';
  private readonly api = inject(FAQService); private readonly toast = inject(ToastService);
  protected categories: FAQCategory[] = []; protected loading = true; protected saving = false; protected error = ''; protected query = ''; protected page = 1; protected pageSize = 10; protected editor: 'category' | 'question' | null = null; protected editingCategoryId: number | null = null; protected editingQuestionId: number | null = null; protected categoryForm = this.emptyCategory(); protected questionForm = this.emptyQuestion();
  protected get questions(): Array<FAQQuestion & { category_name: string }> { return this.categories.flatMap((category) => category.questions.map((question) => ({ ...question, category_name: category.name }))); }
  protected get visibleCategories(): FAQCategory[] { const start = (this.page - 1) * this.pageSize; return this.categories.slice(start, start + this.pageSize); }
  protected get visibleQuestions(): Array<FAQQuestion & { category_name: string }> { const start = (this.page - 1) * this.pageSize; return this.questions.slice(start, start + this.pageSize); }
  protected get totalItems(): number { return this.mode === 'categories' ? this.categories.length : this.questions.length; }
  protected get totalPages(): number { return Math.max(1, Math.ceil(this.totalItems / this.pageSize)); }
  constructor() { this.load(); }
  protected load(): void { this.loading = true; this.page = 1; this.api.list(this.query.trim()).subscribe({ next: (items) => { this.categories = items; this.loading = false; }, error: (response) => { this.error = response.error?.detail || 'Unable to load FAQs'; this.loading = false; } }); }
  protected setPage(page: number): void { this.page = Math.min(Math.max(page, 1), this.totalPages); }
  protected setPageSize(size: number): void { this.pageSize = Number(size); this.page = 1; }
  protected openCategory(category?: FAQCategory): void { this.editor = 'category'; this.editingCategoryId = category?.id || null; this.categoryForm = category ? { name: category.name, slug: category.slug, ordering: category.ordering, status: category.status } : this.emptyCategory(); }
  protected openQuestion(question?: FAQQuestion, categoryId?: number): void { this.editor = 'question'; this.editingQuestionId = question?.id || null; this.questionForm = question ? { ...question } : { ...this.emptyQuestion(), category_id: categoryId || this.categories[0]?.id || 0 }; }
  protected closeEditor(): void { this.editor = null; this.editingCategoryId = null; this.editingQuestionId = null; }
  protected saveCategory(): void { this.saving = true; const request = this.editingCategoryId ? this.api.updateCategory(this.editingCategoryId, this.categoryForm) : this.api.createCategory(this.categoryForm); request.subscribe({ next: () => { this.editor = null; this.saving = false; this.toast.show('FAQ category saved.'); this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to save FAQ category'; this.saving = false; } }); }
  protected saveQuestion(): void { this.saving = true; const request = this.editingQuestionId ? this.api.updateQuestion(this.editingQuestionId, this.questionForm) : this.api.createQuestion(this.questionForm); request.subscribe({ next: () => { this.editor = null; this.saving = false; this.toast.show('FAQ question saved.'); this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to save FAQ question'; this.saving = false; } }); }
  protected removeCategory(item: FAQCategory): void { if (window.confirm(`Delete FAQ category "${item.name}" and its questions?`)) this.api.deleteCategory(item.id).subscribe(() => this.load()); }
  protected removeQuestion(item: FAQQuestion): void { if (window.confirm('Delete this FAQ question?')) this.api.deleteQuestion(item.id).subscribe(() => this.load()); }
  private emptyCategory(): FAQCategoryInput { return { name: '', slug: '', ordering: 0, status: 1 }; }
  private emptyQuestion(): FAQQuestionInput { return { category_id: 0, question_vi: '', answer_vi: '', question_en: '', answer_en: '', ordering: 0, status: 1 }; }
}
