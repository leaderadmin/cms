import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { PageService } from './page.service';
import { PageInput, PageTemplate } from './page.models';

@Component({
  selector: 'app-page-create',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './page-create.component.html',
  styleUrl: './page-create.component.css',
})
export class PageCreateComponent {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected templates: PageTemplate[] = [];
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected form: PageInput = { name: '', slug: '', template_key: '', status: 'draft', components: [] };
  protected step = 1;

  protected get selectedTemplateName(): string {
    return this.templates.find((template) => template.key === this.form.template_key)?.name || this.form.template_key;
  }

  constructor() {
    this.pagesApi.templates().subscribe({
      next: (templates) => { this.templates = templates; this.form.template_key = templates[0]?.key || ''; this.loading = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load templates.'; this.loading = false; },
    });
  }

  protected cancel(): void { window.location.hash = '#pages'; }
  protected next(): void {
    this.error = '';
    if (this.step === 1 && (!this.form.name.trim() || !this.form.slug.trim())) {
      this.error = 'Vui lòng nhập tên page và slug.';
      return;
    }
    if (this.step === 2 && !this.form.template_key) {
      this.error = 'Vui lòng chọn template.';
      return;
    }
    this.step = Math.min(3, this.step + 1);
  }
  protected back(): void { this.error = ''; this.step = Math.max(1, this.step - 1); }
  protected save(): void {
    if (!this.form.name.trim() || !this.form.slug.trim() || !this.form.template_key) { this.error = 'Vui lòng nhập tên, slug và chọn template.'; return; }
    this.saving = true;
    this.error = '';
    this.pagesApi.create(this.form).subscribe({
      next: (page) => { this.toast.show('Page created.'); window.location.hash = `#pages/edit/${page.id}`; },
      error: (response) => { this.error = response.error?.detail || 'Unable to create page.'; this.saving = false; },
    });
  }
}
