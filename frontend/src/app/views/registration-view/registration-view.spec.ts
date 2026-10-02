import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { RegistrationViewComponent } from './registration-view';
import { AuthService } from '../../services';
import { RegisterResponse } from '../../types';

describe('RegistrationViewComponent', () => {
  let component: RegistrationViewComponent;
  let fixture: ComponentFixture<RegistrationViewComponent>;
  let mockAuthService: { register: Mock };

  const mockRegisterResponse: RegisterResponse = {
    id: '123',
    email: 'test@example.com'
  };

  beforeEach(async () => {
    mockAuthService = { register: vi.fn() };

    await TestBed.configureTestingModule({
      imports: [RegistrationViewComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuthService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RegistrationViewComponent);
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

    it('should have empty confirmPassword', () => {
      expect(component.confirmPassword).toBe('');
    });

    it('should have password hidden by default', () => {
      expect(component.hidePassword()).toBe(true);
    });

    it('should have confirm password hidden by default', () => {
      expect(component.hideConfirmPassword()).toBe(true);
    });

    it('should not be loading initially', () => {
      expect(component.isLoading()).toBe(false);
    });

    it('should have no error message initially', () => {
      expect(component.errorMessage()).toBeNull();
    });

    it('should have no success message initially', () => {
      expect(component.successMessage()).toBeNull();
    });
  });

  describe('togglePasswordVisibility', () => {
    it('should toggle password visibility', () => {
      expect(component.hidePassword()).toBe(true);

      component.togglePasswordVisibility();

      expect(component.hidePassword()).toBe(false);

      component.togglePasswordVisibility();

      expect(component.hidePassword()).toBe(true);
    });
  });

  describe('toggleConfirmPasswordVisibility', () => {
    it('should toggle confirm password visibility', () => {
      expect(component.hideConfirmPassword()).toBe(true);

      component.toggleConfirmPasswordVisibility();

      expect(component.hideConfirmPassword()).toBe(false);

      component.toggleConfirmPasswordVisibility();

      expect(component.hideConfirmPassword()).toBe(true);
    });
  });

  describe('onRegister validation', () => {
    it('should set error message when all fields are empty', () => {
      component.email = '';
      component.password = '';
      component.confirmPassword = '';

      component.onRegister();

      expect(component.errorMessage()).toBe('Please fill in all fields');
      expect(mockAuthService.register).not.toHaveBeenCalled();
    });

    it('should set error message when email is empty', () => {
      component.email = '';
      component.password = 'password123';
      component.confirmPassword = 'password123';

      component.onRegister();

      expect(component.errorMessage()).toBe('Please fill in all fields');
    });

    it('should set error message when password is empty', () => {
      component.email = 'test@example.com';
      component.password = '';
      component.confirmPassword = 'password123';

      component.onRegister();

      expect(component.errorMessage()).toBe('Please fill in all fields');
    });

    it('should set error message for invalid email format', () => {
      component.email = 'invalid-email';
      component.password = 'password123';
      component.confirmPassword = 'password123';

      component.onRegister();

      expect(component.errorMessage()).toBe('Please enter a valid email address');
    });

    it('should set error message for email without @', () => {
      component.email = 'testexample.com';
      component.password = 'password123';
      component.confirmPassword = 'password123';

      component.onRegister();

      expect(component.errorMessage()).toBe('Please enter a valid email address');
    });

    it('should set error message for password less than 8 characters', () => {
      component.email = 'test@example.com';
      component.password = '1234567';
      component.confirmPassword = '1234567';

      component.onRegister();

      expect(component.errorMessage()).toBe('Password must be at least 8 characters long');
    });

    it('should set error message when passwords do not match', () => {
      component.email = 'test@example.com';
      component.password = 'password123';
      component.confirmPassword = 'password456';

      component.onRegister();

      expect(component.errorMessage()).toBe('Passwords do not match');
    });
  });

  describe('onRegister success', () => {
    beforeEach(() => {
      component.email = 'test@example.com';
      component.password = 'password123';
      component.confirmPassword = 'password123';
    });

    it('should call authService.register with correct credentials', () => {
      mockAuthService.register.mockReturnValue(of(mockRegisterResponse));

      component.onRegister();

      expect(mockAuthService.register).toHaveBeenCalledWith('test@example.com', 'password123');
    });

    it('should clear error message when register starts', () => {
      mockAuthService.register.mockReturnValue(of(mockRegisterResponse));
      component.errorMessage.set('Previous error');

      component.onRegister();

      expect(component.errorMessage()).toBeNull();
    });

    it('should set success message on successful registration', () => {
      mockAuthService.register.mockReturnValue(of(mockRegisterResponse));

      component.onRegister();

      expect(component.successMessage()).toBe('Registration successful! Redirecting to login...');
      expect(component.isLoading()).toBe(false);
    });
  });

  describe('onRegister errors', () => {
    beforeEach(() => {
      component.email = 'test@example.com';
      component.password = 'password123';
      component.confirmPassword = 'password123';
    });

    it('should set error message for 409 conflict (email exists)', () => {
      const error = { status: 409 };
      mockAuthService.register.mockReturnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage()).toBe('An account with this email already exists');
      expect(component.isLoading()).toBe(false);
    });

    it('should set error message for 422 validation error', () => {
      const error = { status: 422 };
      mockAuthService.register.mockReturnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage()).toBe('Invalid email or password format');
      expect(component.isLoading()).toBe(false);
    });

    it('should set error message for network error (status 0)', () => {
      const error = { status: 0 };
      mockAuthService.register.mockReturnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage()).toBe('Unable to connect to server');
      expect(component.isLoading()).toBe(false);
    });

    it('should set error message from API detail for other errors', () => {
      const error = { status: 500, error: { detail: 'Server error' } };
      mockAuthService.register.mockReturnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage()).toBe('Server error');
      expect(component.isLoading()).toBe(false);
    });

    it('should set generic error message when no detail provided', () => {
      const error = { status: 500, error: {} };
      mockAuthService.register.mockReturnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage()).toBe('Registration failed. Please try again.');
      expect(component.isLoading()).toBe(false);
    });
  });
});

