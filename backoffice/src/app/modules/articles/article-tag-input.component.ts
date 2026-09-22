import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ArticleTag } from './article.models';

@Component({
  selector: 'app-article-tag-input',
  imports: [FormsModule],
  templateUrl: './article-tag-input.component.html',
  styleUrl: './article-tag-input.component.css',
})
export class ArticleTagInputComponent {
  @Input() tags: string[] = [];
  @Input() availableTags: ArticleTag[] = [];
  @Input() tagIds: number[] = [];
  @Output() readonly tagsChange = new EventEmitter<string[]>();
  @Output() readonly tagIdsChange = new EventEmitter<number[]>();
  protected draft = '';

  protected add(event?: Event): void {
    event?.preventDefault();
    const value = this.draft.trim();
    if (!value || this.tags.includes(value)) return;
    this.tagsChange.emit([...this.tags, value]);
    this.draft = '';
  }

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

  protected onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' || event.key === ',') this.add(event);
  }
}
