import { Component, computed, inject, signal } from '@angular/core';
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
    // Shares the request with the admin guard and the profile view. The error
    // is already on userInfoService.error, so swallow it here rather than let
    // an unhandled rejection escape the constructor.
    this.userInfoService
      .loadCurrentUser()
      .pipe(
        catchError(() => EMPTY),
        takeUntilDestroyed(),
      )
      .subscribe();
  }
}
