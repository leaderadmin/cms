import { HttpClient } from '@angular/common/http';
import { Component, HostListener, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { catchError, forkJoin, of } from 'rxjs';
import { AuthService, AuthSession, ProfileComponent } from './modules/auth';
import { BackofficeNavItem, BackofficePageComponent, BackofficeShellComponent } from './shared/ui';
import { RoleManagementComponent, UserCreateComponent, UserManagementComponent } from './modules/users';
import { MenuBuilderComponent, SettingsComponent } from './modules/settings';
import { MenuItem, MenuService } from './modules/settings';
import { ActivityLogComponent } from './modules/audit/activity-log.component';
import { EntityManagementComponent } from './modules/entities';
import { MediaManagerComponent } from './modules/media';
import { ArticleCreateComponent, ArticleEditComponent, ArticleManagementComponent, CategoryManagementComponent } from './modules/articles';
import { BlockManagementComponent, ComponentManagementComponent, PageBuilderComponent, PageCreateComponent, PageListComponent } from './modules/pages';
import { TagManagementComponent } from './modules/articles';

@Component({
  selector: 'app-root',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    BackofficePageComponent,
    BackofficeShellComponent,
    ProfileComponent,
    UserManagementComponent,
    UserCreateComponent,
    RoleManagementComponent,
    MenuBuilderComponent,
    SettingsComponent,
    ActivityLogComponent,
    EntityManagementComponent,
    MediaManagerComponent,
    ArticleManagementComponent,
    ArticleCreateComponent,
    ArticleEditComponent,
    CategoryManagementComponent,
    TagManagementComponent,
    PageBuilderComponent,
    PageCreateComponent,
    PageListComponent,
    BlockManagementComponent,
    ComponentManagementComponent,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private readonly http = inject(HttpClient);
  private readonly menuApi = inject(MenuService);
  protected readonly auth = inject(AuthService);

  protected loading = true;
  protected loggingIn = false;
  protected username = 'demo-admin';
  protected password = 'DemoAdmin123!';
  protected rememberMe = false;
  protected error = '';
  protected authMode: 'login' | 'forgot' | 'reset' = 'login';
  protected resetEmail = '';
  protected resetUsername = '';
  protected resetToken = '';
  protected resetPassword = '';
  protected resetConfirmPassword = '';
  protected authMessage = '';
  protected resetLoading = false;
  protected health: { status?: string; redis?: string } = {};
  protected stats: { visits?: number; last_cron_run?: { ran_at?: string } | null } = {};
  protected sessions: AuthSession[] = [];
  protected view = this.viewFromHash(window.location.hash);
  protected menuItems: MenuItem[] = [];

  protected get navigation(): BackofficeNavItem[] {
    const permissions = this.auth.user()?.permissions || [];
    if (this.menuItems.length) return this.buildMenuNavigation(this.menuItems, permissions);
    const canSee = (item: BackofficeNavItem): boolean => !item.requiredPermissions?.length || item.requiredPermissions.some((permission) => permissions.includes(permission));
    const items: BackofficeNavItem[] = [
      { label: 'Overview', href: '#overview', active: this.view === 'overview', requiredPermissions: ['dashboard.stats.read'] },
      {
        label: 'Account',
        href: '#account',
        active: this.view === 'profile',
        children: [
          { label: 'Profile', href: '#profile', view: 'profile', active: this.view === 'profile', requiredPermissions: ['auth.me.read'] },
        ],
      },
      {
        label: 'Access management',
        href: '#access-management',
        active: this.view === 'users' || this.view === 'roles',
        children: [
          { label: 'Users', href: '#users', view: 'users', active: this.view === 'users', requiredPermissions: ['auth.users.read', 'auth.users.create', 'auth.users.update', 'auth.users.assign_role'] },
          { label: 'Create user', href: '#user-create', view: 'user-create', active: this.view === 'user-create', requiredPermissions: ['auth.users.create'] },
          { label: 'Roles & Permissions', href: '#roles', view: 'roles', active: this.view === 'roles', requiredPermissions: ['auth.roles.read', 'auth.roles.create', 'auth.roles.update', 'auth.roles.delete'] },
        ],
      },
      {
        label: 'Monitoring',
        href: '#monitoring',
        active: this.view === 'activity' || this.view === 'sessions',
        children: [
          { label: 'Activity logs', href: '#activity-logs', view: 'activity', active: this.view === 'activity', requiredPermissions: ['audit.logs.read'] },
          { label: 'Sessions', href: '#sessions', view: 'sessions', active: this.view === 'sessions', requiredPermissions: ['auth.sessions.read', 'auth.sessions.revoke'] },
        ],
      },
      {
        label: 'Settings',
        href: '#settings',
        active: this.view === 'menu-builder' || this.view === 'settings' || this.view === 'mail-settings',
        children: [
          { label: 'General settings', href: '#settings', view: 'settings', active: this.view === 'settings', requiredPermissions: ['auth.menu.read'] },
          { label: 'Mail settings', href: '#mail-settings', view: 'mail-settings', active: this.view === 'mail-settings', requiredPermissions: ['auth.menu.read'] },
          { label: 'Menu builder', href: '#menu-builder', view: 'menu-builder', active: this.view === 'menu-builder', requiredPermissions: ['auth.menu.read', 'auth.menu.create', 'auth.menu.update', 'auth.menu.delete'] },
        ],
      },
      {
        label: 'Entities',
        href: '#entities',
        view: 'entities',
        active: this.view === 'entities',
        requiredPermissions: ['entity.read', 'entity.create', 'entity.update', 'entity.delete'],
      },
      {
        label: 'Build Page',
        href: '#build-page',
        active: this.view === 'pages' || this.view === 'blocks' || this.view === 'components',
        children: [
          { label: 'Pages', href: '#pages', view: 'pages', active: this.view === 'pages' || this.view.startsWith('pages/'), requiredPermissions: ['page.read'] },
          { label: 'Blocks', href: '#blocks', view: 'blocks', active: this.view === 'blocks', requiredPermissions: ['page.component.read'] },
          { label: 'Components', href: '#components', view: 'components', active: this.view === 'components', requiredPermissions: ['page.component.read'] },
        ],
      },
      {
        label: 'Nội dung',
        href: '#content',
        active: this.view === 'articles' || this.view === 'categories' || this.view === 'tags' || this.view === 'media',
        children: [
          { label: 'Articles', href: '#articles', view: 'articles', active: this.view === 'articles', requiredPermissions: ['article.read'] },
          { label: 'Categories', href: '#categories', view: 'categories', active: this.view === 'categories', requiredPermissions: ['article.category.read'] },
          { label: 'Tags', href: '#tags', view: 'tags', active: this.view === 'tags', requiredPermissions: ['article.tag.read'] },
          { label: 'Media', href: '#media', view: 'media', active: this.view === 'media', requiredPermissions: ['media.read'] },
        ],
      },
    ];
    return items
      .map((item) => ({ ...item, children: item.children?.filter(canSee) }))
      .filter((item) => canSee(item) && (!item.children || item.children.length > 0));
  }

  private buildMenuNavigation(items: MenuItem[], permissions: string[]): BackofficeNavItem[] {
    const visible = (item: MenuItem): boolean => !item.required_permission || permissions.includes(item.required_permission);
    const childrenOf = (parentId: number | null): BackofficeNavItem[] => {
      const seen = new Set<string>();
      return items
      .filter((item) => item.parent_id === parentId && visible(item))
      .sort((left, right) => left.sort_order - right.sort_order || left.id - right.id)
      .map((item) => {
        const children = childrenOf(item.id);
        const settingsChild = item.label === 'Settings' && permissions.includes('auth.menu.read') && !children.some((child) => child.view === 'settings')
          ? [{ label: 'General settings', href: '#settings', view: 'settings', icon: 'bi-sliders', active: this.view === 'settings', requiredPermissions: ['auth.menu.read'] }]
          : [];
        const allChildren = item.label === 'Settings' ? [...settingsChild, ...children] : children;
        return { label: item.label, href: item.href || `#${item.view}`, view: item.view || undefined, icon: item.icon, active: item.view === this.view || allChildren.some((child) => child.active), requiredPermissions: item.required_permission ? [item.required_permission] : undefined, children: allChildren.length ? allChildren : undefined };
      })
      .filter((item) => {
        if (item.view !== 'media') return true;
        if (seen.has('media')) return false;
        seen.add('media');
        return true;
      });
    };
    return childrenOf(null).filter((item) => item.view || item.children?.length);
  }

  constructor() {
    const savedLogin = this.auth.getSavedLogin();
    if (savedLogin.username || savedLogin.password) {
      this.username = savedLogin.username;
      this.password = savedLogin.password;
      this.rememberMe = true;
    }
    const token = new URLSearchParams(window.location.search).get('reset_token');
    if (token) {
      this.authMode = 'reset';
      this.resetToken = token;
    }
    if (this.auth.isAuthenticated()) {
      this.auth.loadCurrentUser().subscribe({
        next: () => this.refresh(),
        error: () => {
          this.auth.clearAuth();
          this.loading = false;
        },
      });
    } else {
      this.loading = false;
    }
  }

  protected requestPasswordReset(): void {
    this.resetLoading = true;
    this.error = '';
    this.authMessage = '';
    this.http.post<{ detail: string }>('/api/auth/password/reset/request/', { username: this.resetUsername, email: this.resetEmail }).subscribe({
      next: (response) => { this.authMessage = response.detail; this.resetLoading = false; },
      error: (response) => { this.error = response.error?.email?.[0] || response.error?.detail || 'Unable to send reset token.'; this.resetLoading = false; },
    });
  }

  protected confirmPasswordReset(): void {
    this.resetLoading = true;
    this.error = '';
    this.authMessage = '';
    this.http.post<{ detail: string; username: string; email: string }>('/api/auth/password/reset/confirm/', { token: this.resetToken, new_password: this.resetPassword, confirm_password: this.resetConfirmPassword }).subscribe({
      next: (response) => { this.authMessage = `${response.detail} Account: ${response.username} (${response.email}). Sign in with this account and your new password.`; this.username = response.username; this.resetUsername = response.username; this.resetEmail = response.email; this.authMode = 'login'; this.resetLoading = false; window.history.replaceState({}, '', window.location.pathname); },
      error: (response) => { this.error = response.error?.confirm_password?.[0] || response.error?.new_password?.[0] || response.error?.detail || 'Unable to reset password.'; this.resetLoading = false; },
    });
  }

  protected showLogin(): void { this.authMode = 'login'; this.error = ''; this.authMessage = ''; }
  protected showForgot(): void { this.authMode = 'forgot'; this.error = ''; this.authMessage = ''; }
  protected showReset(): void { this.authMode = 'reset'; this.error = ''; this.authMessage = ''; }
  protected rememberLoginChanged(): void {
    if (!this.rememberMe) {
      this.auth.clearSavedLogin();
    }
  }

  protected login(): void {
    this.loggingIn = true;
    this.error = '';
    this.auth.login(this.username, this.password, this.rememberMe).subscribe({
      next: () => {
        this.loggingIn = false;
        this.refresh();
      },
      error: (response) => {
        this.loggingIn = false;
        this.error = response.error?.detail || 'Unable to sign in with these credentials';
      },
    });
  }

  protected logout(): void {
    this.auth.logout().subscribe({
      next: () => this.resetDashboard(),
      error: () => this.resetDashboard(),
    });
  }

  protected refresh(): void {
    this.loading = true;
    this.error = '';

    forkJoin({
      health: this.http.get<{ status: string; redis: string }>('/api/health/'),
      stats: this.http.get<{ visits: number; last_cron_run: { ran_at?: string } | null }>('/api/stats/'),
      sessions: this.http.get<AuthSession[]>('/api/auth/sessions/'),
      menu: this.menuApi.list().pipe(catchError(() => of([] as MenuItem[]))),
    }).subscribe({
      next: (overview) => {
        this.health = overview.health;
        this.stats = overview.stats;
        this.sessions = overview.sessions;
        this.menuItems = overview.menu;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load Backoffice data';
        this.loading = false;
      }
    });
  }

  protected selectView(view: string): void {
    this.view = view;
    const hash = `#${view}`;
    if (window.location.hash !== hash) window.history.pushState({}, '', hash);
  }

  protected isArticleEditView(): boolean {
    return /^articles\/\d+\/edit$/.test(this.view);
  }

  protected isPageEditView(): boolean {
    return /^pages\/edit\/\d+$/.test(this.view);
  }

  protected pageIdFromView(): number | null {
    const match = this.view.match(/^pages\/edit\/(\d+)$/);
    return match ? Number(match[1]) : null;
  }

  @HostListener('window:hashchange')
  protected syncViewFromHash(): void {
    this.view = this.viewFromHash(window.location.hash);
  }

  private viewFromHash(hash: string): string {
    const view = hash.replace(/^#/, '');
    return view || 'overview';
  }

  private resetDashboard(): void {
    this.auth.clearAuth();
    this.sessions = [];
    this.health = {};
    this.stats = {};
    this.loading = false;
  }
}
