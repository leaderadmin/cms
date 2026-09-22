import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ManagedPermission, ManagedRole, ManagedUser } from './user.models';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);

  list(search = ''): Observable<ManagedUser[]> {
    const query = search.trim() ? `?q=${encodeURIComponent(search.trim())}` : '';
    return this.http.get<ManagedUser[]>(`/api/auth/users/${query}`);
  }

  roles(): Observable<ManagedRole[]> {
    return this.http.get<ManagedRole[]>('/api/auth/roles/');
  }

  permissions(): Observable<ManagedPermission[]> {
    return this.http.get<ManagedPermission[]>('/api/auth/permissions/');
  }

  createRole(name: string, permissions: string[]): Observable<ManagedRole> {
    return this.http.post<ManagedRole>('/api/auth/roles/', { name, permissions });
  }

  updateRole(roleId: number, name: string, permissions: string[]): Observable<ManagedRole> {
    return this.http.patch<ManagedRole>(`/api/auth/roles/${roleId}/`, { name, permissions });
  }

  deleteRole(roleId: number): Observable<void> {
    return this.http.delete<void>(`/api/auth/roles/${roleId}/`);
  }

  create(payload: { username: string; email: string; password: string; display_name: string; job_title: string; phone: string; location: string; bio: string }): Observable<ManagedUser> {
    return this.http.post<ManagedUser>('/api/auth/users/', payload);
  }

  update(userId: number, payload: { email?: string; is_active?: boolean; display_name?: string; job_title?: string; phone?: string; location?: string; bio?: string }): Observable<ManagedUser> {
    return this.http.patch<ManagedUser>(`/api/auth/users/${userId}/`, payload);
  }

  assignRoles(userId: number, roles: string[]): Observable<ManagedUser> {
    return this.http.post<ManagedUser>(`/api/auth/users/${userId}/roles/`, { roles });
  }
}
