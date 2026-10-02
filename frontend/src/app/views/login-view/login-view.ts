import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services';

@Component({
  selector: 'app-login-view',
  imports: [
    FormsModule,
    RouterLink
  ],
  templateUrl: './login-view.html',
  styleUrl: './login-view.scss'
})
export class LoginViewComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  email = '';
  password = '';
  hidePassword = signal(true);
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  togglePasswordVisibility(): void {
    this.hidePassword.update(hide => !hide);
  }

  onLogin(): void {
    if (!this.email || !this.password) {
      this.errorMessage.set('Please enter email and password');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.router.navigate(['/home']);
      },
      error: (err) => {
        this.isLoading.set(false);
        if (err.status === 401) {
          this.errorMessage.set('Invalid email or password');
        } else if (err.status === 0) {
          this.errorMessage.set('Unable to connect to server');
        } else {
          this.errorMessage.set(err.error?.detail || 'Login failed. Please try again.');
        }
      }
    });
  }
}
