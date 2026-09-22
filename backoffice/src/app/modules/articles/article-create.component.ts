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
  selector: 'app-article-create',
  imports: [FormsModule, BackofficePageComponent, ArticleCategorySelectComponent, ArticleTagInputComponent, ArticleImagePickerComponent, ArticleHtmlEditorComponent],
  templateUrl: './article-create.component.html',
  styleUrl: './article-create.component.css',
})
export class ArticleCreateComponent {
  private readonly articlesApi = inject(ArticleService);
  private readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  protected categories: ArticleCategory[] = [];
  protected availableTags: ArticleTag[] = [];
  protected draft: ArticleInput = this.emptyDraft();
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected activeLanguage: 'en' | 'vi' = 'en';
  protected readonly englishTranslation = this.translation('en');
  protected readonly vietnameseTranslation = this.translation('vi');

  constructor() {
    this.articlesApi.categories().subscribe({
      next: (categories) => { this.categories = categories; this.articlesApi.tags().subscribe({ next: (tags) => { this.availableTags = tags; this.loading = false; }, error: () => { this.loading = false; } }); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load categories.'; this.loading = false; },
    });
  }

  protected can(permission: string): boolean { return this.auth.user()?.permissions.includes(permission) || false; }

  protected switchLanguage(language: 'en' | 'vi'): void {
    this.activeLanguage = language;
  }

  protected translationsReady(): boolean {
    return Boolean(this.englishTranslation.title.trim() && this.englishTranslation.url_key.trim() && this.vietnameseTranslation.title.trim() && this.vietnameseTranslation.url_key.trim());
  }

  protected save(): void {
    this.draft.translation = this.activeLanguage === 'en' ? this.englishTranslation : this.vietnameseTranslation;
    this.draft.translations = [this.englishTranslation, this.vietnameseTranslation];
    this.saving = true;
    this.error = '';
    this.articlesApi.create(this.draft).subscribe({
      next: () => {
        this.saving = false;
        this.toast.show('Article created successfully.');
        this.goToList();
      },
      error: (response) => { this.saving = false; this.error = response.error?.detail || 'Unable to create article.'; },
    });
  }

  protected goToList(): void {
    window.location.hash = 'articles';
  }

  private emptyDraft(): ArticleInput {
    return {
      name: '', type: 'article', status: 2, category_ids: [], tags: [], tag_ids: [], image_id: null,
      cta: { label: '', url: '', phone: '' },
      translation: { language_code: 'en', title: '', sub_title: '', content: '', short_description: '', url_key: '', seo_title: '', meta_description: '' },
    };
  }

  private translation(language_code: 'en' | 'vi'): ArticleInput['translation'] {
    return { language_code, title: '', sub_title: '', content: '', short_description: '', url_key: '', seo_title: '', meta_description: '' };
  }

}
