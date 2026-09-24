import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { ProductMetadata } from './product.models';
import { ProductService } from './product.service';

@Component({
  selector: 'app-product-metadata-form',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './product-metadata-form.component.html',
  styleUrl: './product-metadata-form.component.css',
})
export class ProductMetadataFormComponent {
  private readonly productsApi = inject(ProductService);
  private readonly toast = inject(ToastService);
  protected readonly kind = this.resolveKind();
  protected readonly editId = this.resolveEditId();
  protected metadata: ProductMetadata = { groups: [], types: [], categories: [], attributes: [], attribute_sets: [], product_tags: [] };
  protected name = '';
  protected slug = '';
  protected productTypeId: number | null = null;
  protected valueType = 'text';
  protected selectedAttributeIds: number[] = [];
  protected loading = Boolean(this.editId) || this.kind === 'attribute_set' || this.kind === 'attribute' || this.kind === 'group';
  protected saving = false;
  protected error = '';

  constructor() {
    if (this.isGroup) this.productTypeId = this.resolveProductTypeId();
    if (this.loading) {
      this.productsApi.metadata().subscribe({ next: (metadata) => { this.metadata = metadata; this.loadExisting(); this.loading = false; }, error: (response) => { this.error = response.error?.detail || 'Unable to load metadata.'; this.loading = false; } });
    } else if (this.editId) {
      this.loadExisting();
    }
  }

  protected get title(): string { return this.editId ? `Edit ${this.label}` : `Create ${this.label}`; }
  protected get label(): string { return this.kind === 'type' ? 'product type' : this.kind === 'group' ? 'product group' : this.kind === 'attribute' ? 'Product Attribute' : 'Attribute set'; }
  protected get eyebrow(): string { return `CONTENT / PRODUCTS / ${this.label.toUpperCase()} / ${this.editId ? 'EDIT' : 'NEW'}`; }
  protected get isAttributeSet(): boolean { return this.kind === 'attribute_set'; }
  protected get isAttribute(): boolean { return this.kind === 'attribute'; }
  protected get isGroup(): boolean { return this.kind === 'group'; }

  protected save(): void {
    if (!this.name.trim()) { this.error = 'Name is required.'; return; }
    if (this.isGroup && !this.productTypeId) { this.error = 'Select a product type.'; return; }
    this.saving = true;
    this.error = '';
    const extra = this.isGroup ? { product_type_id: this.productTypeId } : this.isAttribute ? { value_type: this.valueType } : this.isAttributeSet ? { attribute_ids: this.selectedAttributeIds } : {};
    const request = this.editId
      ? this.productsApi.updateMetadata(this.kind, this.editId, this.name.trim(), this.slug.trim(), extra)
      : this.productsApi.createMetadata(this.kind, this.name.trim(), this.slug.trim(), extra);
    request.subscribe({ next: () => { this.toast.show(`${this.label} ${this.editId ? 'updated' : 'created'}.`); this.goToList(); }, error: (response) => { this.error = response.error?.detail || `Unable to save ${this.label}.`; this.saving = false; } });
  }

  protected toggleAttribute(id: number): void { this.selectedAttributeIds = this.selectedAttributeIds.includes(id) ? this.selectedAttributeIds.filter((item) => item !== id) : [...this.selectedAttributeIds, id]; }
  protected goToList(): void { window.location.hash = this.kind === 'attribute_set' || this.kind === 'attribute' ? 'attribute-sets' : 'product-sets'; }

  private loadExisting(): void {
    if (!this.editId) return;
    const items: any[] = this.kind === 'type' ? this.metadata.types : this.kind === 'group' ? this.metadata.groups : this.kind === 'attribute' ? this.metadata.attributes : this.metadata.attribute_sets;
    const item = items.find((entry) => Number(entry.id) === this.editId);
    if (item) { this.name = item.name; this.slug = item.slug; this.productTypeId = item.product_type_id || null; this.valueType = item.value_type || 'text'; this.selectedAttributeIds = item.attribute_ids || []; }
  }

  private resolveKind(): string { const match = window.location.hash.match(/^#(product-sets|product-groups|attributes|attribute-sets)(?:\/new|\/edit\/\d+)?/); const value = match?.[1]; return value === 'product-sets' ? 'type' : value === 'product-groups' ? 'group' : value === 'attributes' ? 'attribute' : 'attribute_set'; }
  private resolveEditId(): number | null { const match = window.location.hash.match(/\/edit\/(\d+)$/); return match ? Number(match[1]) : null; }
  private resolveProductTypeId(): number | null { const match = window.location.hash.match(/product_type_id=(\d+)/); return match ? Number(match[1]) : null; }
}
