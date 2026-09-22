import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { ArticleService } from './article.service';
import { ArticleTag } from './article.models';

@Component({
  selector: 'app-tag-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './tag-management.component.html',
  styleUrl: './tag-management.component.css',
})
export class TagManagementComponent {
  private readonly api = inject(ArticleService);
  private readonly toast = inject(ToastService);
  protected tags: ArticleTag[] = [];
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
      error: (response) => { this.error = response.error?.detail || 'Unable to load tags.'; this.loading = false; },
    });
  }

  protected edit(tag: ArticleTag): void { this.editingId = tag.id; this.name = tag.name; this.slug = tag.slug; }
  protected cancel(): void { this.editingId = null; this.name = ''; this.slug = ''; }

  protected save(): void {
    if (!this.name.trim()) return;
    this.saving = true;
    const request = this.editingId ? this.api.updateTag(this.editingId, { name: this.name.trim(), slug: this.slug.trim() }) : this.api.createTag({ name: this.name.trim(), slug: this.slug.trim() });
    request.subscribe({
      next: () => { this.toast.show(this.editingId ? 'Tag updated.' : 'Tag created.'); this.saving = false; this.cancel(); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save tag.'; this.saving = false; },
    });
  }

  protected remove(tag: ArticleTag): void {
    if (!window.confirm(`Delete "${tag.name}"?`)) return;
    this.api.deleteTag(tag.id).subscribe({ next: () => { this.toast.show('Tag deleted.'); this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to delete tag.'; } });
  }
}
