import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
  UrlTree,
  provideRouter,
} from '@angular/router';
import { Observable, firstValueFrom, of, throwError } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { adminGuard } from './admin.guard';
import { UserInfoService } from '../services';
import { UserInfo, UserRole } from '../types';

describe('adminGuard', () => {
  let router: Router;
  let mockUserInfoService: { currentUser: () => UserInfo | null; loadCurrentUser: Mock };

  const adminUser: UserInfo = {
    user_uuid: '1',
    email: 'admin@example.com',
    is_active: true,
    role: UserRole.ADMIN,
  };

  const regularUser: UserInfo = {
    user_uuid: '2',
    email: 'user@example.com',
    is_active: true,
    role: UserRole.USER,
  };

  // The guard takes the route and state but ignores both.
  const runGuard = () =>
    TestBed.runInInjectionContext(() =>
      adminGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    ) as Observable<boolean | UrlTree>;

  beforeEach(() => {
    mockUserInfoService = {
      currentUser: () => null,
      loadCurrentUser: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [provideRouter([]), { provide: UserInfoService, useValue: mockUserInfoService }],
    });

    router = TestBed.inject(Router);
  });

  it('should allow access for an admin', async () => {
    mockUserInfoService.loadCurrentUser.mockReturnValue(of(adminUser));

    await expect(firstValueFrom(runGuard())).resolves.toBe(true);
  });

  it('should redirect a regular user to home', async () => {
    mockUserInfoService.loadCurrentUser.mockReturnValue(of(regularUser));

    const result = await firstValueFrom(runGuard());

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/home');
  });

  // Regression test. The guard used to read the currentUser signal
  // synchronously, so on a reload straight to /admin nothing had fetched the
  // user yet and every admin was redirected to /home.
  it('should allow an admin who deep-links to /admin before the user is cached', async () => {
    mockUserInfoService.currentUser = () => null;
    mockUserInfoService.loadCurrentUser.mockReturnValue(of(adminUser));

    // Nothing has populated the cache at the moment the guard runs.
    expect(mockUserInfoService.currentUser()).toBeNull();

    await expect(firstValueFrom(runGuard())).resolves.toBe(true);
    expect(mockUserInfoService.loadCurrentUser).toHaveBeenCalled();
  });

  it('should redirect to login when the user request fails', async () => {
    mockUserInfoService.loadCurrentUser.mockReturnValue(
      throwError(() => new HttpErrorResponse({ status: 401 })),
    );

    const result = await firstValueFrom(runGuard());

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/login');
  });
});
