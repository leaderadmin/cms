import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth.service';
import { ToastService } from '../../shared/ui';

interface ProfileSettings {
  username: string;
  email: string;
  display_name: string;
  job_title: string;
  phone: string;
  location: string;
  bio: string;
  timezone: string;
  date_format: string;
  email_notifications: boolean;
  security_alerts: boolean;
  compact_mode: boolean;
  avatar_url: string;
}

@Component({
  selector: 'app-profile',
  imports: [FormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css',
})
export class ProfileComponent {
  protected readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly toast = inject(ToastService);
  protected profile: ProfileSettings = this.emptyProfile();
  protected activeTab: 'about' | 'permissions' = 'about';
  protected loading = true;
  protected saving = false;
  protected status = '';
  protected error = '';
  protected passwordForm = { current_password: '', new_password: '', confirm_password: '' };
  protected passwordSaving = false;
  protected passwordStatus = '';
  protected passwordError = '';
  protected avatarUploading = false;

  constructor() {
    this.http.get<ProfileSettings>('/api/auth/profile/').subscribe({
      next: (profile) => { this.profile = profile; this.loading = false; },
      error: () => { this.error = 'Unable to load profile settings.'; this.loading = false; },
    });
  }

  protected get user() {
    return this.auth.user();
  }

  protected get initials(): string {
    const username = this.user?.username || 'User';
    return username.slice(0, 2).toUpperCase();
  }

  protected get accountType(): string {
    return this.user?.is_staff ? 'Staff account' : 'Standard account';
  }

  protected saveProfile(): void {
    this.saving = true;
    this.status = '';
    this.error = '';
    this.http.patch<ProfileSettings>('/api/auth/profile/', this.profile).subscribe({
      next: (profile) => {
        this.profile = profile;
        this.saving = false;
        this.status = 'Profile settings saved.';
        this.toast.show('Profile saved successfully.');
        this.auth.loadCurrentUser().subscribe();
      },
      error: () => { this.saving = false; this.error = 'Unable to save profile settings.'; },
    });
  }

  protected uploadAvatar(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('avatar', file, file.name);
    this.avatarUploading = true;
    this.http.post<ProfileSettings>('/api/auth/profile/avatar/', form).subscribe({
      next: (profile) => {
        this.profile = profile;
        this.avatarUploading = false;
        this.auth.loadCurrentUser().subscribe();
        this.toast.show('Avatar uploaded successfully.');
      },
      error: (response) => {
        this.avatarUploading = false;
        this.error = response.error?.detail || 'Unable to upload avatar.';
      },
    });
    input.value = '';
  }

  protected selectTab(tab: 'about' | 'permissions'): void {
    this.activeTab = tab;
  }

  protected changePassword(): void {
    this.passwordSaving = true;
    this.passwordStatus = '';
    this.passwordError = '';
    this.http.post<{ detail: string; email_sent: boolean; email: string | null }>('/api/auth/password/change/', this.passwordForm).subscribe({
      next: (response) => {
        this.passwordForm = { current_password: '', new_password: '', confirm_password: '' };
        this.passwordSaving = false;
        this.passwordStatus = response.email_sent
          ? `Password changed for ${this.user?.username || 'your account'}. A security email was sent to ${response.email}.`
          : `Password changed for ${this.user?.username || 'your account'}, but the security email could not be sent.`;
        this.toast.show('Password changed successfully.');
      },
      error: (response) => {
        const detail = response.error;
        this.passwordError = detail?.current_password?.[0] || detail?.new_password?.[0] || detail?.confirm_password?.[0] || detail?.detail || 'Unable to change password.';
        this.passwordSaving = false;
      },
    });
  }

  private emptyProfile(): ProfileSettings {
    return { username: '', email: '', avatar_url: '', display_name: '', job_title: '', phone: '', location: '', bio: '', timezone: 'UTC', date_format: 'MMM d, yyyy', email_notifications: true, security_alerts: true, compact_mode: false };
  }
}
