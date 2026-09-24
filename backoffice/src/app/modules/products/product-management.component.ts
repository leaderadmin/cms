import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { Product, ProductInput } from './product.models';
import { ProductService } from './product.service';

@Component({
  selector: 'app-product-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './product-management.component.html',
  styleUrl: './product-management.component.css',
})
export class ProductManagementComponent {
  private readonly productsApi = inject(ProductService);
  private readonly toast = inject(ToastService);
  protected products: Product[] = [];
  protected metadata: any = { groups: [], types: [], categories: [], attributes: [], attribute_sets: [] };
  protected query = '';
  protected kind = '';
  protected status = '';
  protected page = 1;
  protected total = 0;
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editing: Product | null = null;

  constructor() { this.loadMetadata(); }

  protected loadMetadata(): void {
    this.productsApi.metadata().subscribe({ next: (metadata) => { this.metadata = metadata; this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to load product metadata.'; this.loading = false; } });
  }

  protected load(page = 1): void {
    this.page = Math.max(1, page);
    this.loading = true;
    this.productsApi.list(this.query.trim(), this.kind, this.status, this.page, 25).subscribe({ next: (response) => { this.products = response.results; this.total = response.count; this.loading = false; this.error = ''; }, error: (response) => { this.error = response.error?.detail || 'Unable to load products.'; this.loading = false; } });
  }

  protected get totalPages(): number { return Math.max(1, Math.ceil(this.total / 25)); }
  protected startCreate(): void { window.location.hash = 'products/new'; }
  protected startProductSets(): void { window.location.hash = 'product-sets'; }
  protected startEdit(product: Product): void {
    window.location.hash = `products/${product.id}/edit`;
  }
  protected publish(product: Product): void { this.productsApi.publish(product.id).subscribe({ next: () => { this.toast.show('Product published.'); this.load(this.page); }, error: (response) => { this.error = response.error?.detail || 'Unable to publish product.'; } }); }
  protected archive(product: Product): void { if (!window.confirm(`Archive "${product.translation?.title || product.name}"?`)) return; this.productsApi.archive(product.id).subscribe({ next: () => { this.toast.show('Product archived.'); this.load(this.page); }, error: (response) => { this.error = response.error?.detail || 'Unable to archive product.'; } }); }
}
