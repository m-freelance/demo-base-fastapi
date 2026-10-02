import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { signal, WritableSignal } from '@angular/core';
import { of } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { Header } from './header';
import { AuthService, UserInfoService } from '../../services';
import { UserInfo, UserRole } from '../../types';

describe('Header', () => {
  let component: Header;
  let fixture: ComponentFixture<Header>;
  let mockAuthService: { logout: Mock };
  let mockCurrentUser: WritableSignal<UserInfo | null>;
  let mockIsAdmin: WritableSignal<boolean>;
  let mockUserInfoService: {
    currentUser: () => UserInfo | null;
    isAdmin: () => boolean;
    loadCurrentUser: Mock;
  };

  const mockUser: UserInfo = {
    user_uuid: '123',
    email: 'test@example.com',
    is_active: true,
    role: UserRole.USER
  };

  beforeEach(async () => {
    mockAuthService = { logout: vi.fn() };
    mockCurrentUser = signal<UserInfo | null>(mockUser);
    mockIsAdmin = signal<boolean>(false);
    mockUserInfoService = {
      currentUser: () => mockCurrentUser(),
      isAdmin: () => mockIsAdmin(),
      loadCurrentUser: vi.fn().mockReturnValue(of(mockUser))
    };

    await TestBed.configureTestingModule({
      imports: [Header],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuthService },
        { provide: UserInfoService, useValue: mockUserInfoService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Header);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('userEmail', () => {
    it('should return user email when user is logged in', () => {
      expect(component.userEmail()).toBe('test@example.com');
    });

    it('should return empty string when user is null', () => {
      mockCurrentUser.set(null);

      expect(component.userEmail()).toBe('');
    });

    it('should return empty string when user email is undefined', () => {
      mockCurrentUser.set({ ...mockUser, email: undefined } as unknown as UserInfo);

      expect(component.userEmail()).toBe('');
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

  describe('toggleNavbar', () => {
    it('should toggle navbar from collapsed to expanded', () => {
      expect(component.isNavbarCollapsed()).toBe(true);

      component.toggleNavbar();

      expect(component.isNavbarCollapsed()).toBe(false);
    });

    it('should toggle navbar from expanded to collapsed', () => {
      component.toggleNavbar(); // First toggle to expand
      expect(component.isNavbarCollapsed()).toBe(false);

      component.toggleNavbar(); // Second toggle to collapse

      expect(component.isNavbarCollapsed()).toBe(true);
    });
  });

  describe('logout', () => {
    it('should call authService.logout when logout is called', () => {
      component.logout();

      expect(mockAuthService.logout).toHaveBeenCalled();
    });
  });

  describe('constructor', () => {
    it('should load the current user through the shared request', () => {
      expect(mockUserInfoService.loadCurrentUser).toHaveBeenCalled();
    });
  });
});
