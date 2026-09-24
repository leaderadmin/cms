import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { PageService } from './page.service';
import { PageStatus, PageTemplate, PageTemplateInput, PageTemplateRegion } from './page.models';

@Component({
  selector: 'app-page-management',
  imports: [FormsModule, DatePipe, BackofficePageComponent],
  templateUrl: './page-management.component.html',
  styleUrl: './page-management.component.css',
})
export class PageManagementComponent {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected templates: PageTemplate[] = [];
  protected selected: PageTemplate | null = null;
  protected query = '';
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected editingId: number | null = null;
  protected form: PageTemplateInput = this.emptyForm();

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.templates(this.query.trim()).subscribe({
      next: (templates) => { this.templates = templates; this.selected = this.selected ? templates.find((item) => item.id === this.selected?.id) || templates[0] || null : templates[0] || null; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load templates.'; this.loading = false; },
    });
  }

  protected select(template: PageTemplate): void { this.selected = template; this.editorOpen = false; }
  protected openCreate(): void { this.editingId = null; this.form = this.emptyForm(); this.editorOpen = true; }

  protected edit(template: PageTemplate): void {
    this.editingId = template.id;
    this.form = structuredClone({ name: template.name, key: template.key, regions: template.regions, tokens: template.tokens, status: template.status });
    this.editorOpen = true;
  }

  protected cancel(): void { this.editorOpen = false; }
  protected addRegion(): void { this.form.regions.push({ key: `region-${this.form.regions.length + 1}`, label: 'New region', locked: false, max_blocks: null, allowed_blocks: [] }); }
  protected removeRegion(index: number): void { this.form.regions.splice(index, 1); }
  protected blockList(region: PageTemplateRegion): string { return region.allowed_blocks.join(', '); }
  protected setBlockList(region: PageTemplateRegion, value: string): void { region.allowed_blocks = value.split(',').map((block) => block.trim()).filter(Boolean); }

  protected save(): void {
    if (!this.form.name.trim() || !this.form.key.trim() || !this.form.regions.length) return;
    const current = this.selected;
    if (this.editingId && current?.page_count && !window.confirm(`Template này đang được ${current.page_count} trang sử dụng. Thay đổi có thể ảnh hưởng toàn bộ các trang đó. Bạn muốn xem trước và lưu thay đổi?`)) return;
    this.saving = true;
    const request = this.editingId ? this.pagesApi.updateTemplate(this.editingId, this.form) : this.pagesApi.createTemplate(this.form);
    request.subscribe({
      next: (template) => { this.toast.show(this.editingId ? 'Template updated.' : 'Template created.'); this.saving = false; this.editorOpen = false; this.selected = template; this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save template.'; this.saving = false; },
    });
  }

  protected statusLabel(status: PageStatus): string { return status === 'published' ? 'Đang xuất bản' : status === 'draft' ? 'Bản nháp' : 'Đã lưu trữ'; }

  private emptyForm(): PageTemplateInput {
    return {
      name: '', key: '', status: 'published',
      regions: [
        { key: 'header', label: 'header', locked: false, max_blocks: 1, allowed_blocks: [] },
        { key: 'hero', label: 'hero', locked: false, max_blocks: 1, allowed_blocks: ['hero-slider', 'hero-static'] },
        { key: 'main', label: 'main', locked: false, max_blocks: null, allowed_blocks: ['quick-links', 'product-cards', 'exchange-rate-table', 'news-list', 'cta-banner'] },
        { key: 'footer', label: 'footer', locked: false, max_blocks: 1, allowed_blocks: [] },
      ],
      tokens: { primary_color: '#0C447C', radius: '8px', font: 'Inter' },
    };
  }
}
