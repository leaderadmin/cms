import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, HostListener, Input, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { switchMap } from 'rxjs';
import { ToastService } from '../../shared/ui';

interface SettingsForm {
  organizationName: string;
  apiDomain: string;
  backofficeDomain: string;
  logoUrl: string;
  faviconUrl: string;
  description: string;
  websiteUrl: string;
  supportEmail: string;
  version: string;
  footerText: string;
  timezone: string;
  dateFormat: string;
  language: string;
  sessionTimeout: number;
  requireMfa: boolean;
  loginAlerts: boolean;
  emailDigest: boolean;
  compactTables: boolean;
  sidebarMode: 'expanded' | 'compact';
  contentDensity: 'comfortable' | 'compact';
  contentWidth: 'contained' | 'wide';
  theme: 'light' | 'dim';
  cardStyle: 'elevated' | 'flat';
}

interface MailConfig {
  enabled: boolean;
  provider: string;
  host: string;
  port: number;
  username: string;
  password: string;
  fromName: string;
  fromEmail: string;
  encryption: string;
  testRecipient: string;
}

interface MailTemplate {
  id: number;
  name: string;
  key: string;
  subject: string;
  body: string;
  enabled: boolean;
  updatedAt: string;
}

@Component({
  selector: 'app-settings',
  imports: [FormsModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css',
})
export class SettingsComponent {
  private readonly http = inject(HttpClient);
  private readonly toast = inject(ToastService);
  @Input() initialSection = 'general';
  protected activeSection = 'general';
  protected saved = false;
  protected form: SettingsForm = this.loadSettings();
  protected mailConfig: MailConfig = this.loadMailConfig();
  protected templates: MailTemplate[] = this.loadTemplates();
  protected selectedTemplateId: number | null = null;
  protected templateDraft: MailTemplate = this.emptyTemplate();
  protected templateEditing = false;
  protected testSending = false;
  protected testStatus = '';
  protected testError = '';
  protected systemLoading = true;
  protected logoUploading = false;

  ngOnInit(): void {
    this.activeSection = this.initialSection;
    this.http.get<Record<string, string>>('/api/settings/system/').subscribe({
      next: (settings) => {
        this.form = { ...this.form, organizationName: settings['system_name'] || this.form.organizationName, apiDomain: settings['api_domain'] || '', backofficeDomain: settings['backoffice_domain'] || '', logoUrl: settings['logo_url'] || '', faviconUrl: settings['favicon_url'] || '', description: settings['description'] || '', websiteUrl: settings['website_url'] || '', supportEmail: settings['support_email'] || '', version: settings['version'] || this.form.version, footerText: settings['footer_text'] || this.form.footerText };
        this.systemLoading = false;
      },
      error: () => { this.systemLoading = false; },
    });
  }

  protected readonly sections = [
    { id: 'general', label: 'General', description: 'Workspace identity and defaults', icon: 'bi-sliders' },
    { id: 'localization', label: 'Localization', description: 'Language, timezone and formats', icon: 'bi-translate' },
    { id: 'security', label: 'Security', description: 'Sessions and sign-in protection', icon: 'bi-shield-check' },
    { id: 'notifications', label: 'Notifications', description: 'Alerts and email preferences', icon: 'bi-bell' },
    { id: 'mail', label: 'Mail', description: 'SMTP, test delivery and templates', icon: 'bi-envelope-paper' },
    { id: 'appearance', label: 'Appearance', description: 'Tables and workspace density', icon: 'bi-palette' },
  ];

  protected selectSection(section: string): void {
    this.activeSection = section;
    this.saved = false;
  }

  protected selectTemplate(template: MailTemplate): void {
    this.selectedTemplateId = template.id;
    this.templateDraft = { ...template };
    this.templateEditing = true;
  }

  protected newTemplate(): void {
    this.selectedTemplateId = null;
    this.templateDraft = this.emptyTemplate();
    this.templateEditing = true;
  }

  protected saveTemplate(): void {
    if (!this.templateDraft.name.trim() || !this.templateDraft.key.trim()) return;
    const template = { ...this.templateDraft, updatedAt: new Date().toISOString() };
    const savedTemplate = this.selectedTemplateId ? template : { ...template, id: Date.now() };
    this.templates = this.selectedTemplateId
      ? this.templates.map((item) => item.id === this.selectedTemplateId ? savedTemplate : item)
      : [...this.templates, savedTemplate];
    localStorage.setItem('backoffice-mail-templates', JSON.stringify(this.templates));
    this.selectedTemplateId = savedTemplate.id;
    this.templateDraft = { ...savedTemplate };
    this.templateEditing = true;
    this.saved = true;
    this.toast.show('Email template saved successfully.');
  }

  protected deleteTemplate(template: MailTemplate): void {
    if (!window.confirm(`Delete template "${template.name}"?`)) return;
    this.templates = this.templates.filter((item) => item.id !== template.id);
    localStorage.setItem('backoffice-mail-templates', JSON.stringify(this.templates));
    if (this.selectedTemplateId === template.id) {
      this.selectedTemplateId = null;
      this.templateEditing = false;
    }
    this.toast.show('Email template deleted successfully.');
  }

  protected sendTestEmail(): void {
    this.testStatus = '';
    this.testError = '';
    if (!this.mailConfig.testRecipient || !this.mailConfig.testRecipient.includes('@')) {
      this.testError = 'Enter a valid test recipient email.';
      return;
    }
    if (!this.mailConfig.host || !this.mailConfig.fromEmail) {
      this.testError = 'Configure SMTP host and sender email before testing.';
      return;
    }
    this.testSending = true;
    this.http.put('/api/settings/email/', {
      provider: this.mailConfig.provider,
      host: this.mailConfig.host,
      port: this.mailConfig.port,
      username: this.mailConfig.username,
      password: this.mailConfig.password,
      encryption: this.mailConfig.encryption,
      from_name: this.mailConfig.fromName,
      from_email: this.mailConfig.fromEmail,
      enabled: this.mailConfig.enabled,
    }).pipe(
      switchMap(() => this.http.post<{ detail: string }>('/api/settings/email/test/', { recipient: this.mailConfig.testRecipient })),
    ).subscribe({
      next: (response) => {
        this.testSending = false;
        this.testStatus = response.detail || `Test email sent to ${this.mailConfig.testRecipient}.`;
        this.toast.show('Test email sent successfully.');
      },
      error: (error: HttpErrorResponse) => {
        this.testSending = false;
        this.testError = this.emailError(error);
      },
    });
  }

  private emailError(error: HttpErrorResponse): string {
    const detail = error.error?.detail;
    if (detail) return detail;
    if (error.status === 0) return 'Unable to reach the mail API.';
    return 'Unable to send the test email. Check the SMTP settings and try again.';
  }

  protected save(): void {
    this.http.put('/api/settings/system/', {
      system_name: this.form.organizationName,
      api_domain: this.form.apiDomain,
      backoffice_domain: this.form.backofficeDomain,
      logo_url: this.form.logoUrl,
      favicon_url: this.form.faviconUrl,
      description: this.form.description,
      website_url: this.form.websiteUrl,
      support_email: this.form.supportEmail,
      version: this.form.version,
      footer_text: this.form.footerText,
    }).subscribe({
      next: () => window.dispatchEvent(new CustomEvent('backoffice-system-settings-change', { detail: this.form })),
      error: () => this.toast.show('System metadata could not be saved.', 'danger'),
    });
    localStorage.setItem('backoffice-settings', JSON.stringify(this.form));
    localStorage.setItem('backoffice-mail-config', JSON.stringify(this.mailConfig));
    this.publishLanguage(this.form.language);
    this.publishLayout();
    this.saved = true;
    this.toast.show('Settings saved successfully.');
    window.setTimeout(() => this.saved = false, 2600);
  }

  protected uploadLogo(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('logo', file, file.name);
    this.logoUploading = true;
    this.http.post<Record<string, string>>('/api/settings/system/logo/', form).subscribe({
      next: (settings) => {
        this.form.logoUrl = settings['logo_url'] || '/api/settings/system/logo/';
        window.dispatchEvent(new CustomEvent('backoffice-system-settings-change', { detail: this.form }));
        this.logoUploading = false;
        this.toast.show('Logo uploaded successfully.');
      },
      error: (error: HttpErrorResponse) => {
        this.logoUploading = false;
        this.toast.show(error.error?.detail || 'Logo upload failed.', 'danger');
      },
    });
    input.value = '';
  }

  protected languageChanged(language: string): void {
    this.form.language = language;
    this.publishLanguage(language);
  }

  protected reset(): void {
    this.form = this.defaultSettings();
    this.save();
  }

  protected layoutChanged(): void {
    this.publishLayout();
  }

  private loadMailConfig(): MailConfig {
    try {
      const stored = localStorage.getItem('backoffice-mail-config');
      return stored ? { ...this.defaultMailConfig(), ...JSON.parse(stored) } : this.defaultMailConfig();
    } catch {
      return this.defaultMailConfig();
    }
  }

  private loadTemplates(): MailTemplate[] {
    try {
      const stored = localStorage.getItem('backoffice-mail-templates');
      return stored ? JSON.parse(stored) : [
        { id: 1, name: 'Welcome email', key: 'auth.welcome', subject: 'Welcome to {{ organizationName }}', body: 'Hello {{ username }},\n\nWelcome to {{ organizationName }}. Your account is ready.', enabled: true, updatedAt: new Date().toISOString() },
        { id: 2, name: 'Password reset', key: 'auth.password_reset', subject: 'Reset your password', body: 'Hello {{ username }},\n\nUse the link below to reset your password:\n{{ resetUrl }}', enabled: true, updatedAt: new Date().toISOString() },
      ];
    } catch {
      return [];
    }
  }

  private defaultMailConfig(): MailConfig {
    return { enabled: true, provider: 'smtp', host: '', port: 587, username: '', password: '', fromName: 'Startup Backoffice', fromEmail: '', encryption: 'tls', testRecipient: '' };
  }

  private emptyTemplate(): MailTemplate {
    return { id: 0, name: '', key: '', subject: '', body: '', enabled: true, updatedAt: '' };
  }

  @HostListener('window:backoffice-language-change', ['$event'])
  protected syncLanguage(event: Event): void {
    const language = (event as CustomEvent<string>).detail;
    if (language === 'en' || language === 'vi') this.form.language = language;
  }

  private publishLanguage(language: string): void {
    if (language !== 'en' && language !== 'vi') return;
    localStorage.setItem('backoffice-language', language);
    window.dispatchEvent(new CustomEvent('backoffice-language-change', { detail: language }));
  }

  private publishLayout(): void {
    const { sidebarMode, contentDensity, contentWidth, theme, cardStyle } = this.form;
    const layout = { sidebarMode, contentDensity, contentWidth, theme, cardStyle };
    localStorage.setItem('backoffice-layout', JSON.stringify(layout));
    window.dispatchEvent(new CustomEvent('backoffice-layout-change', { detail: layout }));
  }

  private loadSettings(): SettingsForm {
    try {
      const stored = localStorage.getItem('backoffice-settings');
      const settings = stored ? { ...this.defaultSettings(), ...JSON.parse(stored) } : this.defaultSettings();
      const navbarLanguage = localStorage.getItem('backoffice-language');
      if (navbarLanguage === 'en' || navbarLanguage === 'vi') settings.language = navbarLanguage;
      return settings;
    } catch {
      return this.defaultSettings();
    }
  }

  private defaultSettings(): SettingsForm {
    return {
      organizationName: 'Startup Backoffice',
      apiDomain: '',
      backofficeDomain: '',
      logoUrl: '',
      faviconUrl: '',
      description: 'Operations console',
      websiteUrl: '',
      supportEmail: '',
      version: '1.0.0',
      footerText: 'operations console',
      timezone: 'Asia/Ho_Chi_Minh',
      dateFormat: 'dd/MM/yyyy',
      language: 'en',
      sessionTimeout: 60,
      requireMfa: false,
      loginAlerts: true,
      emailDigest: false,
      compactTables: false,
      sidebarMode: 'expanded',
      contentDensity: 'comfortable',
      contentWidth: 'contained',
      theme: 'light',
      cardStyle: 'elevated',
    };
  }
}
