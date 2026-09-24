import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { ProductService } from './product.service';

@Component({
  selector: 'app-product-type-create',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './product-type-create.component.html',
  styleUrl: './product-type-create.component.css',
})
export class ProductTypeCreateComponent {
  private readonly productsApi = inject(ProductService);
  private readonly toast = inject(ToastService);
  protected name = '';
  protected slug = '';
  protected saving = false;
  protected error = '';

  protected save(): void {
    if (!this.name.trim()) {
      this.error = 'Product set name is required.';
      return;
    }
    this.saving = true;
    this.error = '';
    this.productsApi.createMetadata('type', this.name.trim(), this.slug.trim()).subscribe({
      next: () => { this.toast.show('Product set created.'); this.goToList(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to create product set.'; this.saving = false; },
    });
  }

  protected goToList(): void { window.location.hash = 'product-sets'; }
}
