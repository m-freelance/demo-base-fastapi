import { computed, inject, Injectable, signal, Signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, shareReplay, tap, throwError } from 'rxjs';
import { ApiService } from './api-service';
import { UserInfo, UserRole } from '../types';

/**
 * Service for managing current user information.
 * Fetches and caches user data from the /users/me endpoint.
 */
@Injectable({
  providedIn: 'root',
})
export class UserInfoService {
  private readonly apiService = inject(ApiService);

  /**
   * The shared /users/me request. Held so the admin guard, the header and the
   * profile view cost one round trip between them instead of one each.
   */
  private request: Observable<UserInfo> | null = null;

  // Internal writable signals for state management
  private readonly _currentUser = signal<UserInfo | null>(null);
  private readonly _isLoading = signal<boolean>(false);
  private readonly _error = signal<HttpErrorResponse | null>(null);

  // Public readonly signals
  readonly currentUser: Signal<UserInfo | null> = this._currentUser.asReadonly();
  readonly isLoading: Signal<boolean> = this._isLoading.asReadonly();
  readonly error: Signal<HttpErrorResponse | null> = this._error.asReadonly();

  // Computed signals for common checks
  readonly isAuthenticated = computed(() => {
    const user = this._currentUser();
    return user !== null && user.is_active;
  });

  readonly isAdmin = computed(() => {
    const user = this._currentUser();
    return user !== null && user.role === UserRole.ADMIN;
  });

  /**
   * Fetches the current authenticated user, reusing the in-flight or completed
   * request if there is one. Guards can wait on the returned observable, while
   * components can keep reading the signals above.
   * @returns Observable of the current user
   */
  loadCurrentUser(): Observable<UserInfo> {
    if (this.request) {
      return this.request;
    }

    this._isLoading.set(true);
    this._error.set(null);

    this.request = this.apiService.get<UserInfo>('/users/me').pipe(
      tap((user) => {
        this._currentUser.set(user);
        this._isLoading.set(false);
      }),
      catchError((error: HttpErrorResponse) => {
        this._isLoading.set(false);
        this._error.set(error);
        // Forget the failure so the next navigation retries, rather than
        // replaying this error for the rest of the session.
        this.request = null;
        return throwError(() => error);
      }),
      // Everything above runs once however many callers subscribe.
      shareReplay({ bufferSize: 1, refCount: false }),
    );

    return this.request;
  }

  /**
   * Clears the cached user data.
   * Call this method on logout.
   */
  clearUser(): void {
    // The cached request goes too, otherwise whoever signs in next is served
    // the previous user's response.
    this.request = null;
    this._currentUser.set(null);
    this._isLoading.set(false);
    this._error.set(null);
  }
}
