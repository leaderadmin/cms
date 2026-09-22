import { Component, EventEmitter, HostListener, Input, Output, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../modules/auth';
import { ToastService } from './toast.service';

export interface BackofficeNavItem {
  label: string;
  href: string;
  view?: string;
  active?: boolean;
  requiredPermissions?: string[];
  children?: BackofficeNavItem[];
  icon?: string;
}

export type BackofficeLanguage = 'en' | 'vi';
interface LayoutPreferences {
  sidebarMode: 'expanded' | 'compact' | 'mini';
  contentDensity: 'comfortable' | 'compact';
  contentWidth: 'contained' | 'wide';
  theme: 'light' | 'dim';
  cardStyle: 'elevated' | 'flat';
  accentColor: 'abbank' | 'coral' | 'indigo' | 'teal' | 'emerald';
  navbarType: 'fixed' | 'static' | 'floating';
  menuNavigation: 'vertical' | 'compact';
}

interface SystemBranding {
  system_name: string;
  logo_url: string;
  favicon_url: string;
  description: string;
  footer_text: string;
  version: string;
}

@Component({
  selector: 'app-backoffice-shell',
  imports: [FormsModule],
  templateUrl: './backoffice-shell.component.html',
  styleUrl: './backoffice-shell.component.css',
})
export class BackofficeShellComponent {
  protected readonly auth = inject(AuthService);
  protected readonly toast = inject(ToastService);
  private readonly http = inject(HttpClient);
  protected branding: SystemBranding = { system_name: 'Startup Backoffice', logo_url: '', favicon_url: '', description: 'Operations console', footer_text: 'operations console', version: '1.0.0' };
  protected sidebarOpen = true;
  protected expandedGroups = new Set<string>();
  protected language: BackofficeLanguage = (localStorage.getItem('backoffice-language') as BackofficeLanguage) || 'en';
  protected layout: LayoutPreferences = this.loadLayout();
  protected customizerOpen = false;
  protected searchQuery = '';

  constructor() {
    this.loadBranding();
  }

  private loadBranding(): void {
    this.http.get<SystemBranding>('/api/settings/system/').subscribe({
      next: (branding) => { this.branding = { ...this.branding, ...branding }; this.updateFavicon(branding.favicon_url); },
    });
  }

  private updateFavicon(url: string): void {
    if (!url) return;
    let favicon = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
    if (!favicon) { favicon = document.createElement('link'); favicon.rel = 'icon'; document.head.appendChild(favicon); }
    favicon.href = url;
  }

  @Input() navigation: BackofficeNavItem[] = [
    { label: 'Overview', href: '#overview', active: true },
    { label: 'Users', href: '#users', view: 'users' },
    { label: 'Activity logs', href: '#activity-logs' },
    { label: 'Sessions', href: '#sessions' },
  ];

  @Output() protected readonly signOut = new EventEmitter<void>();
  @Output() protected readonly navigate = new EventEmitter<string>();
  @Output() protected readonly languageChanged = new EventEmitter<BackofficeLanguage>();

  protected toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  protected toggleCustomizer(): void {
    this.customizerOpen = !this.customizerOpen;
  }

  protected updateLayout<K extends keyof LayoutPreferences>(key: K, value: LayoutPreferences[K]): void {
    this.layout = { ...this.layout, [key]: value };
    localStorage.setItem('backoffice-layout', JSON.stringify(this.layout));
    window.dispatchEvent(new CustomEvent('backoffice-layout-change', { detail: this.layout }));
  }

  protected hasChildren(item: BackofficeNavItem): boolean {
    return Boolean(item.children?.length);
  }

  protected isGroupExpanded(item: BackofficeNavItem): boolean {
    return item.active || this.expandedGroups.has(item.label);
  }

  protected toggleGroup(item: BackofficeNavItem): void {
    const expanded = new Set(this.expandedGroups);
    if (expanded.has(item.label)) expanded.delete(item.label);
    else expanded.add(item.label);
    this.expandedGroups = expanded;
  }

  protected selectNavigation(item: BackofficeNavItem): void {
    this.navigate.emit(item.view || 'overview');
  }

  protected runSearch(): void {
    const query = this.searchQuery.trim().toLowerCase();
    if (!query) return;
    const match = this.findNavigationItem(this.navigation, query);
    if (match) {
      this.selectNavigation(match);
      this.searchQuery = '';
    }
  }

  private findNavigationItem(items: BackofficeNavItem[], query: string): BackofficeNavItem | undefined {
    for (const item of items) {
      if (item.label.toLowerCase().includes(query) || item.view?.toLowerCase().includes(query)) return item;
      const childMatch = item.children ? this.findNavigationItem(item.children, query) : undefined;
      if (childMatch) return childMatch;
    }
    return undefined;
  }

  protected selectLanguage(language: BackofficeLanguage): void {
    this.language = language;
    localStorage.setItem('backoffice-language', language);
    window.dispatchEvent(new CustomEvent('backoffice-language-change', { detail: language }));
    this.languageChanged.emit(language);
  }

  @HostListener('window:backoffice-language-change', ['$event'])
  protected syncLanguage(event: Event): void {
    const language = (event as CustomEvent<BackofficeLanguage>).detail;
    if (language === 'en' || language === 'vi') this.language = language;
  }

  @HostListener('window:backoffice-layout-change', ['$event'])
  protected syncLayout(event: Event): void {
    this.layout = { ...this.layout, ...(event as CustomEvent<LayoutPreferences>).detail };
  }

  @HostListener('window:backoffice-system-settings-change', ['$event'])
  protected syncBranding(event: Event): void {
    const settings = (event as CustomEvent<Record<string, string>>).detail;
    this.branding = { ...this.branding, system_name: settings['organizationName'] || this.branding.system_name, logo_url: settings['logoUrl'] || '', favicon_url: settings['faviconUrl'] || '', description: settings['description'] || '', footer_text: settings['footerText'] || '', version: settings['version'] || '' };
    this.updateFavicon(this.branding.favicon_url);
  }

  private loadLayout(): LayoutPreferences {
    const defaults: LayoutPreferences = { sidebarMode: 'expanded', contentDensity: 'comfortable', contentWidth: 'contained', theme: 'light', cardStyle: 'elevated', accentColor: 'abbank', navbarType: 'fixed', menuNavigation: 'vertical' };
    try {
      const stored = JSON.parse(localStorage.getItem('backoffice-layout') || '{}');
      return { ...defaults, ...stored, theme: stored.theme === 'dark' ? 'light' : stored.theme || defaults.theme, accentColor: stored.accentColor === 'coral' ? 'abbank' : stored.accentColor || defaults.accentColor };
    } catch {
      return defaults;
    }
  }

  protected label(key: string): string {
    const labels: Record<string, { en: string; vi: string }> = {
      overview: { en: 'Overview', vi: 'Tổng quan' },
      dashboard: { en: 'Dashboard', vi: 'Bảng điều khiển' },
      account: { en: 'Account', vi: 'Tài khoản' },
      access: { en: 'Access management', vi: 'Quản lý truy cập' },
      monitoring: { en: 'Monitoring', vi: 'Giám sát' },
      settings: { en: 'Settings', vi: 'Cài đặt' },
      menuBuilder: { en: 'Menu builder', vi: 'Xây dựng menu' },
      profile: { en: 'Profile', vi: 'Hồ sơ' },
      users: { en: 'Users', vi: 'Người dùng' },
      roles: { en: 'Roles & Permissions', vi: 'Vai trò & quyền' },
      entities: { en: 'Entities', vi: 'Entity' },
      activity: { en: 'Activity logs', vi: 'Nhật ký hoạt động' },
      sessions: { en: 'Sessions', vi: 'Phiên đăng nhập' },
      signOut: { en: 'Sign out', vi: 'Đăng xuất' },
      language: { en: 'Language', vi: 'Ngôn ngữ' },
    };
    return labels[key]?.[this.language] || key;
  }

  protected navigationLabel(item: BackofficeNavItem): string {
    if (item.label === 'Overview') return this.label('dashboard');
    if (item.label === 'Account') return this.label('account');
    if (item.label === 'Access management') return this.label('access');
    if (item.label === 'Monitoring') return this.label('monitoring');
    if (item.label === 'Settings') return this.label('settings');
    if (item.label === 'Menu builder') return this.label('menuBuilder');
    if (item.label === 'Profile') return this.label('profile');
    if (item.label === 'Users') return this.label('users');
    if (item.label === 'Roles & Permissions') return this.label('roles');
    if (item.label === 'Entities') return this.label('entities');
    if (item.label === 'Activity logs') return this.label('activity');
    if (item.label === 'Sessions') return this.label('sessions');
    return item.label;
  }
}
