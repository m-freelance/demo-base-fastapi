import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { signal } from '@angular/core';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { UserManagementService, PaginatedUsersResponse } from './user-management-service';
import { SignalizerService, ApiSignals } from './signalizer-service';
import { UserInfo, UserRole } from '../types';

describe('UserManagementService', () => {
  let service: UserManagementService;
  let mockSignalizerService: { get: Mock };

  const mockUsers: UserInfo[] = [
    { user_uuid: '1', email: 'admin@test.com', is_active: true, role: UserRole.ADMIN },
    { user_uuid: '2', email: 'user@test.com', is_active: true, role: UserRole.USER },
    { user_uuid: '3', email: 'inactive@test.com', is_active: false, role: UserRole.USER }
  ];

  const mockPaginatedResponse: PaginatedUsersResponse = {
    items: mockUsers,
    total: 25,
    page: 1,
    size: 10,
    pages: 3
  };

  const createMockApiSignals = <T>(
    data: T | null = null,
    error: HttpErrorResponse | null = null,
    isLoading: boolean = false
  ): ApiSignals<T> => ({
    isLoading: signal(isLoading).asReadonly(),
    data: signal(data).asReadonly(),
    error: signal(error).asReadonly()
  });

  beforeEach(() => {
    mockSignalizerService = { get: vi.fn() };

    TestBed.configureTestingModule({
      providers: [
        UserManagementService,
        { provide: SignalizerService, useValue: mockSignalizerService }
      ]
    });

    service = TestBed.inject(UserManagementService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('initial state', () => {
    it('should have empty users array initially', () => {
      expect(service.users()).toEqual([]);
    });

    it('should have zero total users initially', () => {
      expect(service.totalUsers()).toBe(0);
    });

    it('should have page 1 as current page initially', () => {
      expect(service.currentPage()).toBe(1);
    });

    it('should have page size of 10 initially', () => {
      expect(service.pageSize()).toBe(10);
    });

    it('should have zero total pages initially', () => {
      expect(service.totalPages()).toBe(0);
    });

    it('should not be loading initially', () => {
      expect(service.isLoading()).toBe(false);
    });

    it('should have no error initially', () => {
      expect(service.error()).toBeNull();
    });
  });

  describe('fetchAllUsers', () => {
    it('should call signalizerService.get with correct URL and default pagination', () => {
      mockSignalizerService.get.mockReturnValue(createMockApiSignals(mockPaginatedResponse));

      service.fetchAllUsers();

      expect(mockSignalizerService.get).toHaveBeenCalledWith('/users?page=1&size=10');
    });

    it('should call signalizerService.get with custom pagination parameters', () => {
      mockSignalizerService.get.mockReturnValue(createMockApiSignals(mockPaginatedResponse));

      service.fetchAllUsers(2, 20);

      expect(mockSignalizerService.get).toHaveBeenCalledWith('/users?page=2&size=20');
    });

    it('should set isLoading to true when fetching starts', () => {
      mockSignalizerService.get.mockReturnValue(createMockApiSignals(null, null, true));

      service.fetchAllUsers();

      expect(service.isLoading()).toBe(true);
    });

    it('should return ApiSignals from signalizerService', () => {
      const expectedSignals = createMockApiSignals(mockPaginatedResponse);
      mockSignalizerService.get.mockReturnValue(expectedSignals);

      const result = service.fetchAllUsers();

      expect(result).toBe(expectedSignals);
    });
  });

  describe('clearUsers', () => {
    it('should reset users to empty array', () => {
      service.clearUsers();

      expect(service.users()).toEqual([]);
    });

    it('should reset totalUsers to 0', () => {
      service.clearUsers();

      expect(service.totalUsers()).toBe(0);
    });

    it('should reset currentPage to 1', () => {
      service.clearUsers();

      expect(service.currentPage()).toBe(1);
    });

    it('should reset totalPages to 0', () => {
      service.clearUsers();

      expect(service.totalPages()).toBe(0);
    });

    it('should reset isLoading to false', () => {
      mockSignalizerService.get.mockReturnValue(createMockApiSignals(null, null, true));
      service.fetchAllUsers();

      service.clearUsers();

      expect(service.isLoading()).toBe(false);
    });

    it('should reset error to null', () => {
      service.clearUsers();

      expect(service.error()).toBeNull();
    });
  });
});



