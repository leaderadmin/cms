import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { AuthResponse, UserProfile } from './auth.models';

const ACCESS_TOKEN_KEY = 'backoffice_access_token';
const AUTH_RESPONSE_KEY = 'backoffice_auth_response';
const SAVED_USERNAME_KEY = 'backoffice_saved_username';
const SAVED_PASSWORD_KEY = 'backoffice_saved_password';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly authResponse = signal<AuthResponse | null>(this.readStoredAuth());

  readonly user = signal<UserProfile | null>(this.authResponse()?.user ?? null);

  login(username: string, password: string, rememberMe: boolean): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/login/', { username, password }).pipe(
      tap((response) => {
        this.setAuth(response, rememberMe);
        this.setSavedLogin(username, password, rememberMe);
      }),
    );
  }

  getSavedLogin(): { username: string; password: string } {
    return {
      username: localStorage.getItem(SAVED_USERNAME_KEY) || '',
      password: localStorage.getItem(SAVED_PASSWORD_KEY) || '',
    };
  }

  clearSavedLogin(): void {
    localStorage.removeItem(SAVED_USERNAME_KEY);
    localStorage.removeItem(SAVED_PASSWORD_KEY);
  }

  logout(): Observable<void> {
    return this.http.post<void>('/api/auth/logout/', {}).pipe(
      tap(() => this.clearAuth()),
    );
  }

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY) || sessionStorage.getItem(ACCESS_TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return Boolean(this.getAccessToken());
  }

  loadCurrentUser(): Observable<UserProfile> {
    return this.http.get<UserProfile>('/api/auth/me/').pipe(
      tap((profile) => this.user.set(profile)),
    );
  }

  clearAuth(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(AUTH_RESPONSE_KEY);
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(AUTH_RESPONSE_KEY);
    this.authResponse.set(null);
    this.user.set(null);
  }

  private setAuth(response: AuthResponse, rememberMe: boolean): void {
    this.clearStoredAuth();
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem(ACCESS_TOKEN_KEY, response.access);
    storage.setItem(AUTH_RESPONSE_KEY, JSON.stringify(response));
    this.authResponse.set(response);
    this.user.set(response.user);
  }

  private readStoredAuth(): AuthResponse | null {
    const stored = localStorage.getItem(AUTH_RESPONSE_KEY) || sessionStorage.getItem(AUTH_RESPONSE_KEY);
    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(stored) as AuthResponse;
    } catch {
      this.clearStoredAuth();
      return null;
    }
  }

  private clearStoredAuth(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(AUTH_RESPONSE_KEY);
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(AUTH_RESPONSE_KEY);
  }

  private setSavedLogin(username: string, password: string, rememberMe: boolean): void {
    if (rememberMe) {
      localStorage.setItem(SAVED_USERNAME_KEY, username);
      localStorage.setItem(SAVED_PASSWORD_KEY, password);
      return;
    }
    this.clearSavedLogin();
  }
}
