import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services';

/** Endpoints that establish a session and therefore must not be intercepted. */
const PUBLIC_AUTH_PATHS = ['/auth/login', '/auth/register'];

/**
 * HTTP interceptor that:
 * 1. Attaches the authorization token to outgoing requests
 * 2. Handles 401 responses by redirecting to login page
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Login and register carry their credentials in the body. Sending a stale
  // token with them is pointless, and their 401 means "wrong password", not
  // "session expired", so logging the user out here would redirect away from
  // the login form and discard the error message it is about to show.
  if (PUBLIC_AUTH_PATHS.some((path) => req.url.includes(path))) {
    return next(req);
  }

  // Get the authorization header
  const authHeader = authService.getAuthorizationHeader();

  // Clone the request and add authorization header if available
  const authReq = authHeader
    ? req.clone({
        setHeaders: {
          Authorization: authHeader,
        },
      })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Handle 401 Unauthorized responses
      if (error.status === 401) {
        authService.logout();
      }
      return throwError(() => error);
    }),
  );
};
