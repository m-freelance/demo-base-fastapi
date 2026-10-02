import { effect, EffectRef, inject, Injectable, Injector, Signal, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { SignalizerService, ApiSignals } from './signalizer-service';
import { UserInfo } from '../types';

/**
 * Paginated response structure from the backend (fastapi-pagination)
 */
export interface PaginatedUsersResponse {
  items: UserInfo[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Service for admin user management operations.
 * Provides functionality to fetch and manage all users.
 */
@Injectable({
  providedIn: 'root',
})
export class UserManagementService {
  private readonly signalizerService = inject(SignalizerService);
  private readonly injector = inject(Injector);

  /** Effect mirroring the latest page request into the signals below. */
  private syncEffect: EffectRef | null = null;

  // Internal writable signals for state management
  private readonly _users = signal<UserInfo[]>([]);
  private readonly _totalUsers = signal<number>(0);
  private readonly _currentPage = signal<number>(1);
  private readonly _pageSize = signal<number>(10);
  private readonly _totalPages = signal<number>(0);
  private readonly _isLoading = signal<boolean>(false);
  private readonly _error = signal<HttpErrorResponse | null>(null);

  // Public readonly signals
  readonly users: Signal<UserInfo[]> = this._users.asReadonly();
  readonly totalUsers: Signal<number> = this._totalUsers.asReadonly();
  readonly currentPage: Signal<number> = this._currentPage.asReadonly();
  readonly pageSize: Signal<number> = this._pageSize.asReadonly();
  readonly totalPages: Signal<number> = this._totalPages.asReadonly();
  readonly isLoading: Signal<boolean> = this._isLoading.asReadonly();
  readonly error: Signal<HttpErrorResponse | null> = this._error.asReadonly();

  /**
   * Fetches all users from the API with pagination support.
   * @param page - The page number to fetch (1-based)
   * @param size - The number of items per page
   * @returns ApiSignals containing isLoading, data, and error signals
   */
  fetchAllUsers(page: number = 1, size: number = 10): ApiSignals<PaginatedUsersResponse> {
    this._isLoading.set(true);
    this._error.set(null);

    const signals = this.signalizerService.get<PaginatedUsersResponse>(
      `/users?page=${page}&size=${size}`,
    );

    // Mirror the request signals rather than polling them on a timer, so a
    // page lands as soon as it arrives. Only the newest request keeps its
    // mirror, otherwise a slow earlier page could overwrite a faster later one.
    this.syncEffect?.destroy();
    this.syncEffect = effect(
      () => {
        const data = signals.data();
        const error = signals.error();

        this._isLoading.set(signals.isLoading());

        if (data) {
          this._users.set(data.items);
          this._totalUsers.set(data.total);
          this._currentPage.set(data.page);
          this._pageSize.set(data.size);
          this._totalPages.set(data.pages);
        }
        if (error) {
          this._error.set(error);
        }
      },
      { injector: this.injector },
    );

    return signals;
  }

  /**
   * Clears the cached users data.
   */
  clearUsers(): void {
    // Tear the mirror down first, or it writes the old page straight back.
    this.syncEffect?.destroy();
    this.syncEffect = null;
    this._users.set([]);
    this._totalUsers.set(0);
    this._currentPage.set(1);
    this._totalPages.set(0);
    this._isLoading.set(false);
    this._error.set(null);
  }
}
