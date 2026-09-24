import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { ToastService } from '../../shared/ui';
import { Menu, MenuItem, MenuItemPayload, MenuPayload, RoutePermission } from './menu.models';
import { MenuService } from './menu.service';

@Component({
  selector: 'app-menu-builder',
  imports: [FormsModule],
  templateUrl: './menu-builder.component.html',
  styleUrl: './menu-builder.component.css',
})
export class MenuBuilderComponent {
  private readonly menuApi = inject(MenuService);
  private readonly toast = inject(ToastService);
  protected items: MenuItem[] = [];
  protected menus: Menu[] = [];
  protected selectedMenuId: number | null = null;
  protected menuForm: MenuPayload = this.emptyMenuForm();
  protected editingMenuId: number | null = null;
  protected menuEditorOpen = false;
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected draggedItem: MenuItem | null = null;
  protected dragOverId: number | null = null;
  protected previewParentId: number | null | undefined;
  protected rootDropIndex: number | null = null;
  protected form: MenuItemPayload = this.emptyForm();
  protected editingId: number | null = null;
  protected itemEditorOpen = false;
  protected permissions: RoutePermission[] = [];
  protected permissionSearch = '';
  protected permissionDropdownOpen = false;

  constructor() {
    this.loadMenus();
    this.menuApi.listPermissions().subscribe({
      next: (permissions) => { this.permissions = permissions; },
      error: () => { this.error = 'Unable to load permissions'; },
    });
  }

  protected get roots(): MenuItem[] {
    return this.items.filter((item) => !item.parent_id).sort(this.sortItems);
  }

  protected childrenOf(parentId: number): MenuItem[] {
    return this.items.filter((item) => item.parent_id === parentId).sort(this.sortItems);
  }

  protected load(): void {
    if (!this.selectedMenuId) return;
    this.loading = true;
    this.menuApi.list(this.selectedMenuId).subscribe({
      next: (items) => { this.items = items; this.loading = false; },
      error: () => { this.error = 'Unable to load menu items'; this.loading = false; },
    });
  }

  protected loadMenus(): void {
    this.menuApi.listMenus().subscribe({
      next: (menus) => { this.menus = menus; this.selectedMenuId = this.selectedMenuId && menus.some((menu) => menu.id === this.selectedMenuId) ? this.selectedMenuId : menus[0]?.id ?? null; this.load(); },
      error: () => { this.error = 'Unable to load menus'; this.loading = false; },
    });
  }

  protected selectMenu(menuId: number): void { this.selectedMenuId = menuId; this.cancelEdit(); this.editingMenuId = null; this.menuEditorOpen = false; this.menuForm = this.emptyMenuForm(); this.load(); }

  protected editMenu(menu: Menu): void { this.editingMenuId = menu.id; this.menuEditorOpen = true; this.menuForm = { ...menu }; }

  protected cancelMenuEdit(): void { this.editingMenuId = null; this.menuEditorOpen = true; this.menuForm = this.emptyMenuForm(); }

  protected closeMenuEdit(): void { this.menuEditorOpen = false; }

  protected saveMenu(): void {
    if (!this.menuForm.name.trim() || !this.menuForm.slug.trim()) return;
    const request = this.editingMenuId ? this.menuApi.updateMenu(this.editingMenuId, this.menuForm) : this.menuApi.createMenu(this.menuForm);
    request.subscribe({ next: (menu) => { this.menuEditorOpen = false; this.editingMenuId = null; this.toast.show('Menu saved successfully.'); this.selectedMenuId = menu.id; this.loadMenus(); }, error: () => { this.error = 'Unable to save menu'; } });
  }

  protected removeMenu(menu: Menu): void {
    if (!window.confirm(`Delete menu "${menu.name}" and all its items?`)) return;
    this.menuApi.deleteMenu(menu.id).subscribe({ next: () => { this.toast.show('Menu deleted successfully.'); this.selectedMenuId = null; this.loadMenus(); }, error: () => { this.error = 'Unable to delete menu'; } });
  }

  protected openCreateItem(): void {
    this.editingId = null;
    this.form = this.emptyForm();
    this.permissionSearch = '';
    this.permissionDropdownOpen = false;
    this.itemEditorOpen = true;
  }

  protected edit(item: MenuItem): void {
    this.editingId = item.id;
    this.form = { ...item };
    this.permissionSearch = '';
    this.permissionDropdownOpen = false;
    this.itemEditorOpen = true;
  }

  protected cancelEdit(): void {
    this.editingId = null;
    this.form = this.emptyForm();
    this.itemEditorOpen = false;
    this.permissionSearch = '';
    this.permissionDropdownOpen = false;
  }

  protected get filteredPermissions(): RoutePermission[] {
    const query = this.permissionSearch.trim().toLowerCase();
    if (!query) return this.permissions;
    return this.permissions.filter((permission) => `${this.permissionLabel(permission)} ${permission.code} ${permission.module} ${permission.route}`.toLowerCase().includes(query));
  }

  protected permissionLabel(permission: RoutePermission): string {
    const actions: Record<string, string> = { read: 'Xem', create: 'Tạo', update: 'Cập nhật', delete: 'Xóa', publish: 'Xuất bản', upload: 'Tải lên', revoke: 'Thu hồi', assign_role: 'Gán vai trò', stats: 'Xem thống kê' };
    const resources: Record<string, string> = { 'auth.me': 'hồ sơ cá nhân', 'auth.users': 'người dùng', 'auth.roles': 'vai trò', 'auth.permissions': 'quyền truy cập', 'auth.sessions': 'phiên đăng nhập', 'auth.menu': 'menu', dashboard: 'bảng điều khiển', 'audit.logs': 'nhật ký hoạt động', entity: 'đơn vị', article: 'bài viết', 'article.category': 'danh mục bài viết', 'article.tag': 'thẻ bài viết', media: 'thư viện media', page: 'trang', 'page.component': 'component trang', 'page.form': 'form động', product: 'sản phẩm', 'product.metadata': 'thuộc tính sản phẩm', 'product.tag': 'thẻ sản phẩm', recruitment: 'tuyển dụng', 'recruitment.department': 'phòng ban tuyển dụng', faq: 'FAQ', dealer: 'đại lý' };
    const parts = permission.code.split('.');
    return `${actions[parts.at(-1) || ''] || 'Quản lý'} ${resources[parts.slice(0, -1).join('.')] || parts.slice(0, -1).join(' ')}`;
  }

  protected selectPermission(permission: RoutePermission): void {
    this.form.required_permission = permission.code;
    this.form.href = this.permissionHref(permission);
    this.permissionSearch = this.permissionLabel(permission);
    this.permissionDropdownOpen = false;
  }

  protected permissionHref(permission: RoutePermission): string {
    const routes: Record<string, string> = { 'dashboard.stats': '#overview', 'auth.me': '#profile', 'auth.users': '#users', 'auth.roles': '#roles', 'auth.permissions': '#roles', 'auth.sessions': '#sessions', 'auth.menu': '#menu-builder', 'audit.logs': '#activity', entity: '#entities', article: '#articles', 'article.category': '#categories', 'article.tag': '#tags', media: '#media', page: '#pages', 'page.component': '#components', 'page.form': '#forms', product: '#products', 'product.metadata': '#products', 'product.tag': '#product-tags', recruitment: '#recruitment', 'recruitment.department': '#recruitment-departments', faq: '#faq', dealer: '#dealers' };
    return routes[permission.code.split('.').slice(0, -1).join('.')] || '';
  }

  protected save(): void {
    if (!this.form.label.trim()) return;
    this.saving = true;
    const request = this.editingId
      ? this.menuApi.update(this.editingId, this.form)
      : this.menuApi.create(this.form);
    request.subscribe({
      next: () => { this.cancelEdit(); this.saving = false; this.toast.show('Menu item saved successfully.'); this.load(); },
      error: () => { this.error = 'Unable to save menu item'; this.saving = false; },
    });
  }

  protected remove(item: MenuItem): void {
    if (!window.confirm(`Delete "${item.label}" and its child menu items?`)) return;
    this.menuApi.delete(item.id).subscribe({
      next: () => { this.toast.show('Menu item deleted successfully.'); this.load(); },
      error: () => { this.error = 'Unable to delete menu item'; },
    });
  }

  protected startDrag(item: MenuItem, event: DragEvent): void {
    this.draggedItem = item;
    this.dragOverId = null;
    this.previewParentId = undefined;
    this.rootDropIndex = null;
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', String(item.id));
    }
  }

  protected endDrag(): void {
    this.draggedItem = null;
    this.dragOverId = null;
    this.previewParentId = undefined;
    this.rootDropIndex = null;
  }

  protected itemById = (item: MenuItem): boolean => item.id === this.previewParentId;

  protected allowDrop(event: DragEvent, item?: MenuItem): void {
    event.preventDefault();
    if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
    this.dragOverId = item?.id ?? null;
    this.rootDropIndex = null;
    if (this.draggedItem && item?.parent_id === null && item.id !== this.draggedItem.id && this.draggedItem.parent_id !== item.id) this.previewParentId = item.id;
    else if (!item && this.draggedItem?.parent_id !== null) this.previewParentId = null;
    else this.previewParentId = undefined;
  }

  protected allowRootPosition(event: DragEvent, index: number): void {
    event.preventDefault();
    event.stopPropagation();
    if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
    this.rootDropIndex = index;
    this.dragOverId = null;
    this.previewParentId = null;
  }

  protected dropOn(event: DragEvent, item: MenuItem): void {
    event.preventDefault();
    event.stopPropagation();
    this.dragOverId = null;
    this.previewParentId = undefined;
    this.rootDropIndex = null;
    if (!this.draggedItem || item.parent_id !== null || this.draggedItem.id === item.id || this.draggedItem.parent_id === item.id || this.isDescendant(item.id, this.draggedItem.id)) return;
    this.move(this.draggedItem, item.id);
  }

  protected dropOnRoot(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.dragOverId = null;
    this.previewParentId = undefined;
    this.rootDropIndex = null;
    if (!this.draggedItem || !this.draggedItem.parent_id) return;
    this.move(this.draggedItem, null);
  }

  protected dropOnRootAt(event: DragEvent, index: number): void {
    event.preventDefault();
    event.stopPropagation();
    const item = this.draggedItem;
    if (!item) return;
    const roots = this.roots.filter((root) => root.id !== item.id);
    const originalIndex = this.roots.findIndex((root) => root.id === item.id);
    const adjustedIndex = Math.max(0, Math.min(roots.length, index - (originalIndex >= 0 && originalIndex < index ? 1 : 0)));
    roots.splice(adjustedIndex, 0, { ...item, parent_id: null });
    this.persistRootOrder(roots);
  }

  protected move(item: MenuItem, parentId: number | null): void {
    this.menuApi.update(item.id, { parent_id: parentId, sort_order: this.nextOrder(parentId) }).subscribe({
      next: () => { this.endDrag(); this.toast.show('Menu order saved successfully.'); this.load(); },
      error: () => { this.error = 'Unable to move menu item'; this.endDrag(); this.load(); },
    });
  }

  private persistRootOrder(roots: MenuItem[]): void {
    this.saving = true;
    forkJoin(roots.map((root, sort_order) => this.menuApi.update(root.id, { parent_id: null, sort_order }))).subscribe({
      next: () => { this.saving = false; this.endDrag(); this.toast.show('Menu order saved successfully.'); this.load(); },
      error: () => { this.saving = false; this.error = 'Unable to save menu order'; this.endDrag(); this.load(); },
    });
  }

  protected iconClass(icon: string): string {
    return icon.startsWith('bi-') ? `bi ${icon}` : `bi bi-${icon}`;
  }

  private isDescendant(candidateId: number, ancestorId: number): boolean {
    return this.items.some((item) => item.id === candidateId && item.parent_id === ancestorId)
      || this.items.filter((item) => item.parent_id === ancestorId).some((child) => this.isDescendant(candidateId, child.id));
  }

  private nextOrder(parentId: number | null): number {
    const siblings = this.items.filter((item) => item.parent_id === parentId);
    return siblings.length ? Math.max(...siblings.map((item) => item.sort_order)) + 1 : 0;
  }

  private sortItems(left: MenuItem, right: MenuItem): number {
    return left.sort_order - right.sort_order || left.id - right.id;
  }

  private emptyForm(): MenuItemPayload {
    return { menu_id: this.selectedMenuId ?? 0, label: '', href: '', view: '', icon: 'bi-circle', required_permission: '', parent_id: null, sort_order: 0, is_active: true };
  }

  private emptyMenuForm(): MenuPayload { return { name: '', slug: '', is_active: true }; }

  protected get selectedMenu(): Menu | undefined { return this.menus.find((menu) => menu.id === this.selectedMenuId); }
}
