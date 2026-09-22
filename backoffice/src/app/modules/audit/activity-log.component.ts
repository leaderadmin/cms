import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivityLog, ActivityLogFilters } from './audit.models';
import { AuditService } from './audit.service';

@Component({
  selector: 'app-activity-log',
  imports: [DatePipe, FormsModule],
  templateUrl: './activity-log.component.html',
  styleUrl: './activity-log.component.css',
})
export class ActivityLogComponent {
  private readonly auditApi = inject(AuditService);
  protected logs: ActivityLog[] = [];
  protected loading = true;
  protected error = '';
  protected expandedId: number | null = null;
  protected filters: ActivityLogFilters = { page: 1, limit: 20, action: '', path: '', status_code: '', level: '', username: '' };
  protected total = 0;
  protected totalPages = 1;
  protected readonly pageSizes = [10, 25, 50, 100];

  protected get pageItems(): (number | 'ellipsis')[] {
    if (this.totalPages <= 7) return Array.from({ length: this.totalPages }, (_, index) => index + 1);
    const items: (number | 'ellipsis')[] = [1];
    if (this.filters.page > 4) items.push('ellipsis');
    for (let page = Math.max(2, this.filters.page - 1); page <= Math.min(this.totalPages - 1, this.filters.page + 1); page += 1) items.push(page);
    if (this.filters.page < this.totalPages - 3) items.push('ellipsis');
    items.push(this.totalPages);
    return items;
  }

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading = true;
    this.error = '';
    this.auditApi.list(this.filters).subscribe({
      next: (response) => {
        this.logs = response.results;
        this.total = response.count;
        this.totalPages = response.total_pages;
        this.loading = false;
      },
      error: (response) => {
        this.error = response.status === 403 ? 'You do not have permission to view activity logs.' : 'Unable to load activity logs';
        this.loading = false;
      },
    });
  }

  protected applyFilters(): void {
    this.filters.page = 1;
    this.load();
  }

  protected clearFilters(): void {
    this.filters = { page: 1, limit: 20, action: '', path: '', status_code: '', level: '', username: '' };
    this.load();
  }

  protected goToPage(page: number): void {
    if (page < 1 || page > this.totalPages || page === this.filters.page) return;
    this.filters.page = page;
    this.load();
  }

  protected changePageSize(size: string): void {
    this.filters.limit = Number(size);
    this.filters.page = 1;
    this.load();
  }

  protected toggleDetails(log: ActivityLog): void {
    this.expandedId = this.expandedId === log.id ? null : log.id;
  }

  protected statusClass(status: number | null): string {
    if (!status) return 'text-bg-secondary';
    if (status >= 500) return 'text-bg-danger';
    if (status >= 400) return 'text-bg-warning';
    if (status >= 300) return 'text-bg-info';
    return 'text-bg-success';
  }

  protected levelClass(level: string): string {
    return level === 'ERROR' || level === 'CRITICAL' ? 'text-bg-danger' : level === 'WARNING' || level === 'WARN' ? 'text-bg-warning' : 'text-bg-secondary';
  }

  protected changedFields(log: ActivityLog): string {
    return log.changed_fields?.length ? JSON.stringify(log.changed_fields) : 'None';
  }
}
