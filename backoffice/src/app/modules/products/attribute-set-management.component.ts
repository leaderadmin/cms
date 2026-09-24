import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent } from '../../shared/ui';
import { ProductMetadata } from './product.models';
import { ProductService } from './product.service';

@Component({
  selector: 'app-attribute-set-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './attribute-set-management.component.html',
  styleUrl: './attribute-set-management.component.css',
})
export class AttributeSetManagementComponent {
  private readonly productsApi = inject(ProductService);
  protected metadata: ProductMetadata = { groups: [], types: [], categories: [], attributes: [], attribute_sets: [], product_tags: [] };
  protected loading = true;
  protected error = '';
  protected name = '';
  protected slug = '';
  protected selectedAttributeIds: number[] = [];
  protected saving = false;
  protected attributeName = '';
  protected attributeSlug = '';
  protected attributeValueType = 'text';
  protected expandedSetIds = new Set<number>();

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.productsApi.metadata().subscribe({
      next: (metadata) => { this.metadata = metadata; this.loading = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load Attribute sets.'; this.loading = false; },
    });
  }

  protected goToProducts(): void { window.location.hash = 'products'; }
  protected goToAttributeCreate(): void { window.location.hash = 'attributes/new'; }
  protected goToSetCreate(): void { window.location.hash = 'attribute-sets/new'; }
  protected edit(kind: string, id: number): void { window.location.hash = `${kind}/edit/${id}`; }
  protected toggleSet(setId: number): void {
    const expandedSetIds = new Set(this.expandedSetIds);
    if (expandedSetIds.has(setId)) expandedSetIds.delete(setId);
    else expandedSetIds.add(setId);
    this.expandedSetIds = expandedSetIds;
  }
  protected isExpanded(setId: number): boolean { return this.expandedSetIds.has(setId); }

  protected toggleAttribute(id: number): void {
    this.selectedAttributeIds = this.selectedAttributeIds.includes(id)
      ? this.selectedAttributeIds.filter((item) => item !== id)
      : [...this.selectedAttributeIds, id];
  }

  protected createAttribute(): void {
    if (!this.attributeName.trim()) { this.error = 'Attribute name is required.'; return; }
    this.saving = true;
    this.productsApi.createMetadata('attribute', this.attributeName.trim(), this.attributeSlug.trim(), { value_type: this.attributeValueType }).subscribe({
      next: () => { this.attributeName = ''; this.attributeSlug = ''; this.attributeValueType = 'text'; this.saving = false; this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to create Attribute.'; this.saving = false; },
    });
  }

  protected createAttributeSet(): void {
    if (!this.name.trim()) { this.error = 'Attribute set name is required.'; return; }
    this.saving = true;
    this.productsApi.createMetadata('attribute_set', this.name.trim(), this.slug.trim(), { attribute_ids: this.selectedAttributeIds }).subscribe({
      next: () => { this.name = ''; this.slug = ''; this.selectedAttributeIds = []; this.saving = false; this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to create Attribute set.'; this.saving = false; },
    });
  }
}