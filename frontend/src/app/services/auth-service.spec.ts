import { TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { Router } from '@angular/router';
import { of, throwError, firstValueFrom } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { AuthService } from './auth-service';
import { ApiService } from './api-service';
import { LocalStorageService, StorageSignal } from './local-storage-service';
import { UserInfoService } from './user-info-service';
import { LoginResponse, RegisterResponse } from '../types';

describe('AuthService', () => {
  let service: AuthService;
  let mockApiService: { post: Mock; get: Mock };
  let mockLocalStorageService: { connectString: Mock };
  let mockRouter: { navigate: Mock };
  let mockUserInfoService: { clearUser: Mock };
  let mockTokenStorage: StorageSignal<string | null>;

  // Backed by a real signal on purpose. With a plain closure, AuthService's
  // isAuthenticated computed has nothing to track and stays stuck on the
  // value it first read.
  const mockSignal = (initialValue: string | null): StorageSignal<string | null> => {
    const value = signal<string | null>(initialValue);
    return {
      value: value.asReadonly(),
      set: (v: string | null) => value.set(v),
      remove: () => value.set(null)
    };
  };

  beforeEach(() => {
    mockApiService = { post: vi.fn(), get: vi.fn() };
    mockRouter = { navigate: vi.fn() };
    mockUserInfoService = { clearUser: vi.fn() };
    mockTokenStorage = mockSignal(null);
    mockLocalStorageService = { connectString: vi.fn().mockReturnValue(mockTokenStorage) };

    TestBed.configureTestingModule({
      providers: [
        AuthService,
        { provide: ApiService, useValue: mockApiService },
        { provide: LocalStorageService, useValue: mockLocalStorageService },
        { provide: Router, useValue: mockRouter },
        { provide: UserInfoService, useValue: mockUserInfoService }
      ]
    });

    service = TestBed.inject(AuthService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    const mockLoginResponse: LoginResponse = {
      access_token: 'test_token',
      token_type: 'bearer'
    };

    it('should call ApiService with form data and store token on success', async () => {
      mockApiService.post.mockReturnValue(of(mockLoginResponse));

      const result = await firstValueFrom(service.login('test@example.com', 'password123'));

      expect(mockApiService.post).toHaveBeenCalled();
      expect(result).toEqual(mockLoginResponse);
      expect(mockTokenStorage.value()).toBe('test_token');
    });

    it('should remove token on login error', async () => {
      const error = new Error('Login failed');
      mockApiService.post.mockReturnValue(throwError(() => error));

      await expect(firstValueFrom(service.login('test@example.com', 'wrong_password')))
        .rejects.toThrow('Login failed');
      expect(mockTokenStorage.value()).toBeNull();
    });
  });

  describe('register', () => {
    const mockRegisterResponse: RegisterResponse = {
      id: '123',
      email: 'test@example.com'
    };

    it('should call ApiService with registration data', async () => {
      mockApiService.post.mockReturnValue(of(mockRegisterResponse));

      const result = await firstValueFrom(service.register('test@example.com', 'password123'));

      expect(mockApiService.post).toHaveBeenCalledWith(
        '/auth/register',
        { email: 'test@example.com', password: 'password123' }
      );
      expect(result).toEqual(mockRegisterResponse);
    });
  });

  describe('logout', () => {
    it('should remove token and navigate to login', () => {
      mockTokenStorage.set('some_token');

      service.logout();

      expect(mockTokenStorage.value()).toBeNull();
      expect(mockRouter.navigate).toHaveBeenCalledWith(['/login']);
    });

    // Otherwise the next user to sign in sees the previous user's email, and
    // their admin nav link if that user was an admin.
    it('should clear the cached user info', () => {
      mockTokenStorage.set('some_token');

      service.logout();

      expect(mockUserInfoService.clearUser).toHaveBeenCalled();
    });

    it('should report the user as unauthenticated afterwards', () => {
      mockTokenStorage.set('some_token');
      expect(service.isAuthenticated()).toBe(true);

      service.logout();

      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('getAuthorizationHeader', () => {
    it('should return bearer token when authenticated', () => {
      mockTokenStorage.set('my_token');
      expect(service.getAuthorizationHeader()).toBe('Bearer my_token');
    });

    it('should return null when not authenticated', () => {
      expect(service.getAuthorizationHeader()).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      mockTokenStorage.set('valid_token');
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return false when token is null', () => {
      expect(service.isAuthenticated()).toBe(false);
    });
  });
});
