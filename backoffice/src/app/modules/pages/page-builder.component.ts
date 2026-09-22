import { Component, inject, Input, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { PageService } from './page.service';
import { Page, PageComponentDefinition, PageInput, PageTemplate } from './page.models';

interface BuilderRegion {
  id: string;
  label: string;
  locked: boolean;
  maxBlocks: number | null;
  allowedBlocks: string[];
}

interface PlacedBlock { type: string; props: Record<string, unknown>; }

@Component({
  selector: 'app-page-builder',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './page-builder.component.html',
  styleUrl: './page-builder.component.css',
})
export class PageBuilderComponent implements OnInit {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected pages: Page[] = [];
  protected templates: PageTemplate[] = [];
  protected components: PageComponentDefinition[] = [];
  protected selected: Page | null = null;
  protected regions: BuilderRegion[] = [];
  protected draft: Record<string, PlacedBlock[]> = {};
  protected loading = true;
  protected saving = false;
  protected error = '';
  @Input() pageId: number | null = null;
  protected newPage: PageInput = { name: '', slug: '', template_key: '', status: 'draft', components: [] };
  private draggedType: string | null = null;
  private draggedIndex: number | null = null;
  private draggedRegionId: string | null = null;

  ngOnInit(): void { this.load(); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.list().subscribe({
      next: (pages) => { this.pages = pages; this.selected = (this.pageId ? pages.find((page) => page.id === this.pageId) : pages[0]) || null; if (this.pageId && !this.selected) this.error = 'Page không tồn tại.'; this.loadDependencies(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load pages.'; this.loading = false; },
    });
  }

  private loadDependencies(): void {
    this.pagesApi.templates().subscribe({
      next: (templates) => { this.templates = templates; if (!this.newPage.template_key) this.newPage.template_key = templates[0]?.key || ''; this.loadComponents(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load page templates.'; this.loading = false; },
    });
  }

  private loadComponents(): void {
    this.pagesApi.componentDefinitions().subscribe({
      next: (components) => { this.components = components; this.loadSelectedDraft(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load components.'; this.loading = false; },
    });
  }

  protected select(page: Page): void { this.selected = page; this.loadSelectedDraft(); }

  protected createPage(): void {
    if (!this.newPage.name.trim() || !this.newPage.slug.trim() || !this.newPage.template_key) {
      this.error = 'Vui lòng nhập tên page, slug và chọn template trước khi tạo.';
      return;
    }
    this.error = '';
    this.saving = true;
    this.pagesApi.create(this.newPage).subscribe({ next: (page) => { this.toast.show('Page created.'); this.newPage = { name: '', slug: '', template_key: this.templates[0]?.key || '', status: 'draft', components: [] }; this.pages = [...this.pages, page]; this.selected = page; this.saving = false; this.loadComponents(); }, error: (response) => { this.error = response.error?.detail || 'Unable to create page.'; this.saving = false; } });
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
    items.push({ type, props: {} });
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
  protected removeFromRegion(region: BuilderRegion, index: number): void { this.draft[region.id].splice(index, 1); }
  protected itemLabel(type: string): string { return this.components.find((item) => item.component_key === type)?.name || type; }
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
