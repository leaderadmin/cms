import { DatePipe } from '@angular/common';
import { Component, inject, Input, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { ContentArticle, ContentCategory, PageService } from './page.service';
import { DynamicForm, ReusablePageComponent, ReusablePageComponentInput } from './page.models';

@Component({
  selector: 'app-block-management',
  imports: [FormsModule, DatePipe, BackofficePageComponent, RichEditorComponent],
  templateUrl: './block-management.component.html',
  styleUrl: './block-management-redesign.css',
})
export class BlockManagementComponent implements OnInit {
  @Input() blockId: number | null = null;
  @Input() createMode = false;
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected blocks: ReusablePageComponent[] = [];
  protected articles: ContentArticle[] = [];
  protected articlePage = 1;
  protected articlePageSize = 25;
  protected articleTotal = 0;
  protected articlesLoading = false;
  protected categories: ContentCategory[] = [];
  protected forms: DynamicForm[] = [];
  protected articleQuery = '';
  protected selected: ReusablePageComponent | null = null;
  protected query = '';
  protected page = 1;
  protected pageSize = 10;
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected form: ReusablePageComponentInput = this.emptyForm();

  constructor() {
    this.loadArticles();
    this.pagesApi.categories().subscribe({ next: (categories) => { this.categories = categories; } });
    this.pagesApi.forms().subscribe({ next: (forms) => { this.forms = forms; } });
  }

  ngOnInit(): void { this.load(); }

  protected get totalPages(): number { return Math.max(1, Math.ceil(this.blocks.length / this.pageSize)); }
  protected get pageNumbers(): Array<number | null> { return this.paginationPages(this.page, this.totalPages); }
  protected get pagedBlocks(): ReusablePageComponent[] { const start = (this.page - 1) * this.pageSize; return this.blocks.slice(start, start + this.pageSize); }
  protected get firstVisibleBlock(): number { return this.blocks.length ? (this.page - 1) * this.pageSize + 1 : 0; }
  protected get lastVisibleBlock(): number { return Math.min(this.page * this.pageSize, this.blocks.length); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.components(this.query.trim()).subscribe({
      next: (blocks) => { this.blocks = blocks; this.page = Math.min(this.page, this.totalPages); this.selected = this.blockId ? blocks.find((item) => item.id === this.blockId) || null : null; if (this.createMode) this.create(); else if (this.blockId && this.selected) this.edit(this.selected); this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load blocks.'; this.loading = false; },
    });
  }

  protected goToPage(page: number): void { this.page = Math.min(Math.max(page, 1), this.totalPages); }
  protected changePageSize(size: string): void { this.pageSize = Number(size); this.page = 1; }

  protected create(): void { this.selected = null; this.form = this.emptyForm(); this.editorOpen = true; if (window.location.hash !== '#blocks/new') window.location.hash = '#blocks/new'; }
  protected edit(block: ReusablePageComponent): void { this.selected = block; this.form = structuredClone({ name: block.name, block_name: block.block_name, short_code: block.short_code || block.block_name, html: block.html, css: block.css, js: block.js, content: block.content, status: block.status }); this.editorOpen = true; if (window.location.hash !== `#blocks/edit/${block.id}`) window.location.hash = `#blocks/edit/${block.id}`; }
  protected cancel(): void { this.editorOpen = false; this.selected = null; window.location.hash = '#blocks'; }

  protected save(): void {
    if (!this.form.name.trim() || !this.form.block_name.trim()) return;
    this.saving = true;
    const request = this.selected ? this.pagesApi.updateComponent(this.selected.id, this.form) : this.pagesApi.createComponent(this.form);
    request.subscribe({
      next: (block) => { const wasCreating = !this.selected; this.toast.show(wasCreating ? 'Block created.' : 'Block updated.'); this.selected = block; this.editorOpen = false; this.saving = false; window.location.hash = `#blocks/edit/${block.id}`; },
      error: (response) => { this.error = response.error?.detail || 'Unable to save block.'; this.saving = false; },
    });
  }

  protected remove(block: ReusablePageComponent): void {
    if (!window.confirm(`Xóa block ${block.name}?`)) return;
    this.pagesApi.deleteComponent(block.id).subscribe({ next: () => { this.toast.show('Block deleted.'); this.selected = null; window.location.hash = '#blocks'; }, error: (response) => { this.error = response.error?.detail || 'Unable to delete block.'; } });
  }

  protected contentSourceMode(): string {
    const source = this.parseContent()['source'];
    return !source || source.collection === 'html' ? 'html' : source.collection === 'form' ? 'form' : source?.filter?.category_id ? 'category' : 'selected';
  }
  protected setContentSourceMode(mode: string): void {
    const content = this.parseContent();
    const source = { collection: mode === 'html' ? 'html' : mode === 'form' ? 'form' : 'articles', filter: {}, limit: 6 } as any;
    if (mode === 'form') source.filter.short_code = this.forms[0]?.short_code || '';
    if (mode === 'category') source.filter.category_id = this.categories[0]?.id;
    if (mode === 'selected') source.filter.ids = [];
    content['source'] = source;
    this.form.content = JSON.stringify(content, null, 2);
  }
  protected contentCategoryId(): number | '' { return Number(this.parseContent()['source']?.filter?.category_id) || ''; }
  protected contentFormShortCode(): string { return this.parseContent()['source']?.filter?.short_code || ''; }
  protected setContentForm(shortCode: string): void { const content = this.parseContent(); content['source'] = { collection: 'form', filter: { short_code: shortCode }, limit: 1 }; this.form.content = JSON.stringify(content, null, 2); }
  protected setContentCategory(value: string): void { const content = this.parseContent(); content['source'] = { collection: 'articles', filter: { category_id: Number(value) }, limit: 6 }; this.form.content = JSON.stringify(content, null, 2); }
  protected contentArticleSelected(articleId: number): boolean { return Boolean(this.parseContent()['source']?.filter?.ids?.includes(articleId)); }
  protected get articleTotalPages(): number { return Math.max(1, Math.ceil(this.articleTotal / this.articlePageSize)); }
  protected get articlePageNumbers(): Array<number | null> { return this.paginationPages(this.articlePage, this.articleTotalPages); }
  protected loadArticles(page = 1): void {
    this.articlesLoading = true;
    this.pagesApi.articles(this.articleQuery.trim(), page, this.articlePageSize).subscribe({
      next: (response) => { this.articles = response.results; this.articlePage = response.page; this.articleTotal = response.count; this.articlesLoading = false; },
      error: () => { this.articles = []; this.articleTotal = 0; this.articlesLoading = false; },
    });
  }
  protected searchArticles(): void { this.loadArticles(1); }
  protected goToArticlePage(page: number): void { if (page >= 1 && page <= this.articleTotalPages && page !== this.articlePage) this.loadArticles(page); }
  private paginationPages(page: number, totalPages: number): Array<number | null> {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, index) => index + 1);
    const pages = new Set([1, totalPages, page, page - 1, page + 1]);
    const result: Array<number | null> = [];
    for (let number = 1; number <= totalPages; number += 1) {
      if (pages.has(number)) result.push(number);
      else if (result[result.length - 1] !== null) result.push(null);
    }
    return result;
  }
  protected toggleContentArticle(articleId: number, checked: boolean): void {
    const content = this.parseContent();
    const source = content['source'] || { collection: 'articles', filter: { ids: [] }, limit: 6 };
    const ids = Array.isArray(source.filter?.ids) ? source.filter.ids : [];
    source.collection = 'articles'; source.filter = { ids: checked ? [...new Set([...ids, articleId])] : ids.filter((id: number) => id !== articleId) };
    content['source'] = source;
    this.form.content = JSON.stringify(content, null, 2);
  }
  private parseContent(): Record<string, any> { try { const value = JSON.parse(this.form.content || '{}'); return value && typeof value === 'object' && !Array.isArray(value) ? value : {}; } catch { return {}; } }

  protected renderDocument(block: Pick<ReusablePageComponentInput, 'html' | 'css' | 'js'>): string {
    return `<!doctype html><html><head><meta charset="utf-8"><style>${block.css}</style></head><body>${block.html}<script>${block.js}</script></body></html>`;
  }

  private emptyForm(): ReusablePageComponentInput { return { name: '', block_name: '', short_code: '', html: '<section class="block">\n  <h2>{{ title }}</h2>\n</section>', css: '.block { padding: 24px; }', js: '', content: '{"title":"New block"}', status: 'draft' }; }
}
