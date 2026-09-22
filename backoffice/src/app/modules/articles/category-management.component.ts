import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { ArticleCategory, ArticleCategoryInput } from './article.models';
import { ArticleService } from './article.service';

@Component({
  selector: 'app-category-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './category-management.component.html',
  styleUrl: './category-management.component.css',
})
export class CategoryManagementComponent {
  private readonly articlesApi = inject(ArticleService);
  private readonly toast = inject(ToastService);
  protected categories: ArticleCategory[] = [];
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected query = '';
  protected status = '';
  protected type = '';
  protected editingId: number | null = null;
  protected editorOpen = false;
  protected form: ArticleCategoryInput = this.emptyForm();

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.articlesApi.categories(this.query.trim(), this.status, this.type).subscribe({
      next: (categories) => { this.categories = categories; this.loading = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load categories'; this.loading = false; },
    });
  }

  protected openCreate(): void { this.editingId = null; this.editorOpen = true; this.form = this.emptyForm(); this.error = ''; }

  protected edit(category: ArticleCategory): void {
    this.editingId = category.id;
    this.editorOpen = true;
    this.form = {
      name: category.name,
      type: category.type,
      status: category.status,
      parent_id: category.parent_id ?? null,
      ordering: category.ordering ?? 0,
      translation: { language_code: category.translation?.language_code || 'vi', title: category.translation?.title || category.title, description: category.translation?.description || '', url_key: category.translation?.url_key || '', meta_keyword: category.translation?.meta_keyword || '', meta_description: category.translation?.meta_description || '' },
    };
    this.error = '';
  }

  protected save(): void {
    if (!this.form.name.trim()) return;
    this.saving = true;
    const request = this.editingId ? this.articlesApi.updateCategory(this.editingId, this.form) : this.articlesApi.createCategory(this.form);
    request.subscribe({
      next: () => { this.saving = false; this.editingId = null; this.editorOpen = false; this.toast.show('Category saved successfully.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save category'; this.saving = false; },
    });
  }

  protected archive(category: ArticleCategory): void {
    if (!window.confirm(`Archive category "${category.title}"?`)) return;
    this.articlesApi.archiveCategory(category.id).subscribe({
      next: () => { this.toast.show('Category archived.'); if (this.editingId === category.id) { this.editingId = null; this.editorOpen = false; } this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to archive category'; },
    });
  }

  protected cancel(): void { this.editingId = null; this.editorOpen = false; this.error = ''; }

  protected parentName(category: ArticleCategory): string {
    return this.categories.find((item) => item.id === category.parent_id)?.title || 'Root';
  }

  private emptyForm(): ArticleCategoryInput {
    return { name: '', type: 'article', status: 1, parent_id: null, ordering: 0, translation: { language_code: 'vi', title: '', description: '', url_key: '', meta_keyword: '', meta_description: '' } };
  }
}