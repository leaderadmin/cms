import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { PageService } from './page.service';
import { ReusablePageComponent, ReusablePageComponentInput } from './page.models';

@Component({
  selector: 'app-block-management',
  imports: [FormsModule, DatePipe, BackofficePageComponent, RichEditorComponent],
  templateUrl: './block-management.component.html',
  styleUrl: './block-management.component.css',
})
export class BlockManagementComponent {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected blocks: ReusablePageComponent[] = [];
  protected selected: ReusablePageComponent | null = null;
  protected query = '';
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected form: ReusablePageComponentInput = this.emptyForm();

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.components(this.query.trim()).subscribe({
      next: (blocks) => { this.blocks = blocks; this.selected = this.selected ? blocks.find((item) => item.id === this.selected?.id) || null : blocks[0] || null; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load blocks.'; this.loading = false; },
    });
  }

  protected create(): void { this.selected = null; this.form = this.emptyForm(); this.editorOpen = true; }
  protected edit(block: ReusablePageComponent): void { this.selected = block; this.form = structuredClone({ name: block.name, block_name: block.block_name, html: block.html, css: block.css, js: block.js, content: block.content, status: block.status }); this.editorOpen = true; }
  protected cancel(): void { this.editorOpen = false; }

  protected save(): void {
    if (!this.form.name.trim() || !this.form.block_name.trim()) return;
    this.saving = true;
    const request = this.selected ? this.pagesApi.updateComponent(this.selected.id, this.form) : this.pagesApi.createComponent(this.form);
    request.subscribe({
      next: (block) => { this.toast.show(this.selected ? 'Block updated.' : 'Block created.'); this.selected = block; this.editorOpen = false; this.saving = false; this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save block.'; this.saving = false; },
    });
  }

  protected remove(block: ReusablePageComponent): void {
    if (!window.confirm(`Xóa block ${block.name}?`)) return;
    this.pagesApi.deleteComponent(block.id).subscribe({ next: () => { this.toast.show('Block deleted.'); this.selected = null; this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to delete block.'; } });
  }

  protected renderDocument(block: Pick<ReusablePageComponentInput, 'html' | 'css' | 'js'>): string {
    return `<!doctype html><html><head><meta charset="utf-8"><style>${block.css}</style></head><body>${block.html}<script>${block.js}</script></body></html>`;
  }

  private emptyForm(): ReusablePageComponentInput { return { name: '', block_name: '', html: '<section class="block">\n  <h2>{{ title }}</h2>\n</section>', css: '.block { padding: 24px; }', js: '', content: '{"title":"New block"}', status: 'draft' }; }
}
