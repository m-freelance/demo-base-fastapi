import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services';

@Component({
  selector: 'app-registration-view',
  imports: [
    FormsModule,
    RouterLink
  ],
  templateUrl: './registration-view.html',
  styleUrl: './registration-view.scss'
})
export class RegistrationViewComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  email = '';
  password = '';
  confirmPassword = '';
  hidePassword = signal(true);
  hideConfirmPassword = signal(true);
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  togglePasswordVisibility(): void {
    this.hidePassword.update(hide => !hide);
  }

  toggleConfirmPasswordVisibility(): void {
    this.hideConfirmPassword.update(hide => !hide);
  }

  onRegister(): void {
    // Validate fields
    if (!this.email || !this.password || !this.confirmPassword) {
      this.errorMessage.set('Please fill in all fields');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.errorMessage.set('Please enter a valid email address');
      return;
    }

    // Validate password length
    if (this.password.length < 8) {
      this.errorMessage.set('Password must be at least 8 characters long');
      return;
    }

    // Validate password match
    if (this.password !== this.confirmPassword) {
      this.errorMessage.set('Passwords do not match');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    this.authService.register(this.email, this.password).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.successMessage.set('Registration successful! Redirecting to login...');

        // Redirect to login after short delay
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (err) => {
        this.isLoading.set(false);
        if (err.status === 409) {
          this.errorMessage.set('An account with this email already exists');
        } else if (err.status === 422) {
          this.errorMessage.set('Invalid email or password format');
        } else if (err.status === 0) {
          this.errorMessage.set('Unable to connect to server');
        } else {
          this.errorMessage.set(err.error?.detail || 'Registration failed. Please try again.');
        }
      }
    });
  }
}

