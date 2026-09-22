import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { PageService } from './page.service';
import { Page } from './page.models';

@Component({
  selector: 'app-page-list',
  imports: [DatePipe, FormsModule, BackofficePageComponent],
  templateUrl: './page-list.component.html',
  styleUrl: './page-list.component.css',
})
export class PageListComponent {
  private readonly pagesApi = inject(PageService);
  private readonly toast = inject(ToastService);
  protected pages: Page[] = [];
  protected loading = true;
  protected error = '';
  protected search = '';
  protected statusFilter: Page['status'] | 'all' = 'all';

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.pagesApi.list().subscribe({
      next: (pages) => { this.pages = pages; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load pages.'; this.loading = false; },
    });
  }

  protected create(): void { window.location.hash = '#pages/new'; }
  protected edit(page: Page): void { window.location.hash = `#pages/edit/${page.id}`; }
  protected statusLabel(status: Page['status']): string { return status === 'published' ? 'Published' : status === 'archived' ? 'Archived' : 'Draft'; }
  protected get filteredPages(): Page[] {
    const query = this.search.trim().toLowerCase();
    return this.pages.filter((page) => {
      const matchesSearch = !query || page.name.toLowerCase().includes(query) || page.slug.toLowerCase().includes(query) || page.template_key.toLowerCase().includes(query);
      const matchesStatus = this.statusFilter === 'all' || page.status === this.statusFilter;
      return matchesSearch && matchesStatus;
    });
  }

  protected archive(page: Page): void {
    if (!window.confirm(`Archive page "${page.name}"?`)) return;
    this.pagesApi.archive(page.id).subscribe({
      next: () => { this.toast.show('Page archived.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to archive page.'; },
    });
  }
}
