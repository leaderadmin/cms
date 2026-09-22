import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe, DecimalPipe } from '@angular/common';
import { BackofficePageComponent } from '../../shared/ui';
import { Article } from './article.models';
import { ArticleService } from './article.service';
import { AuthService } from '../auth';
import { ToastService } from '../../shared/ui';
import { MediaService } from '../media';

@Component({
  selector: 'app-article-management',
  imports: [FormsModule, DatePipe, DecimalPipe, BackofficePageComponent],
  templateUrl: './article-management.component.html',
  styleUrl: './article-management.component.css',
})
export class ArticleManagementComponent {
  private readonly articlesApi = inject(ArticleService);
  private readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly mediaApi = inject(MediaService);
  protected readonly thumbnailUrls = new Map<number, string>();
  protected articles: Article[] = [];
  protected query = '';
  protected status = '';
  protected language = 'vi';
  protected loading = true;
  protected error = '';
  protected page = 1;
  protected readonly pageSize = 25;
  protected total = 0;


  constructor() {
    this.load();
  }

  protected load(page = 1): void {
    this.page = Math.max(1, page);
    this.loading = true;
    this.articlesApi.list(this.query.trim(), this.status, this.language, this.page, this.pageSize).subscribe({
      next: (response) => { this.articles = response.results; this.articles.filter((article) => article.image).forEach((article) => this.loadThumbnail(article.image!.id)); this.page = response.page; this.total = response.count; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load articles.'; this.loading = false; },
    });
  }

  protected get totalPages(): number { return Math.max(1, Math.ceil(this.total / this.pageSize)); }

  protected goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages && page !== this.page) this.load(page);
  }

  protected categoryNames(article: Article): string {
    return article.categories.slice(0, 2).map((category) => category.title || category.name).join(', ') || 'Uncategorized';
  }

  protected thumbnailUrl(article: Article): string { return this.thumbnailUrls.get(article.id) || ''; }

  protected can(permission: string): boolean { return this.auth.user()?.permissions.includes(permission) || false; }

  protected startCreate(): void {
    window.location.hash = 'articles/new';
  }

  protected startEdit(article: Article): void {
    window.location.hash = `articles/${article.id}/edit`;
  }

  protected publish(article: Article): void {
    this.articlesApi.publish(article.id, this.language || 'vi').subscribe({
      next: () => { this.toast.show('Article published.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to publish article.'; },
    });
  }

  protected archive(article: Article): void {
    if (!window.confirm(`Archive "${article.translation?.title || article.name}"?`)) return;
    this.articlesApi.archive(article.id).subscribe({
      next: () => { this.toast.show('Article archived.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to archive article.'; },
    });
  }

  private loadThumbnail(imageId: number): void {
    this.mediaApi.preview(imageId).subscribe({ next: (blob) => this.thumbnailUrls.set(imageId, URL.createObjectURL(blob)) });
  }

}
