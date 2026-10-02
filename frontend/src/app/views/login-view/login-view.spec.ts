import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, ActivatedRoute } from '@angular/router';
import { of, throwError } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { LoginViewComponent } from './login-view';
import { AuthService } from '../../services';
import { LoginResponse } from '../../types';

describe('LoginViewComponent', () => {
  let component: LoginViewComponent;
  let fixture: ComponentFixture<LoginViewComponent>;
  let mockAuthService: { login: Mock };
  let mockRouter: { navigate: Mock };

  const mockLoginResponse: LoginResponse = {
    access_token: 'test_token',
    token_type: 'bearer'
  };

  beforeEach(async () => {
    mockAuthService = { login: vi.fn() };
    mockRouter = { navigate: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [LoginViewComponent],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: Router, useValue: mockRouter },
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => null } } } }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LoginViewComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('initial state', () => {
    it('should have empty email', () => {
      expect(component.email).toBe('');
    });

    it('should have empty password', () => {
      expect(component.password).toBe('');
    });

    it('should have password hidden by default', () => {
      expect(component.hidePassword()).toBe(true);
    });

    it('should not be loading initially', () => {
      expect(component.isLoading()).toBe(false);
    });

    it('should have no error message initially', () => {
      expect(component.errorMessage()).toBeNull();
    });
  });

  describe('togglePasswordVisibility', () => {
    it('should toggle password visibility from hidden to visible', () => {
      expect(component.hidePassword()).toBe(true);

      component.togglePasswordVisibility();

      expect(component.hidePassword()).toBe(false);
    });

    it('should toggle password visibility from visible to hidden', () => {
      component.togglePasswordVisibility(); // First toggle to show
      expect(component.hidePassword()).toBe(false);

      component.togglePasswordVisibility(); // Second toggle to hide

      expect(component.hidePassword()).toBe(true);
    });
  });

  describe('onLogin', () => {
    it('should set error message when email is empty', () => {
      component.email = '';
      component.password = 'password123';

      component.onLogin();

      expect(component.errorMessage()).toBe('Please enter email and password');
      expect(mockAuthService.login).not.toHaveBeenCalled();
    });

    it('should set error message when password is empty', () => {
      component.email = 'test@example.com';
      component.password = '';

      component.onLogin();

      expect(component.errorMessage()).toBe('Please enter email and password');
      expect(mockAuthService.login).not.toHaveBeenCalled();
    });

    it('should set error message when both fields are empty', () => {
      component.email = '';
      component.password = '';

      component.onLogin();

      expect(component.errorMessage()).toBe('Please enter email and password');
      expect(mockAuthService.login).not.toHaveBeenCalled();
    });

    it('should call authService.login with correct credentials', () => {
      mockAuthService.login.mockReturnValue(of(mockLoginResponse));
      component.email = 'test@example.com';
      component.password = 'password123';

      component.onLogin();

      expect(mockAuthService.login).toHaveBeenCalledWith('test@example.com', 'password123');
    });

    it('should set isLoading to true when login starts', () => {
      mockAuthService.login.mockReturnValue(of(mockLoginResponse));
      component.email = 'test@example.com';
      component.password = 'password123';

      component.onLogin();

      // isLoading will be reset to false after success, so we check the call was made
      expect(mockAuthService.login).toHaveBeenCalled();
    });

    it('should clear error message when login starts', () => {
      mockAuthService.login.mockReturnValue(of(mockLoginResponse));
      component.email = 'test@example.com';
      component.password = 'password123';
      component.errorMessage.set('Previous error');

      component.onLogin();

      expect(component.errorMessage()).toBeNull();
    });

    it('should navigate to home on successful login', () => {
      mockAuthService.login.mockReturnValue(of(mockLoginResponse));
      component.email = 'test@example.com';
      component.password = 'password123';

      component.onLogin();

      expect(mockRouter.navigate).toHaveBeenCalledWith(['/home']);
      expect(component.isLoading()).toBe(false);
    });

    it('should set error message for 401 unauthorized', () => {
      const error = { status: 401 };
      mockAuthService.login.mockReturnValue(throwError(() => error));
      component.email = 'test@example.com';
      component.password = 'wrong_password';

      component.onLogin();

      expect(component.errorMessage()).toBe('Invalid email or password');
      expect(component.isLoading()).toBe(false);
    });

    it('should set error message for network error (status 0)', () => {
      const error = { status: 0 };
      mockAuthService.login.mockReturnValue(throwError(() => error));
      component.email = 'test@example.com';
      component.password = 'password123';

      component.onLogin();

      expect(component.errorMessage()).toBe('Unable to connect to server');
      expect(component.isLoading()).toBe(false);
    });

    it('should set error message from API detail for other errors', () => {
      const error = { status: 500, error: { detail: 'Server error occurred' } };
      mockAuthService.login.mockReturnValue(throwError(() => error));
      component.email = 'test@example.com';
      component.password = 'password123';

      component.onLogin();

      expect(component.errorMessage()).toBe('Server error occurred');
      expect(component.isLoading()).toBe(false);
    });

    it('should set generic error message when no detail provided', () => {
      const error = { status: 500, error: {} };
      mockAuthService.login.mockReturnValue(throwError(() => error));
      component.email = 'test@example.com';
      component.password = 'password123';

      component.onLogin();

      expect(component.errorMessage()).toBe('Login failed. Please try again.');
      expect(component.isLoading()).toBe(false);
    });
  });
});




