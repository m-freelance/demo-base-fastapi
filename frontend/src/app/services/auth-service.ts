import { Injectable, inject, computed } from '@angular/core';
import { HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { ApiService } from './api-service';
import { LocalStorageService, StorageSignal } from './local-storage-service';
import { UserInfoService } from './user-info-service';
import { LoginResponse, RegisterRequest, RegisterResponse } from '../types';

const TOKEN_KEY = 'auth_token';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly API_AUTH_ENDPOINT = '/auth';

  private readonly apiService = inject(ApiService);
  private readonly localStorageService = inject(LocalStorageService);
  private readonly userInfoService = inject(UserInfoService);
  private readonly router = inject(Router);

  /** Reactive localStorage connection for the auth token */
  private readonly tokenStorage: StorageSignal<string | null>;

  /** Read-only signal for authentication state */
  readonly isAuthenticated = computed(() => !!this.tokenStorage.value());

  constructor() {
    // Create reactive localStorage connection for the token
    this.tokenStorage = this.localStorageService.connectString(TOKEN_KEY, null);
  }

  /**
   * Login user with email and password
   * @param email - User's email address
   * @param password - User's password
   * @returns Observable of LoginResponse
   */
  login(email: string, password: string): Observable<LoginResponse> {
    // Backend expects form data for OAuth2 login
    const formData = new URLSearchParams();
    formData.set('username', email);
    formData.set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.apiService
      .post<LoginResponse>(`${this.API_AUTH_ENDPOINT}/login`, formData.toString(), { headers })
      .pipe(
        tap((response) => {
          this.tokenStorage.set(response.access_token);
        }),
        catchError((error) => {
          this.tokenStorage.remove();
          return throwError(() => error);
        }),
      );
  }

  /**
   * Register a new user
   * @param email - User's email address
   * @param password - User's password
   * @returns Observable of RegisterResponse
   */
  register(email: string, password: string): Observable<RegisterResponse> {
    const request: RegisterRequest = { email, password };

    return this.apiService.post<RegisterResponse>(`${this.API_AUTH_ENDPOINT}/register`, request);
  }

  /**
   * Logout user and clear authentication state
   */
  logout(): void {
    this.tokenStorage.remove();
    // Without this the next user to sign in briefly sees the previous user's
    // email in the header, and their admin nav link if that user was an admin.
    this.userInfoService.clearUser();
    this.redirectToLogin();
  }

  /**
   * Redirect to login page if not authenticated
   */
  redirectToLogin(): void {
    this.router.navigate(['/login']);
  }

  /**
   * Get authorization header for authenticated requests
   */
  getAuthorizationHeader(): string | null {
    const token = this.tokenStorage.value();
    return token ? `Bearer ${token}` : null;
  }
}
