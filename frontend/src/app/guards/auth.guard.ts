import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services';

/**
 * Auth guard that redirects unauthenticated users to the login page.
 * Use this guard on routes that require authentication.
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Redirect to login page
  return router.createUrlTree(['/login']);
};

