import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Menu, MenuItem, MenuItemPayload, MenuPayload, RoutePermission } from './menu.models';

@Injectable({ providedIn: 'root' })
export class MenuService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/auth/menu/';
  private readonly menusEndpoint = '/api/auth/menus/';
  private readonly permissionsEndpoint = '/api/auth/permissions/';

  listPermissions(): Observable<RoutePermission[]> {
    return this.http.get<RoutePermission[]>(this.permissionsEndpoint);
  }

  listMenus(): Observable<Menu[]> {
    return this.http.get<Menu[]>(this.menusEndpoint);
  }

  createMenu(payload: MenuPayload): Observable<Menu> {
    return this.http.post<Menu>(this.menusEndpoint, payload);
  }

  updateMenu(id: number, payload: Partial<MenuPayload>): Observable<Menu> {
    return this.http.patch<Menu>(`${this.menusEndpoint}${id}/`, payload);
  }

  deleteMenu(id: number): Observable<void> {
    return this.http.delete<void>(`${this.menusEndpoint}${id}/`);
  }

  list(menuId?: number): Observable<MenuItem[]> {
    return this.http.get<MenuItem[]>(this.endpoint, menuId ? { params: { menu_id: menuId } } : {});
  }

  create(payload: MenuItemPayload): Observable<MenuItem> {
    return this.http.post<MenuItem>(this.endpoint, payload);
  }

  update(id: number, payload: Partial<MenuItemPayload>): Observable<MenuItem> {
    return this.http.patch<MenuItem>(`${this.endpoint}${id}/`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.endpoint}${id}/`);
  }
}
