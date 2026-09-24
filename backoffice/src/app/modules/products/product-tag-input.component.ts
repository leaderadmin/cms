import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ProductTag } from './product.models';

@Component({
  selector: 'app-product-tag-input',
  imports: [],
  templateUrl: './product-tag-input.component.html',
  styleUrl: './product-tag-input.component.css',
})
export class ProductTagInputComponent {
  @Input() tags: string[] = [];
  @Input() availableTags: ProductTag[] = [];
  @Input() tagIds: number[] = [];
  @Output() readonly tagsChange = new EventEmitter<string[]>();
  @Output() readonly tagIdsChange = new EventEmitter<number[]>();

  protected remove(tag: string): void {
    this.tagsChange.emit(this.tags.filter((item) => item !== tag));
    const selected = this.availableTags.find((item) => item.name === tag);
    if (selected) this.tagIdsChange.emit(this.tagIds.filter((id) => id !== selected.id));
  }

  protected selectTag(event: Event): void {
    const id = Number((event.target as HTMLSelectElement).value);
    const tag = this.availableTags.find((item) => item.id === id);
    if (!tag || this.tagIds.includes(id)) return;
    this.tagIdsChange.emit([...this.tagIds, id]);
    this.tagsChange.emit([...this.tags, tag.name]);
    (event.target as HTMLSelectElement).value = '';
  }

}
