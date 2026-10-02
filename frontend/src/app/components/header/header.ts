import { Component, DestroyRef, computed, effect, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { EMPTY, catchError } from 'rxjs';
import { AuthService, UserInfoService } from '../../services';

@Component({
  selector: 'app-header',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  private readonly authService = inject(AuthService);
  private readonly userInfoService = inject(UserInfoService);
  private readonly destroyRef = inject(DestroyRef);

  readonly userEmail = computed(() => this.userInfoService.currentUser()?.email || '');
  readonly isAdmin = computed(() => this.userInfoService.isAdmin());
  readonly isNavbarCollapsed = signal(true);

  toggleNavbar(): void {
    this.isNavbarCollapsed.update((value) => !value);
  }

  logout(): void {
    this.authService.logout();
  }

  constructor() {
    // Keyed on the token, not on isAuthenticated. /login has no guard, so
    // signing in as someone else swaps one token for another without this
    // component ever being destroyed, and a one-shot fetch in the constructor
    // would leave the first user's name in the bar.
    effect(() => {
      const token = this.authService.token();

      // Signing out. Asking for /users/me without credentials would only 401.
      if (!token) {
        return;
      }

      // Shared with the admin guard and the profile view, so a normal login
      // still costs one request. The error is already on userInfoService.error.
      this.userInfoService
        .loadCurrentUser()
        .pipe(
          catchError(() => EMPTY),
          takeUntilDestroyed(this.destroyRef)
        )
        .subscribe();
    });
  }
}
