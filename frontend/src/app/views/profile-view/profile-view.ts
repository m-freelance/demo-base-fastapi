import { Component, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { UpperCasePipe } from '@angular/common';
import { EMPTY, catchError } from 'rxjs';
import { UserInfoService } from '../../services';

@Component({
  selector: 'app-profile-view',
  imports: [UpperCasePipe],
  templateUrl: './profile-view.html',
  styleUrl: './profile-view.scss',
})
export class ProfileViewComponent {
  private readonly userInfoService = inject(UserInfoService);

  readonly currentUser = this.userInfoService.currentUser;
  readonly isLoading = this.userInfoService.isLoading;
  readonly error = this.userInfoService.error;
  readonly isAdmin = this.userInfoService.isAdmin;

  constructor() {
    // The header has usually loaded this already, so reusing the shared
    // request means visiting the profile normally costs no extra call.
    this.userInfoService
      .loadCurrentUser()
      .pipe(
        catchError(() => EMPTY),
        takeUntilDestroyed(),
      )
      .subscribe();
  }
}
