import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { signal, WritableSignal } from '@angular/core';
import { of, throwError } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { ProfileViewComponent } from './profile-view';
import { UserInfoService } from '../../services';
import { UserInfo, UserRole } from '../../types';

describe('ProfileViewComponent', () => {
  let component: ProfileViewComponent;
  let fixture: ComponentFixture<ProfileViewComponent>;
  let mockCurrentUser: WritableSignal<UserInfo | null>;
  let mockIsLoading: WritableSignal<boolean>;
  let mockError: WritableSignal<HttpErrorResponse | null>;
  let mockIsAdmin: WritableSignal<boolean>;
  let mockUserInfoService: {
    currentUser: WritableSignal<UserInfo | null>;
    isLoading: WritableSignal<boolean>;
    error: WritableSignal<HttpErrorResponse | null>;
    isAdmin: WritableSignal<boolean>;
    loadCurrentUser: Mock;
  };

  const mockUser: UserInfo = {
    user_uuid: '123',
    email: 'test@example.com',
    is_active: true,
    role: UserRole.USER,
  };

  const createComponent = () => {
    fixture = TestBed.createComponent(ProfileViewComponent);
    component = fixture.componentInstance;
    return component;
  };

  beforeEach(async () => {
    mockCurrentUser = signal<UserInfo | null>(mockUser);
    mockIsLoading = signal<boolean>(false);
    mockError = signal<HttpErrorResponse | null>(null);
    mockIsAdmin = signal<boolean>(false);

    mockUserInfoService = {
      currentUser: mockCurrentUser,
      isLoading: mockIsLoading,
      error: mockError,
      isAdmin: mockIsAdmin,
      loadCurrentUser: vi.fn().mockReturnValue(of(mockUser)),
    };

    await TestBed.configureTestingModule({
      imports: [ProfileViewComponent],
      providers: [{ provide: UserInfoService, useValue: mockUserInfoService }],
    }).compileComponents();

    createComponent();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should reuse the shared user request rather than fetching its own', () => {
    expect(mockUserInfoService.loadCurrentUser).toHaveBeenCalledTimes(1);
  });

  describe('currentUser', () => {
    it('should expose the user from the shared service', () => {
      expect(component.currentUser()).toEqual(mockUser);
    });

    it('should return null when no user is loaded', () => {
      mockCurrentUser.set(null);

      expect(component.currentUser()).toBeNull();
    });
  });

  describe('isLoading', () => {
    it('should reflect the loading state of the shared request', () => {
      mockIsLoading.set(true);

      expect(component.isLoading()).toBe(true);
    });

    it('should return false when not loading', () => {
      expect(component.isLoading()).toBe(false);
    });
  });

  describe('error', () => {
    it('should expose the error from the shared service', () => {
      const httpError = new HttpErrorResponse({ status: 500, statusText: 'Server Error' });
      mockError.set(httpError);

      expect(component.error()).toBe(httpError);
    });

    it('should return null when no error', () => {
      expect(component.error()).toBeNull();
    });

    it('should not surface a rejected request as an unhandled error', async () => {
      const httpError = new HttpErrorResponse({ status: 401 });
      mockUserInfoService.loadCurrentUser.mockReturnValue(throwError(() => httpError));

      expect(() => createComponent()).not.toThrow();
      await fixture.whenStable();
    });
  });

  describe('isAdmin', () => {
    it('should return false for regular user', () => {
      expect(component.isAdmin()).toBe(false);
    });

    it('should return true for admin user', () => {
      mockIsAdmin.set(true);

      expect(component.isAdmin()).toBe(true);
    });
  });
});
