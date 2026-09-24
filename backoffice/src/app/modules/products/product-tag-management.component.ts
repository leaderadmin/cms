import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { ProductService } from './product.service';
import { ProductTag } from './product.models';

@Component({
  selector: 'app-product-tag-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './product-tag-management.component.html',
  styleUrl: './product-tag-management.component.css',
})
export class ProductTagManagementComponent {
  private readonly api = inject(ProductService);
  private readonly toast = inject(ToastService);
  protected tags: ProductTag[] = [];
  protected query = '';
  protected name = '';
  protected slug = '';
  protected editingId: number | null = null;
  protected loading = true;
  protected saving = false;
  protected error = '';

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.api.tags(this.query.trim()).subscribe({
      next: (tags) => { this.tags = tags; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load product tags.'; this.loading = false; },
    });
  }

  protected edit(tag: ProductTag): void { this.editingId = tag.id; this.name = tag.name; this.slug = tag.slug; }
  protected newTag(): void { this.editingId = 0; this.name = ''; this.slug = ''; }
  protected cancel(): void { this.editingId = null; this.name = ''; this.slug = ''; }

  protected save(): void {
    if (!this.name.trim()) return;
    this.saving = true;
    const request = this.editingId ? this.api.updateTag(this.editingId, { name: this.name.trim(), slug: this.slug.trim() }) : this.api.createTag({ name: this.name.trim(), slug: this.slug.trim() });
    request.subscribe({
      next: () => { this.toast.show(this.editingId ? 'Product tag updated.' : 'Product tag created.'); this.saving = false; this.cancel(); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save product tag.'; this.saving = false; },
    });
  }

  protected remove(tag: ProductTag): void {
    if (!window.confirm(`Delete "${tag.name}"?`)) return;
    this.api.deleteTag(tag.id).subscribe({ next: () => { this.toast.show('Product tag deleted.'); this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to delete product tag.'; } });
  }
}
