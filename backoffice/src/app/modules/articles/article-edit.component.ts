import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent } from '../../shared/ui';
import { AuthService } from '../auth';
import { ToastService } from '../../shared/ui';
import { ArticleCategory, ArticleInput, ArticleTag } from './article.models';
import { ArticleService } from './article.service';
import { ArticleCategorySelectComponent } from './article-category-select.component';
import { ArticleHtmlEditorComponent } from './article-html-editor.component';
import { ArticleTagInputComponent } from './article-tag-input.component';
import { ArticleImagePickerComponent } from './article-image-picker.component';

@Component({
  selector: 'app-article-edit',
  imports: [FormsModule, BackofficePageComponent, ArticleCategorySelectComponent, ArticleTagInputComponent, ArticleImagePickerComponent, ArticleHtmlEditorComponent],
  templateUrl: './article-edit.component.html',
  styleUrl: './article-edit.component.css',
})
export class ArticleEditComponent {
  private readonly articlesApi = inject(ArticleService);
  private readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  protected categories: ArticleCategory[] = [];
  protected availableTags: ArticleTag[] = [];
  protected draft: ArticleInput = this.emptyDraft();
  protected title = 'Edit article';
  protected loading = true;
  protected saving = false;
  protected error = '';

  constructor() {
    const articleId = Number(window.location.hash.match(/^#articles\/(\d+)\/edit$/)?.[1]);
    if (!articleId) {
      this.error = 'Invalid article URL.';
      this.loading = false;
      return;
    }
    this.articlesApi.categories().subscribe({
      next: (categories) => { this.categories = categories; this.articlesApi.tags().subscribe({ next: (tags) => { this.availableTags = tags; this.loadArticle(articleId); }, error: () => this.loadArticle(articleId) }); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load categories.'; this.loading = false; },
    });
  }

  protected can(permission: string): boolean { return this.auth.user()?.permissions.includes(permission) || false; }

  protected save(): void {
    const articleId = Number(window.location.hash.match(/^#articles\/(\d+)\/edit$/)?.[1]);
    if (!articleId) return;
    this.saving = true;
    this.error = '';
    this.articlesApi.update(articleId, this.draft).subscribe({
      next: () => { this.saving = false; this.toast.show('Article updated successfully.'); this.goToList(); },
      error: (response) => { this.saving = false; this.error = response.error?.detail || 'Unable to update article.'; },
    });
  }

  protected goToList(): void { window.location.hash = 'articles'; }

  private loadArticle(articleId: number): void {
    this.articlesApi.get(articleId).subscribe({
      next: (article) => {
        const translation = article.translation;
        this.title = translation?.title || article.name;
        this.draft = {
          name: article.name,
          type: article.type,
          status: article.status,
          category_ids: article.categories.length ? [article.categories[0].id] : [],
          tags: article.tags || [],
          tag_ids: article.tag_ids || [],
          image_id: article.image?.id || null,
          cta: { label: article.cta?.label || '', url: article.cta?.url || '', phone: article.cta?.phone || '' },
          translation: {
            language_code: translation?.language_code || 'vi',
            title: translation?.title || article.name,
            sub_title: translation?.sub_title || '',
            content: translation?.content || '',
            short_description: translation?.short_description || '',
            url_key: translation?.url_key || '',
            seo_title: translation?.seo_title || '',
            meta_description: translation?.meta_description || '',
          },
        };
        this.loading = false;
      },
      error: (response) => { this.error = response.error?.detail || 'Unable to load article.'; this.loading = false; },
    });
  }

  private emptyDraft(): ArticleInput {
    return {
      name: '', type: 'article', status: 2, category_ids: [], tags: [], tag_ids: [], image_id: null,
      cta: { label: '', url: '', phone: '' },
      translation: { language_code: 'vi', title: '', sub_title: '', content: '', short_description: '', url_key: '', seo_title: '', meta_description: '' },
    };
  }
}
