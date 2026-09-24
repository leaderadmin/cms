import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { Product, ProductInput, ProductTag } from './product.models';
import { ProductService } from './product.service';
import { ProductTagInputComponent } from './product-tag-input.component';

@Component({
  selector: 'app-product-edit',
  imports: [FormsModule, BackofficePageComponent, RichEditorComponent, ProductTagInputComponent],
  templateUrl: './product-edit.component.html',
  styleUrl: './product-edit.component.css',
})
export class ProductEditComponent {
  private readonly productsApi = inject(ProductService);
  private readonly toast = inject(ToastService);
  protected metadata: any = { groups: [], types: [], categories: [], attributes: [], attribute_sets: [], product_tags: [] as ProductTag[] };
  protected form: ProductInput = this.emptyForm();
  protected editing: Product | null = null;
  protected title = 'New product';
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected activeLanguage: 'en' | 'vi' = 'en';

  constructor() {
    this.productsApi.metadata().subscribe({
      next: (metadata) => {
        this.metadata = metadata;
        const match = window.location.hash.match(/^#products\/(\d+)\/edit$/);
        if (match) this.loadProduct(Number(match[1]));
        else {
          const group = new URLSearchParams(window.location.hash.split('?')[1] || '').get('group');
          if (group && this.metadata.groups.some((item: any) => item.slug === group)) this.form.kind = group;
          this.loading = false;
        }
      },
      error: (response) => { this.error = response.error?.detail || 'Unable to load product metadata.'; this.loading = false; },
    });
  }

  protected categoryOptions(): any[] {
    return this.metadata.categories.filter((category: any) => !this.form.product_type_id || !category.product_type_id || category.product_type_id === this.form.product_type_id);
  }

  protected switchLanguage(language: 'en' | 'vi'): void {
    this.activeLanguage = language;
  }

  protected attributeDefinitions(): Array<{ id: number; name: string; slug: string; value_type: string }> {
    const selectedSet = this.metadata.attribute_sets.find((item: any) => Number(item.id) === Number(this.form.attribute_set_id));
    if (!selectedSet) return [];
    const attributeIds = Array.isArray(selectedSet.attribute_ids) ? selectedSet.attribute_ids.map((id: unknown) => Number(id)) : [];
    return attributeIds
      .map((id: number) => this.metadata.attributes.find((item: any) => Number(item.id) === id))
      .filter(Boolean);
  }

  protected attributeValue(slug: string): unknown {
    return this.form.attributes[slug] ?? '';
  }

  protected setAttributeValue(slug: string, value: unknown): void {
    this.form.attributes = { ...this.form.attributes, [slug]: value };
  }

  protected setAttributeSet(value: number | string | null): void {
    this.form.attribute_set_id = value === null || value === undefined || value === '' ? null : Number(value);
  }

  protected presentationValue(key: string, fallback: string | boolean): string | boolean {
    const presentation = (this.form.extra_data?.['presentation'] || {}) as Record<string, unknown>;
    return presentation[key] === undefined ? fallback : presentation[key] as string | boolean;
  }

  protected setPresentationValue(key: string, value: string | boolean): void {
    const presentation = (this.form.extra_data?.['presentation'] || {}) as Record<string, unknown>;
    this.form.extra_data = { ...this.form.extra_data, presentation: { ...presentation, [key]: value } };
  }

  protected save(): void {
    if (!this.form.name.trim() || !this.form.translation.title.trim() || !this.form.translations[1].title.trim()) {
      this.error = 'Product name, Vietnamese title and English title are required.';
      return;
    }
    this.form.translation = this.activeLanguage === 'en' ? this.form.translations[1] : this.form.translations[0];
    this.form.tags = this.form.tags.map((tag) => tag.trim()).filter((tag, index, tags) => tag && tags.indexOf(tag) === index);
    this.saving = true;
    this.error = '';
    const request = this.editing ? this.productsApi.update(this.editing.id, this.form) : this.productsApi.create(this.form);
    request.subscribe({
      next: () => { this.toast.show(this.editing ? 'Product updated.' : 'Product created.'); this.goToList(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save product.'; this.saving = false; },
    });
  }

  protected goToList(): void { window.location.hash = 'products'; }

  private loadProduct(id: number): void {
    this.productsApi.get(id).subscribe({
      next: (product) => {
        this.editing = product;
        this.title = product.translation?.title || product.name;
        const translations = product.translations || [];
        const vietnamese = translations.find((item) => item.language_code === 'vi') || product.translation || this.emptyTranslation(product.name, product.slug);
        const english = translations.find((item) => item.language_code === 'en') || this.emptyTranslation(product.name, product.slug);
        this.form = {
          name: product.name,
          slug: product.slug,
          kind: product.kind,
          status: product.status,
          ordering: product.ordering,
          is_featured: product.is_featured,
          tags: product.tags || [],
          tag_ids: product.tag_ids || [],
          product_type_id: product.product_type?.id || null,
          category_id: product.category?.id || null,
          attribute_set_id: product.attribute_set?.id || null,
          attributes: product.attributes || {},
          extra_data: product.extra_data || {},
          translation: { ...vietnamese, language_code: 'vi' },
          translations: [{ ...vietnamese, language_code: 'vi' }, { ...english, language_code: 'en' }],
        };
        this.loading = false;
      },
      error: (response) => { this.error = response.error?.detail || 'Unable to load product.'; this.loading = false; },
    });
  }

  private emptyTranslation(title = '', slug = '', language_code = 'vi'): any { return { language_code, title, short_description: '', content: '', url_key: slug, seo_title: '', meta_keyword: '', meta_description: '' }; }
  private emptyForm(): ProductInput { const vietnamese = this.emptyTranslation(); const english = this.emptyTranslation('', '', 'en'); return { name: '', slug: '', kind: 'service', status: 0, ordering: 0, is_featured: false, tags: [], tag_ids: [], product_type_id: null, category_id: null, attribute_set_id: null, attributes: {}, extra_data: {}, translation: vietnamese, translations: [vietnamese, english] }; }
}
