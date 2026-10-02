import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
  UrlTree,
  provideRouter,
} from '@angular/router';
import { signal, WritableSignal } from '@angular/core';
import { describe, it, expect, beforeEach } from 'vitest';

import { authGuard } from './auth.guard';
import { AuthService } from '../services';

describe('authGuard', () => {
  let router: Router;
  let mockIsAuthenticated: WritableSignal<boolean>;

  // The guard takes the route and state but ignores both.
  const runGuard = () =>
    TestBed.runInInjectionContext(() =>
      authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );

  beforeEach(() => {
    mockIsAuthenticated = signal<boolean>(false);

    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: { isAuthenticated: () => mockIsAuthenticated() } },
      ],
    });

    router = TestBed.inject(Router);
  });

  it('should allow access when a token is present', () => {
    mockIsAuthenticated.set(true);

    expect(runGuard()).toBe(true);
  });

  it('should redirect to login when there is no token', () => {
    mockIsAuthenticated.set(false);

    const result = runGuard();

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/login');
  });
});
