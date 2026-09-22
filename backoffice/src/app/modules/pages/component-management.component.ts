import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { PageService } from './page.service';
import { PageComponentDefinition, PageComponentDefinitionInput, ReusablePageComponent } from './page.models';

@Component({
  selector: 'app-component-management',
  imports: [FormsModule, DatePipe, BackofficePageComponent, RichEditorComponent],
  templateUrl: './component-management.component.html',
  styleUrl: './component-management.component.css',
})
export class ComponentManagementComponent {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected components: PageComponentDefinition[] = [];
  protected blocks: ReusablePageComponent[] = [];
  protected selected: PageComponentDefinition | null = null;
  protected query = '';
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected form: PageComponentDefinitionInput = this.emptyForm();
  private draggedBlock: string | null = null;
  private draggedIndex: number | null = null;

  constructor() { this.load(); this.loadBlocks(); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.componentDefinitions(this.query.trim()).subscribe({
      next: (components) => { this.components = components; this.selected = this.selected ? components.find((item) => item.id === this.selected?.id) || null : components[0] || null; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load components.'; this.loading = false; },
    });
  }

  protected loadBlocks(): void { this.pagesApi.components().subscribe({ next: (blocks) => { this.blocks = blocks; } }); }
  protected create(): void { this.selected = null; this.form = this.emptyForm(); this.editorOpen = true; }
  protected edit(component: PageComponentDefinition): void { this.selected = component; this.form = structuredClone(component); this.editorOpen = true; }
  protected cancel(): void { this.editorOpen = false; }

  protected save(): void {
    if (!this.form.name.trim() || !this.form.component_key.trim()) return;
    this.saving = true;
    const request = this.selected ? this.pagesApi.updateComponentDefinition(this.selected.id, this.form) : this.pagesApi.createComponentDefinition(this.form);
    request.subscribe({
      next: (component) => { this.toast.show(this.selected ? 'Component updated.' : 'Component created.'); this.selected = component; this.editorOpen = false; this.saving = false; this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save component.'; this.saving = false; },
    });
  }

  protected remove(component: PageComponentDefinition): void {
    if (!window.confirm(`Xóa component ${component.name}?`)) return;
    this.pagesApi.deleteComponentDefinition(component.id).subscribe({ next: () => { this.toast.show('Component deleted.'); this.selected = null; this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to delete component.'; } });
  }

  protected startBlockDrag(blockKey: string, event: DragEvent): void { this.draggedBlock = blockKey; this.draggedIndex = null; event.dataTransfer?.setData('text/plain', blockKey); }
  protected startPlacedDrag(index: number, event: DragEvent): void { this.draggedIndex = index; this.draggedBlock = null; event.dataTransfer?.setData('text/plain', String(index)); }
  protected addBlock(blockKey: string): void {
    if (!this.blocks.some((block) => block.block_name === blockKey) || this.form.blocks.some((block) => block.block_name === blockKey)) return;
    this.form.blocks = [...this.form.blocks, { block_name: blockKey, position: this.form.blocks.length + 1 }];
  }
  protected openBlockManager(): void { window.location.hash = 'blocks'; }
  protected allowDrop(event: DragEvent): void { event.preventDefault(); }
  protected dropBlock(event: DragEvent, targetIndex?: number): void {
    event.preventDefault();
    if (this.draggedIndex !== null && targetIndex !== undefined) {
      const [moved] = this.form.blocks.splice(this.draggedIndex, 1);
      this.form.blocks.splice(targetIndex > this.draggedIndex ? targetIndex - 1 : targetIndex, 0, moved);
    } else {
      const blockKey = this.draggedBlock || event.dataTransfer?.getData('text/plain');
      if (blockKey) this.addBlock(blockKey);
    }
    this.form.blocks = this.form.blocks.map((block, index) => ({ ...block, position: index + 1 }));
    this.draggedBlock = null;
    this.draggedIndex = null;
  }
  protected removeBlock(index: number): void { this.form.blocks.splice(index, 1); this.form.blocks = this.form.blocks.map((block, position) => ({ ...block, position: position + 1 })); }
  protected blockByKey(key: string): ReusablePageComponent | undefined { return this.blocks.find((block) => block.block_name === key); }
  protected renderDocument(value: Pick<PageComponentDefinitionInput, 'prehtml' | 'html' | 'css' | 'js' | 'backhtml'>): string { return `<!doctype html><html><head><meta charset="utf-8"><style>${value.css}</style></head><body>${value.prehtml}${value.html}${value.backhtml}<script>${value.js}</script></body></html>`; }

  private emptyForm(): PageComponentDefinitionInput { return { name: '', component_key: '', prehtml: '', html: '<section class="component">\n  <h2>{{ title }}</h2>\n</section>', css: '.component { padding: 24px; }', js: '', content: '{"title":"New component"}', backhtml: '', blocks: [], status: 'draft' }; }
}
