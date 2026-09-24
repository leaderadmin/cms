import { Component, inject, Input, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { ContentArticle, ContentCategory, ContentProduct, PageService } from './page.service';
import { DynamicForm, Page, PageComponentDefinition, PageContentMode, PageInput, PageTemplate } from './page.models';

interface BuilderRegion {
  id: string;
  label: string;
  locked: boolean;
  maxBlocks: number | null;
  allowedBlocks: string[];
}

interface BlockSource { collection: string; filter: { ids?: number[]; category_id?: number; [key: string]: any }; limit: number; }
interface PlacedBlock { type: string; props: { source: BlockSource; [key: string]: any }; }

@Component({
  selector: 'app-page-builder',
  imports: [FormsModule, BackofficePageComponent, RichEditorComponent],
  templateUrl: './page-builder.component.html',
  styleUrls: ['./page-builder.component.css', './page-builder-overrides.css', './page-content-overrides.css'],
})
export class PageBuilderComponent implements OnInit {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected pages: Page[] = [];
  protected templates: PageTemplate[] = [];
  protected components: PageComponentDefinition[] = [];
  protected articles: ContentArticle[] = [];
  protected categories: ContentCategory[] = [];
  protected contentPages: Page[] = [];
  protected products: ContentProduct[] = [];
  protected forms: DynamicForm[] = [];
  protected selected: Page | null = null;
  protected selectedBlock: PlacedBlock | null = null;
  protected regions: BuilderRegion[] = [];
  protected draft: Record<string, PlacedBlock[]> = {};
  protected loading = true;
  protected saving = false;
  protected error = '';
  @Input() pageId: number | null = null;
  protected newPage: PageInput = { name: '', slug: '', short_code: '', template_key: '', status: 'draft', components: [], article_ids: [], content_config: { mode: 'articles', article_ids: [], html: '', css: '', js: '' } };
  private draggedType: string | null = null;
  private draggedIndex: number | null = null;
  private draggedRegionId: string | null = null;

  ngOnInit(): void { this.load(); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.list().subscribe({
      next: (pages) => { this.pages = pages; this.selected = (this.pageId ? pages.find((page) => page.id === this.pageId) : pages[0]) || null; if (this.selected && !this.selected.content_config) this.selected.content_config = { mode: 'articles', article_ids: this.selected.article_ids || [] }; if (this.pageId && !this.selected) this.error = 'Page không tồn tại.'; this.loadDependencies(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load pages.'; this.loading = false; },
    });
  }

  private loadDependencies(): void {
    this.pagesApi.forms().subscribe({ next: (forms) => { this.forms = forms; } });
    this.pagesApi.templates().subscribe({
      next: (templates) => { this.templates = templates; if (!this.newPage.template_key) this.newPage.template_key = templates[0]?.key || ''; this.loadComponents(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load page templates.'; this.loading = false; },
    });
  }

  private loadComponents(): void {
    this.pagesApi.componentDefinitions().subscribe({
      next: (components) => { this.components = components; this.pagesApi.articles().subscribe({ next: (response) => { this.articles = response.results; this.pagesApi.contentPages().subscribe({ next: (pages) => { this.contentPages = pages; this.pagesApi.products().subscribe({ next: (products) => { this.products = products.results; this.loadCategories(); }, error: () => this.loadCategories() }); }, error: () => this.loadCategories() }); }, error: () => this.loadCategories() }); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load components.'; this.loading = false; },
    });
  }

  private loadCategories(): void {
    this.pagesApi.categories().subscribe({ next: (categories) => { this.categories = categories; this.loadSelectedDraft(); }, error: () => this.loadSelectedDraft() });
  }

  protected select(page: Page): void { this.selected = page; this.loadSelectedDraft(); }

  protected savePageSettings(): void {
    if (!this.selected || !this.selected.name.trim() || !this.selected.slug.trim() || !this.selected.template_key) return;
    this.saving = true;
    const payload: PageInput = {
      name: this.selected.name,
      slug: this.selected.slug,
      short_code: this.selected.short_code || '',
      template_key: this.selected.template_key,
      status: this.selected.status,
      components: this.selected.components,
      article_ids: this.selected.article_ids || [],
      content_config: this.selected.content_config || { mode: 'articles', article_ids: this.selected.article_ids || [] },
    };
    this.pagesApi.update(this.selected.id, payload).subscribe({
      next: (page) => { this.selected = page; this.pages = this.pages.map((item) => item.id === page.id ? page : item); this.toast.show('Page information saved.'); this.saving = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to save page information.'; this.saving = false; },
    });
  }

  protected articleSelected(articleId: number): boolean { return Boolean(this.selected?.article_ids?.includes(articleId)); }
  protected togglePageArticle(articleId: number, checked: boolean): void {
    if (!this.selected) return;
    const articleIds = this.selected.article_ids || [];
    this.selected.article_ids = checked ? [...new Set([...articleIds, articleId])] : articleIds.filter((id) => id !== articleId);
    this.selected.content_config = { ...(this.selected.content_config || { mode: 'articles' }), article_ids: this.selected.article_ids };
  }

  protected pageContentMode(): PageContentMode { return this.selected?.content_config?.mode || 'articles'; }
  protected setPageContentMode(mode: PageContentMode): void { if (this.selected) this.selected.content_config = { ...(this.selected.content_config || { article_ids: this.selected.article_ids || [] }), mode, article_ids: this.selected.article_ids || [], form_short_code: mode === 'form' ? (this.forms[0]?.short_code || '') : this.selected.content_config?.form_short_code }; }
  protected setPageContentForm(shortCode: string): void { if (this.selected) this.selected.content_config = { ...(this.selected.content_config || { mode: 'form', article_ids: [] }), mode: 'form', form_short_code: shortCode, article_ids: this.selected.article_ids || [] }; }
  protected setPageContentCategory(categoryId: string): void { if (this.selected) this.selected.content_config = { ...(this.selected.content_config || { mode: 'category', article_ids: [] }), mode: 'category', category_id: Number(categoryId), article_ids: this.selected.article_ids || [] }; }

  protected createPage(): void {
    if (!this.newPage.name.trim() || !this.newPage.slug.trim() || !this.newPage.template_key) {
      this.error = 'Vui lòng nhập tên page, slug và chọn template trước khi tạo.';
      return;
    }
    this.error = '';
    this.saving = true;
    this.pagesApi.create(this.newPage).subscribe({ next: (page) => { this.toast.show('Page created.'); this.newPage = { name: '', slug: '', short_code: '', template_key: this.templates[0]?.key || '', status: 'draft', components: [], article_ids: [], content_config: { mode: 'articles', article_ids: [], html: '', css: '', js: '' } }; this.pages = [...this.pages, page]; this.selected = page; this.saving = false; this.loadComponents(); }, error: (response) => { this.error = response.error?.detail || 'Unable to create page.'; this.saving = false; } });
  }

  private loadSelectedDraft(): void {
    if (!this.selected) { this.loading = false; return; }
    this.loading = true;
    this.pagesApi.draft(this.selected.slug).subscribe({ next: (response) => { this.draft = (response.version?.regions || {}) as Record<string, PlacedBlock[]>; this.setRegions(); this.loading = false; }, error: (response) => { if (response.status !== 404) this.error = response.error?.detail || 'Unable to load draft.'; this.draft = {}; this.setRegions(); this.loading = false; } });
  }

  private setRegions(): void {
    const template = this.templates.find((item) => item.key === this.selected?.template_key);
    this.regions = (template?.regions || []).map((region: any) => ({ id: String(region.id || region.key), label: region.label || region.id || region.key, locked: Boolean(region.locked), maxBlocks: region.maxBlocks ?? region.max_blocks ?? null, allowedBlocks: region.allowedBlocks || region.allowed_blocks || [] }));
    for (const region of this.regions) if (!this.draft[region.id]) this.draft[region.id] = [];
  }

  protected startPaletteDrag(type: string, event: DragEvent): void { this.draggedType = type; this.draggedIndex = null; event.dataTransfer?.setData('text/plain', type); }
  protected startPlacedDrag(regionId: string, index: number, event: DragEvent): void { this.draggedIndex = index; this.draggedRegionId = regionId; this.draggedType = null; event.dataTransfer?.setData('text/plain', String(index)); }
  protected allowDrop(event: DragEvent): void { event.preventDefault(); }
  protected addToRegion(region: BuilderRegion, type: string): void {
    const items = this.draft[region.id] || (this.draft[region.id] = []);
    if (region.locked || (region.maxBlocks !== null && items.length >= region.maxBlocks) || !this.isAllowed(region, type)) return;
    const block = { type, props: { source: { collection: 'articles', filter: {}, limit: 6 } } };
    items.push(block);
    this.selectBlock(block);
  }
  protected addToFirstAvailableRegion(type: string): void {
    const region = this.regions.find((item) => !item.locked && this.isAllowed(item, type) && (item.maxBlocks === null || this.draft[item.id].length < item.maxBlocks));
    if (region) this.addToRegion(region, type);
  }
  protected dropIntoRegion(event: DragEvent, region: BuilderRegion, targetIndex?: number): void {
    event.preventDefault();
    const items = this.draft[region.id] || (this.draft[region.id] = []);
    if (this.draggedIndex !== null && this.draggedRegionId) {
      const sourceItems = this.draft[this.draggedRegionId] || [];
      const [moved] = sourceItems.splice(this.draggedIndex, 1);
      if (moved && this.draggedRegionId !== region.id && region.locked) {
        sourceItems.splice(this.draggedIndex, 0, moved);
      } else if (moved && this.draggedRegionId !== region.id && (region.maxBlocks === null || items.length < region.maxBlocks) && this.isAllowed(region, moved.type)) {
        items.splice(targetIndex ?? items.length, 0, moved);
      } else if (moved && this.draggedRegionId === region.id) {
        const insertAt = targetIndex !== undefined && targetIndex > this.draggedIndex ? targetIndex - 1 : targetIndex ?? items.length;
        items.splice(insertAt, 0, moved);
      } else if (moved) {
        sourceItems.splice(this.draggedIndex, 0, moved);
      }
    }
    else { const type = this.draggedType || event.dataTransfer?.getData('text/plain'); if (type) this.addToRegion(region, type); }
    this.draggedType = null; this.draggedIndex = null; this.draggedRegionId = null;
  }
  protected removeFromRegion(region: BuilderRegion, index: number): void { const removed = this.draft[region.id].splice(index, 1)[0]; if (removed === this.selectedBlock) this.selectedBlock = null; }
  protected selectBlock(block: PlacedBlock): void { this.selectedBlock = block; }
  protected sourceMode(block: PlacedBlock): string { return block.props.source?.collection === 'pages' ? 'page' : block.props.source?.collection === 'products' ? 'product' : block.props.source?.filter?.ids ? 'selected' : block.props.source?.filter?.category_id ? 'category' : 'all'; }
  protected setSourceMode(mode: string): void {
    if (!this.selectedBlock) return;
    const source = this.selectedBlock.props.source || { collection: 'articles', filter: {}, limit: 6 };
    source.collection = mode === 'page' ? 'pages' : mode === 'product' ? 'products' : 'articles'; source.limit = Number(source.limit) || 6;
    source.filter = mode === 'category' ? { category_id: this.categories[0]?.id } : mode === 'selected' ? { ids: this.articles.slice(0, 1).map((article) => article.id) } : mode === 'page' ? { ids: this.contentPages.slice(0, 1).map((page) => page.id) } : mode === 'product' ? { ids: this.products.slice(0, 1).map((product) => product.id) } : {};
    this.selectedBlock.props.source = source;
  }
  protected setCategory(categoryId: string): void { if (this.selectedBlock) { this.selectedBlock.props.source = { collection: 'articles', filter: { category_id: Number(categoryId) }, limit: this.selectedBlock.props.source?.limit || 6 }; } }
  protected toggleArticle(articleId: number, checked: boolean): void {
    if (!this.selectedBlock) return;
    const source = this.selectedBlock.props.source || { collection: 'articles', filter: { ids: [] }, limit: 6 };
    const ids = Array.isArray(source.filter?.ids) ? [...source.filter.ids] : [];
    const nextIds = checked ? [...new Set([...ids, articleId])] : ids.filter((id: number) => id !== articleId);
    this.selectedBlock.props.source = { collection: 'articles', filter: { ids: nextIds }, limit: source.limit || 6 };
  }
  protected selectedArticle(articleId: number): boolean { return Boolean(this.selectedBlock?.props.source?.filter?.ids?.includes(articleId)); }
  protected togglePage(pageId: number, checked: boolean): void {
    if (!this.selectedBlock) return;
    const source = this.selectedBlock.props.source || { collection: 'pages', filter: { ids: [] }, limit: 6 };
    const ids = Array.isArray(source.filter?.ids) ? [...source.filter.ids] : [];
    const nextIds = checked ? [...new Set([...ids, pageId])] : ids.filter((id: number) => id !== pageId);
    this.selectedBlock.props.source = { collection: 'pages', filter: { ids: nextIds }, limit: source.limit || 6 };
  }
  protected selectedPage(pageId: number): boolean { return Boolean(this.selectedBlock?.props.source?.collection === 'pages' && this.selectedBlock.props.source.filter?.ids?.includes(pageId)); }
  protected toggleProduct(productId: number, checked: boolean): void {
    if (!this.selectedBlock) return;
    const source = this.selectedBlock.props.source || { collection: 'products', filter: { ids: [] }, limit: 6 };
    const ids = Array.isArray(source.filter?.ids) ? [...source.filter.ids] : [];
    const nextIds = checked ? [...new Set([...ids, productId])] : ids.filter((id: number) => id !== productId);
    this.selectedBlock.props.source = { collection: 'products', filter: { ids: nextIds }, limit: source.limit || 6 };
  }
  protected selectedProduct(productId: number): boolean { return Boolean(this.selectedBlock?.props.source?.collection === 'products' && this.selectedBlock.props.source.filter?.ids?.includes(productId)); }
  protected updateLimit(value: string): void { if (this.selectedBlock?.props.source) this.selectedBlock.props.source.limit = Math.max(1, Math.min(50, Number(value) || 6)); }
  protected itemLabel(type: string): string { return this.components.find((item) => item.component_key === type)?.name || type; }
  protected editComponent(type: string, event: Event): void { event.stopPropagation(); const component = this.components.find((item) => item.component_key === type); if (component) window.location.hash = `components?edit=${component.id}`; }
  protected isAllowed(region: BuilderRegion, type: string): boolean {
    return this.components.some((component) => component.component_key === type);
  }
  protected selectById(value: string): void { const page = this.pages.find((item) => item.id === Number(value)); if (page) this.select(page); }
  protected backToList(): void { window.location.hash = '#pages'; }
  protected hasAvailableComponent(type: string): boolean { return this.regions.some((region) => !region.locked && this.isAllowed(region, type) && (region.maxBlocks === null || this.draft[region.id].length < region.maxBlocks)); }
  protected saveDraft(): void {
    if (!this.selected) return;
    this.saving = true;
    this.pagesApi.updateDraft(this.selected.slug, this.draft).subscribe({ next: (response) => { this.selected = response.page; this.toast.show('Draft saved.'); this.saving = false; }, error: (response) => { this.error = response.error?.detail || 'Unable to save draft.'; this.saving = false; } });
  }

  protected publishDraft(): void {
    if (!this.selected || !this.selected.draft_version_id) return;
    this.saving = true;
    this.pagesApi.publish(this.selected.slug).subscribe({
      next: (response) => { this.selected = response.page; this.toast.show('Page published.'); this.saving = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to publish page.'; this.saving = false; },
    });
  }

  private templateFor(page: Page): PageTemplate | undefined { return this.templates.find((item) => item.key === page.template_key); }
}
