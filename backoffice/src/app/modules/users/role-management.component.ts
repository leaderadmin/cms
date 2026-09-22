import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { AuthService } from '../auth';
import { UserService } from './user.service';
import { ManagedPermission, ManagedRole } from './user.models';

@Component({
  selector: 'app-role-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './role-management.component.html',
  styleUrl: './role-management.component.css',
})
export class RoleManagementComponent {
  private readonly usersApi = inject(UserService);
  private readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);

  protected roles: ManagedRole[] = [];
  protected permissions: ManagedPermission[] = [];
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected showForm = false;
  protected form = { id: 0, name: '' };
  protected selectedPermissions: string[] = [];
  protected expandedModules = new Set<string>();
  protected page = 1;
  protected pageSize = 10;

  protected get totalPages(): number { return Math.max(Math.ceil(this.roles.length / this.pageSize), 1); }
  protected get pagedRoles(): ManagedRole[] { return this.roles.slice((this.page - 1) * this.pageSize, this.page * this.pageSize); }
  protected get pageItems(): (number | 'ellipsis')[] {
    if (this.totalPages <= 7) return Array.from({ length: this.totalPages }, (_, index) => index + 1);
    const items: (number | 'ellipsis')[] = [1];
    if (this.page > 4) items.push('ellipsis');
    for (let page = Math.max(2, this.page - 1); page <= Math.min(this.totalPages - 1, this.page + 1); page += 1) items.push(page);
    if (this.page < this.totalPages - 3) items.push('ellipsis');
    items.push(this.totalPages);
    return items;
  }

  protected goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) this.page = page;
  }

  protected changePageSize(size: string): void {
    this.pageSize = Number(size);
    this.page = 1;
  }

  protected get permissionGroups(): { module: string; resources: { name: string; permissions: ManagedPermission[] }[] }[] {
    const groups = new Map<string, Map<string, ManagedPermission[]>>();
    for (const permission of this.permissions) {
      const parts = permission.code.split('.');
      const resource = parts.length >= 3 ? parts[1] : permission.module === 'entity' ? 'entities' : `${permission.module}s`;
      const resources = groups.get(permission.module) || new Map<string, ManagedPermission[]>();
      const resourcePermissions = resources.get(resource) || [];
      resourcePermissions.push(permission);
      resources.set(resource, resourcePermissions);
      groups.set(permission.module, resources);
    }
    return [...groups.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([module, resources]) => ({
        module,
        resources: [...resources.entries()]
          .sort(([left], [right]) => left.localeCompare(right))
          .map(([name, permissions]) => ({
            name,
            permissions: permissions.sort((left, right) => left.code.localeCompare(right.code)),
          })),
      }));
  }

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading = true;
    this.error = '';
    this.usersApi.roles().subscribe({
      next: (roles) => { this.roles = roles; this.loading = false; },
      error: () => { this.error = 'Unable to load roles'; this.loading = false; },
    });
    this.usersApi.permissions().subscribe({
      next: (permissions) => {
        this.permissions = permissions;
        this.expandedModules = new Set(this.permissionGroups.map((group) => group.module));
      },
      error: () => { this.error = 'Unable to load permissions'; },
    });
  }

  protected isModuleExpanded(module: string): boolean {
    return this.expandedModules.has(module);
  }

  protected toggleModule(module: string): void {
    const expanded = new Set(this.expandedModules);
    if (expanded.has(module)) expanded.delete(module);
    else expanded.add(module);
    this.expandedModules = expanded;
  }

  protected editRole(role?: ManagedRole): void {
    this.showForm = true;
    this.form = { id: role?.id || 0, name: role?.name || '' };
    this.selectedPermissions = role ? [...role.permissions] : [];
  }

  protected closeForm(): void {
    this.showForm = false;
    this.form = { id: 0, name: '' };
    this.selectedPermissions = [];
  }

  protected permissionSelected(code: string): boolean {
    return this.selectedPermissions.includes(code);
  }

  protected permissionAction(code: string): string {
    const parts = code.split('.');
    return parts.length >= 3 ? parts.slice(2).join('.') : parts.at(-1) || code;
  }

  protected selectedCount(codes: string[]): number {
    return codes.filter((code) => this.permissionSelected(code)).length;
  }

  protected resourcePermissionCodes(resource: { permissions: ManagedPermission[] }): string[] {
    return resource.permissions.map((permission) => permission.code);
  }

  protected modulePermissionCodes(group: { resources: { permissions: ManagedPermission[] }[] }): string[] {
    return group.resources.flatMap((resource) => this.resourcePermissionCodes(resource));
  }

  protected togglePermissions(codes: string[], checked: boolean): void {
    const selected = new Set(this.selectedPermissions);
    for (const code of codes) {
      if (checked) selected.add(code);
      else selected.delete(code);
    }
    this.selectedPermissions = [...selected];
  }

  protected can(permission: string): boolean {
    return this.auth.user()?.permissions.includes(permission) || false;
  }

  protected togglePermission(code: string, checked: boolean): void {
    this.selectedPermissions = checked
      ? [...new Set([...this.selectedPermissions, code])]
      : this.selectedPermissions.filter((permission) => permission !== code);
  }

  protected saveRole(): void {
    this.saving = true;
    this.error = '';
    const request = this.form.id
      ? this.usersApi.updateRole(this.form.id, this.form.name, this.selectedPermissions)
      : this.usersApi.createRole(this.form.name, this.selectedPermissions);
    request.subscribe({
      next: (role) => {
        this.roles = [...this.roles.filter((item) => item.id !== role.id), role]
          .sort((left, right) => left.name.localeCompare(right.name));
        this.closeForm();
        this.saving = false;
        this.toast.show('Role saved successfully.');
      },
      error: (response) => { this.error = response.error?.detail || 'Unable to save role'; this.saving = false; },
    });
  }

  protected removeRole(role: ManagedRole): void {
    if (!window.confirm(`Delete role ${role.name}?`)) return;
    this.usersApi.deleteRole(role.id).subscribe({
      next: () => { this.roles = this.roles.filter((item) => item.id !== role.id); this.toast.show('Role deleted successfully.'); },
      error: () => { this.error = 'Unable to delete role'; },
    });
  }
}
