import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ArticleCategory } from './article.models';

@Component({
  selector: 'app-article-category-select',
  imports: [FormsModule],
  templateUrl: './article-category-select.component.html',
  styleUrl: './article-category-select.component.css',
})
export class ArticleCategorySelectComponent {
  @Input() categories: ArticleCategory[] = [];
  @Input() selectedIds: number[] = [];
  @Output() readonly selectedIdsChange = new EventEmitter<number[]>();
  protected search = '';
  protected open = false;

  protected get filteredCategories(): ArticleCategory[] {
    const query = this.search.trim().toLowerCase();
    return this.categories.filter((category) => !query || `${category.title} ${category.name}`.toLowerCase().includes(query));
  }

  protected get selectedCategories(): ArticleCategory[] {
    return this.categories.filter((category) => category.id === this.selectedIds[0]);
  }

  protected toggle(category: ArticleCategory): void {
    this.selectedIdsChange.emit([category.id]);
    this.open = false;
  }

  protected remove(category: ArticleCategory): void {
    this.selectedIdsChange.emit([]);
  }

  protected toggleOpen(event?: Event): void {
    event?.stopPropagation();
    this.open = !this.open;
  }

  @HostListener('document:click')
  protected close(): void { this.open = false; }
}
