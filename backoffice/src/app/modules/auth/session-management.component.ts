import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { AuthSession } from './auth.models';

@Component({
  selector: 'app-session-management',
  imports: [DatePipe, BackofficePageComponent],
  templateUrl: './session-management.component.html',
  styleUrl: './session-management.component.css',
})
export class SessionManagementComponent {
  private readonly http = inject(HttpClient);
  private readonly toast = inject(ToastService);
  protected sessions: AuthSession[] = [];
  protected loading = true;
  protected revoking = '';
  protected error = '';

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.error = '';
    this.http.get<AuthSession[]>('/api/auth/sessions/').subscribe({
      next: (sessions) => { this.sessions = sessions; this.loading = false; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load sessions.'; this.loading = false; },
    });
  }

  protected revoke(session: AuthSession): void {
    if (!session.active || this.revoking) return;
    this.revoking = session.session_id;
    this.http.post<void>(`/api/auth/sessions/${session.session_id}/revoke/`, {}).subscribe({
      next: () => { this.toast.show('Session revoked.'); this.revoking = ''; this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to revoke session.'; this.revoking = ''; },
    });
  }
}
