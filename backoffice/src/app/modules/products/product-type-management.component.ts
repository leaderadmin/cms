import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent } from '../../shared/ui';
import { ProductMetadata } from './product.models';
import { ProductService } from './product.service';

@Component({
  selector: 'app-product-type-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './product-type-management.component.html',
  styleUrl: './product-type-management.component.css',
})
export class ProductTypeManagementComponent {
  private readonly productsApi = inject(ProductService);
  protected metadata: ProductMetadata = { groups: [], types: [], categories: [], attributes: [], attribute_sets: [], product_tags: [] };
  protected loading = true;
  protected error = '';
  protected expandedTypeIds = new Set<number>();

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.productsApi.metadata().subscribe({
      next: (metadata) => { this.metadata = metadata; this.loading = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load catalog structure.'; this.loading = false; },
    });
  }

  protected goToProducts(): void { window.location.hash = 'products'; }
  protected goToCreate(): void { window.location.hash = 'product-sets/new'; }
  protected goToGroupCreate(typeId?: number): void { window.location.hash = typeId ? `product-groups/new?product_type_id=${typeId}` : 'product-groups/new'; }
  protected goToProductCreate(groupSlug: string): void { window.location.hash = `products/new?group=${encodeURIComponent(groupSlug)}`; }
  protected edit(kind: string, id: number): void { window.location.hash = `${kind}/${id}/edit`; }

  protected toggleType(typeId: number): void {
    const expandedTypeIds = new Set(this.expandedTypeIds);
    if (expandedTypeIds.has(typeId)) expandedTypeIds.delete(typeId);
    else expandedTypeIds.add(typeId);
    this.expandedTypeIds = expandedTypeIds;
  }

  protected isExpanded(typeId: number): boolean { return this.expandedTypeIds.has(typeId); }

}
