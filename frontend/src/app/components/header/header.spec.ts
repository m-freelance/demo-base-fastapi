import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { signal, WritableSignal } from '@angular/core';
import { firstValueFrom, of } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { Header } from './header';
import { AuthService, ApiService, LocalStorageService, UserInfoService } from '../../services';
import type { StorageSignal } from '../../services';
import { LoginResponse, UserInfo, UserRole } from '../../types';

describe('Header', () => {
  let component: Header;
  let fixture: ComponentFixture<Header>;
  let mockAuthService: { logout: Mock; token: WritableSignal<string | null> };
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
    mockAuthService = { logout: vi.fn(), token: signal<string | null>('token_a') };
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

// Real AuthService and UserInfoService, so these cover the actual chain from a
// token change through to what the bar renders. Only HTTP and storage are
// doubled.
describe('Header reacting to auth changes', () => {
  let fixture: ComponentFixture<Header>;
  let authService: AuthService;
  let api: { post: Mock; get: Mock };
  let tokenSignal: WritableSignal<string | null>;

  const adminUser: UserInfo = {
    user_uuid: 'a',
    email: 'admin@example.com',
    is_active: true,
    role: UserRole.ADMIN
  };

  const regularUser: UserInfo = {
    user_uuid: 'b',
    email: 'user@example.com',
    is_active: true,
    role: UserRole.USER
  };

  const newToken: LoginResponse = { access_token: 'token_b', token_type: 'bearer' };

  const createHeader = async () => {
    fixture = TestBed.createComponent(Header);
    await fixture.whenStable();
    return fixture.componentInstance;
  };

  beforeEach(async () => {
    TestBed.resetTestingModule();

    api = { post: vi.fn(), get: vi.fn() };
    tokenSignal = signal<string | null>(null);
    const tokenStorage: StorageSignal<string | null> = {
      value: tokenSignal.asReadonly(),
      set: (v) => tokenSignal.set(v),
      remove: () => tokenSignal.set(null)
    };

    await TestBed.configureTestingModule({
      imports: [Header],
      providers: [
        provideRouter([{ path: 'login', children: [] }]),
        { provide: ApiService, useValue: api },
        { provide: LocalStorageService, useValue: { connectString: () => tokenStorage } }
      ]
    }).compileComponents();

    authService = TestBed.inject(AuthService);
  });

  it('should show the new user email after an account switch, with no navigation or reload', async () => {
    tokenSignal.set('token_a');
    api.get.mockReturnValue(of(adminUser));
    const component = await createHeader();
    expect(component.userEmail()).toBe('admin@example.com');
    expect(component.isAdmin()).toBe(true);

    api.post.mockReturnValue(of(newToken));
    api.get.mockReturnValue(of(regularUser));
    await firstValueFrom(authService.login('user@example.com', 'password'));
    await fixture.whenStable();

    // Same instance throughout, so nothing remounted it on our behalf.
    expect(fixture.componentInstance).toBe(component);
    expect(component.userEmail()).toBe('user@example.com');
    expect(component.isAdmin()).toBe(false);
  });

  it('should request /users/me exactly once for a single login', async () => {
    const component = await createHeader();
    expect(api.get).not.toHaveBeenCalled();
    expect(component.userEmail()).toBe('');

    api.post.mockReturnValue(of(newToken));
    api.get.mockReturnValue(of(regularUser));
    await firstValueFrom(authService.login('user@example.com', 'password'));
    await fixture.whenStable();

    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledWith('/users/me');
  });

  it('should not request /users/me on logout', async () => {
    tokenSignal.set('token_a');
    api.get.mockReturnValue(of(adminUser));
    await createHeader();
    const callsWhileSignedIn = api.get.mock.calls.length;

    authService.logout();
    await fixture.whenStable();

    expect(tokenSignal()).toBeNull();
    expect(api.get.mock.calls.length).toBe(callsWhileSignedIn);
  });
});
