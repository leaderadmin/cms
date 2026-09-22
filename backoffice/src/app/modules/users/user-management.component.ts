import { Component, EventEmitter, Output, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { AuthService } from '../auth';
import { UserService } from './user.service';
import { ManagedRole, ManagedUser } from './user.models';
import { of, switchMap } from 'rxjs';

@Component({
  selector: 'app-user-management',
  imports: [DatePipe, FormsModule, BackofficePageComponent],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css',
})
export class UserManagementComponent {
  private readonly usersApi = inject(UserService);
  private readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);

  protected users: ManagedUser[] = [];
  protected roles: ManagedRole[] = [];
  protected search = '';
  protected loading = true;
  protected saving = false;
  protected error = '';
  @Output() protected readonly createRequested = new EventEmitter<void>();
  protected editingUserId: number | null = null;
  protected editForm = { email: '', display_name: '', job_title: '', phone: '', location: '', bio: '', role: '' };
  protected page = 1;
  protected pageSize = 10;

  protected get totalPages(): number { return Math.max(Math.ceil(this.users.length / this.pageSize), 1); }
  protected get pagedUsers(): ManagedUser[] { return this.users.slice((this.page - 1) * this.pageSize, this.page * this.pageSize); }
  protected get pageItems(): (number | 'ellipsis')[] {
    if (this.totalPages <= 7) return Array.from({ length: this.totalPages }, (_, index) => index + 1);
    const items: (number | 'ellipsis')[] = [1];
    if (this.page > 4) items.push('ellipsis');
    for (let page = Math.max(2, this.page - 1); page <= Math.min(this.totalPages - 1, this.page + 1); page += 1) items.push(page);
    if (this.page < this.totalPages - 3) items.push('ellipsis');
    items.push(this.totalPages);
    return items;
  }

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading = true;
    this.error = '';
    this.usersApi.list(this.search).subscribe({
      next: (users) => { this.users = users; this.loading = false; },
      error: () => { this.error = 'Unable to load users'; this.loading = false; },
    });
    this.usersApi.roles().subscribe({ next: (roles) => { this.roles = roles; } });
  }

  protected goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) this.page = page;
  }

  protected changePageSize(size: string): void {
    this.pageSize = Number(size);
    this.page = 1;
  }

  protected startEdit(user: ManagedUser): void {
    this.editingUserId = user.id;
    this.editForm = { email: user.email || '', display_name: user.display_name || '', job_title: user.job_title || '', phone: user.phone || '', location: user.location || '', bio: user.bio || '', role: this.roleFor(user) };
    this.error = '';
  }

  protected cancelEdit(): void { this.editingUserId = null; }

  protected saveEdit(user: ManagedUser): void {
    this.saving = true;
    this.error = '';
    const { role, ...profile } = this.editForm;
    this.usersApi.update(user.id, profile).pipe(
      switchMap((updated) => this.can('auth.users.assign_role') ? this.usersApi.assignRoles(user.id, role ? [role] : []) : of(updated)),
    ).subscribe({
      next: (updated) => { this.replace(updated); this.editingUserId = null; this.saving = false; this.toast.show('User saved successfully.'); },
      error: (response) => { this.error = response.error?.detail || 'Unable to update user'; this.saving = false; },
    });
  }

  protected toggleActive(user: ManagedUser): void {
    this.usersApi.update(user.id, { is_active: !user.is_active }).subscribe({
      next: (updated) => { this.replace(updated); this.toast.show('User status saved successfully.'); },
      error: () => { this.error = 'Unable to update user status'; },
    });
  }

  protected changeRole(user: ManagedUser, role: string): void {
    this.usersApi.assignRoles(user.id, role ? [role] : []).subscribe({
      next: (updated) => { this.replace(updated); this.toast.show('User role saved successfully.'); },
      error: () => { this.error = 'Unable to update user role'; },
    });
  }

  protected roleFor(user: ManagedUser): string {
    return user.roles[0] || '';
  }

  protected can(permission: string): boolean {
    return this.auth.user()?.permissions.includes(permission) || false;
  }

  private replace(updated: ManagedUser): void {
    this.users = this.users.map((user) => user.id === updated.id ? updated : user);
  }
}
