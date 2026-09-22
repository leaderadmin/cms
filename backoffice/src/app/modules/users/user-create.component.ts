import { Component, EventEmitter, Output, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { UserService } from './user.service';

@Component({
  selector: 'app-user-create',
  imports: [FormsModule, BackofficePageComponent],
  template: `
    <app-backoffice-page
      eyebrow="ANGULAR / BACKOFFICE / ACCESS"
      title="Create user"
      description="Create an account and configure its contact information before granting access."
      [error]="error">
      <div page-actions><button class="btn btn-outline-secondary" type="button" (click)="cancel.emit()"><i class="bi bi-arrow-left me-2"></i>Back to users</button></div>
      <form class="card card-outline card-primary create-user-card" #userForm="ngForm" (ngSubmit)="create()" novalidate>
        <div class="card-header"><h3 class="card-title"><i class="bi bi-person-plus me-2"></i>Account information</h3></div>
        <div class="card-body row g-3">
          <div class="col-md-6"><label class="form-label" for="new-username">Username <span class="required-mark">*</span></label><input id="new-username" class="form-control" name="username" [(ngModel)]="form.username" required minlength="3" maxlength="150" #username="ngModel" autocomplete="username"><div class="invalid-feedback" [class.d-block]="username.invalid && username.touched">Username must be at least 3 characters.</div></div>
          <div class="col-md-6"><label class="form-label" for="new-email">Email <span class="required-mark">*</span></label><input id="new-email" class="form-control" name="email" type="email" [(ngModel)]="form.email" required email #email="ngModel" autocomplete="email"><div class="invalid-feedback" [class.d-block]="email.invalid && email.touched">Enter a valid email address.</div></div>
          <div class="col-md-6"><label class="form-label" for="new-password">Temporary password <span class="required-mark">*</span></label><input id="new-password" class="form-control" name="password" type="password" minlength="8" [(ngModel)]="form.password" required #password="ngModel" autocomplete="new-password"><div class="invalid-feedback" [class.d-block]="password.invalid && password.touched">Password must be at least 8 characters and pass the password policy.</div></div>
          <div class="col-md-6"><label class="form-label" for="new-display-name">Display name</label><input id="new-display-name" class="form-control" name="display_name" [(ngModel)]="form.display_name" maxlength="160" autocomplete="name"></div>
          <div class="col-md-6"><label class="form-label" for="new-phone">Phone</label><input id="new-phone" class="form-control" name="phone" type="tel" [(ngModel)]="form.phone" maxlength="40" autocomplete="tel"></div>
          <div class="col-md-6"><label class="form-label" for="new-job-title">Job title</label><input id="new-job-title" class="form-control" name="job_title" [(ngModel)]="form.job_title" maxlength="160"></div>
          <div class="col-12"><label class="form-label" for="new-location">Location</label><input id="new-location" class="form-control" name="location" [(ngModel)]="form.location" maxlength="160" autocomplete="address-level2"></div>
          <div class="col-12"><label class="form-label" for="new-bio">Bio</label><textarea id="new-bio" class="form-control" name="bio" rows="4" maxlength="1000" [(ngModel)]="form.bio"></textarea><small class="form-text">{{ form.bio.length }}/1000 characters</small></div>
        </div>
        <div class="card-footer d-flex justify-content-end gap-2"><button class="btn btn-outline-secondary" type="button" (click)="cancel.emit()">Cancel</button><button class="btn btn-primary" type="submit" [disabled]="saving || userForm.invalid">{{ saving ? 'Creating...' : 'Create user' }}</button></div>
      </form>
    </app-backoffice-page>
  `,
  styles: [`
    :host { display: block; }
    .create-user-card { max-width: 960px; border-top-width: 3px; }
    .required-mark { color: #dc3545; }
    .invalid-feedback { font-size: 12px; }
    .form-text { color: var(--bs-secondary-color); }
  `],
})
export class UserCreateComponent {
  private readonly usersApi = inject(UserService);
  private readonly toast = inject(ToastService);
  @Output() protected readonly completed = new EventEmitter<void>();
  @Output() protected readonly cancel = new EventEmitter<void>();

  protected saving = false;
  protected error = '';
  protected form = { username: '', email: '', password: '', display_name: '', job_title: '', phone: '', location: '', bio: '' };

  protected create(): void {
    this.saving = true;
    this.error = '';
    this.usersApi.create(this.form).subscribe({
      next: () => { this.saving = false; this.toast.show('User created successfully.'); this.completed.emit(); },
      error: (response) => { this.error = response.error?.password?.[0] || response.error?.username?.[0] || response.error?.email?.[0] || response.error?.detail || 'Unable to create user.'; this.saving = false; },
    });
  }
}
