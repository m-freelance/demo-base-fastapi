import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { UserInfoService } from '../services';
import { UserRole } from '../types';

/**
 * Admin guard that restricts access to admin users only.
 * Redirects non-admin users to the home page.
 * Note: This guard assumes the user is already authenticated.
 */
export const adminGuard: CanActivateFn = () => {
  const userInfoService = inject(UserInfoService);
  const router = inject(Router);

  // Wait on the request instead of reading the cached signal. On a reload
  // straight to /admin nothing has fetched the user yet, so a synchronous
  // role check sees null and bounces the admin who just asked for the page.
  return userInfoService.loadCurrentUser().pipe(
    map((user) => (user.role === UserRole.ADMIN ? true : router.createUrlTree(['/home']))),
    // A failure here is an expired or rejected token, so send them to login.
    catchError(() => of(router.createUrlTree(['/login']))),
  );
};
