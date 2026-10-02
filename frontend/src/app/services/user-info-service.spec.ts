import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError, firstValueFrom } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { UserInfoService } from './user-info-service';
import { ApiService } from './api-service';
import { UserInfo, UserRole } from '../types';

describe('UserInfoService', () => {
  let service: UserInfoService;
  let mockApiService: { get: Mock };

  // Mock user data matching backend GetUserResponseDto
  const mockUserInfo: UserInfo = {
    user_uuid: '550e8400-e29b-41d4-a716-446655440000',
    email: 'test@example.com',
    is_active: true,
    role: UserRole.USER,
  };

  const mockAdminUserInfo: UserInfo = {
    user_uuid: '550e8400-e29b-41d4-a716-446655440001',
    email: 'admin@example.com',
    is_active: true,
    role: UserRole.ADMIN,
  };

  beforeEach(() => {
    mockApiService = { get: vi.fn() };

    TestBed.configureTestingModule({
      providers: [UserInfoService, { provide: ApiService, useValue: mockApiService }],
    });

    service = TestBed.inject(UserInfoService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('loadCurrentUser', () => {
    it('should call the /users/me endpoint', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());

      expect(mockApiService.get).toHaveBeenCalledWith('/users/me');
    });

    it('should emit the user returned by the API', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      const user = await firstValueFrom(service.loadCurrentUser());

      expect(user).toEqual(mockUserInfo);
    });

    it('should populate the currentUser signal', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());

      expect(service.currentUser()).toEqual(mockUserInfo);
    });

    it('should issue only one request for concurrent callers', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      // The header, the admin guard and the profile view all ask at once.
      await Promise.all([
        firstValueFrom(service.loadCurrentUser()),
        firstValueFrom(service.loadCurrentUser()),
        firstValueFrom(service.loadCurrentUser()),
      ]);

      expect(mockApiService.get).toHaveBeenCalledTimes(1);
    });

    it('should replay the cached user to a later caller without refetching', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());
      const second = await firstValueFrom(service.loadCurrentUser());

      expect(second).toEqual(mockUserInfo);
      expect(mockApiService.get).toHaveBeenCalledTimes(1);
    });

    it('should clear isLoading once the request resolves', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());

      expect(service.isLoading()).toBe(false);
    });

    it('should expose the error and rethrow it on failure', async () => {
      const mockError = new HttpErrorResponse({
        status: 401,
        statusText: 'Unauthorized',
        error: { detail: 'Invalid or missing authentication token' },
      });
      mockApiService.get.mockReturnValue(throwError(() => mockError));

      await expect(firstValueFrom(service.loadCurrentUser())).rejects.toBe(mockError);
      expect(service.error()).toBe(mockError);
      expect(service.isLoading()).toBe(false);
      expect(service.currentUser()).toBeNull();
    });

    it('should retry after a failure instead of replaying the error', async () => {
      const mockError = new HttpErrorResponse({ status: 500 });
      mockApiService.get.mockReturnValueOnce(throwError(() => mockError));

      await expect(firstValueFrom(service.loadCurrentUser())).rejects.toBe(mockError);

      mockApiService.get.mockReturnValue(of(mockUserInfo));
      const user = await firstValueFrom(service.loadCurrentUser());

      expect(user).toEqual(mockUserInfo);
      expect(mockApiService.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('isAuthenticated computed', () => {
    it('should return true when user is loaded and active', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());

      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return false when user is not loaded', () => {
      expect(service.isAuthenticated()).toBe(false);
    });

    it('should return false when user is inactive', async () => {
      mockApiService.get.mockReturnValue(of({ ...mockUserInfo, is_active: false }));

      await firstValueFrom(service.loadCurrentUser());

      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('isAdmin computed', () => {
    it('should return true when user has admin role', async () => {
      mockApiService.get.mockReturnValue(of(mockAdminUserInfo));

      await firstValueFrom(service.loadCurrentUser());

      expect(service.isAdmin()).toBe(true);
    });

    it('should return false when user has user role', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());

      expect(service.isAdmin()).toBe(false);
    });

    it('should return false when user is not loaded', () => {
      expect(service.isAdmin()).toBe(false);
    });
  });

  describe('clearUser', () => {
    it('should clear user data', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));

      await firstValueFrom(service.loadCurrentUser());
      expect(service.currentUser()).toEqual(mockUserInfo);

      service.clearUser();

      expect(service.currentUser()).toBeNull();
      expect(service.error()).toBeNull();
      expect(service.isLoading()).toBe(false);
    });

    it('should drop the cached request so the next user is refetched', async () => {
      mockApiService.get.mockReturnValue(of(mockUserInfo));
      await firstValueFrom(service.loadCurrentUser());

      service.clearUser();

      mockApiService.get.mockReturnValue(of(mockAdminUserInfo));
      const next = await firstValueFrom(service.loadCurrentUser());

      expect(next).toEqual(mockAdminUserInfo);
      expect(mockApiService.get).toHaveBeenCalledTimes(2);
    });
  });
});
