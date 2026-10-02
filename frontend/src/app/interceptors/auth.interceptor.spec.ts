import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { describe, it, expect, beforeEach, afterEach, vi, Mock } from 'vitest';

import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../services';

describe('authInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let mockAuthService: { getAuthorizationHeader: Mock; logout: Mock };

  const API = 'http://localhost:8000/api/v1';

  beforeEach(() => {
    mockAuthService = {
      getAuthorizationHeader: vi.fn().mockReturnValue('Bearer test_token'),
      logout: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: mockAuthService },
      ],
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('attaching the token', () => {
    it('should add the Authorization header to a normal request', () => {
      http.get(`${API}/users/me`).subscribe();

      const req = httpMock.expectOne(`${API}/users/me`);
      expect(req.request.headers.get('Authorization')).toBe('Bearer test_token');
      req.flush({});
    });

    it('should leave the request alone when there is no token', () => {
      mockAuthService.getAuthorizationHeader.mockReturnValue(null);

      http.get(`${API}/users/me`).subscribe();

      const req = httpMock.expectOne(`${API}/users/me`);
      expect(req.request.headers.has('Authorization')).toBe(false);
      req.flush({});
    });

    it('should not attach a token to the login request', () => {
      http.post(`${API}/auth/login`, 'username=a&password=b').subscribe();

      const req = httpMock.expectOne(`${API}/auth/login`);
      expect(req.request.headers.has('Authorization')).toBe(false);
      req.flush({ access_token: 't', token_type: 'bearer' });
    });

    it('should not attach a token to the register request', () => {
      http.post(`${API}/auth/register`, { email: 'a@b.c', password: 'password' }).subscribe();

      const req = httpMock.expectOne(`${API}/auth/register`);
      expect(req.request.headers.has('Authorization')).toBe(false);
      req.flush({ id: '1', email: 'a@b.c' });
    });
  });

  describe('handling 401', () => {
    it('should log out on a 401 from a normal request', () => {
      http.get(`${API}/users/me`).subscribe({ error: () => undefined });

      httpMock
        .expectOne(`${API}/users/me`)
        .flush({ detail: 'Invalid or expired token' }, { status: 401, statusText: 'Unauthorized' });

      expect(mockAuthService.logout).toHaveBeenCalled();
    });

    it('should rethrow the 401 so the caller still sees it', () => {
      const onError = vi.fn();
      http.get(`${API}/users/me`).subscribe({ error: onError });

      httpMock.expectOne(`${API}/users/me`).flush({}, { status: 401, statusText: 'Unauthorized' });

      expect(onError).toHaveBeenCalled();
      expect(onError.mock.calls[0][0].status).toBe(401);
    });

    it('should NOT log out on a 401 from login, so the form keeps its error', () => {
      const onError = vi.fn();
      http.post(`${API}/auth/login`, 'username=a&password=wrong').subscribe({ error: onError });

      httpMock
        .expectOne(`${API}/auth/login`)
        .flush(
          { detail: 'Incorrect email or password' },
          { status: 401, statusText: 'Unauthorized' },
        );

      expect(mockAuthService.logout).not.toHaveBeenCalled();
      expect(onError).toHaveBeenCalled();
    });

    it('should NOT log out on a 401 from register', () => {
      http
        .post(`${API}/auth/register`, { email: 'a@b.c', password: 'password' })
        .subscribe({ error: () => undefined });

      httpMock
        .expectOne(`${API}/auth/register`)
        .flush({}, { status: 401, statusText: 'Unauthorized' });

      expect(mockAuthService.logout).not.toHaveBeenCalled();
    });

    it('should not log out on other error statuses', () => {
      http.get(`${API}/users`).subscribe({ error: () => undefined });

      httpMock.expectOne(`${API}/users`).flush({}, { status: 500, statusText: 'Server Error' });

      expect(mockAuthService.logout).not.toHaveBeenCalled();
    });
  });
});
