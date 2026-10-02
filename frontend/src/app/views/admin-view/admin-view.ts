import { Component, inject, OnInit, computed } from '@angular/core';
import { UpperCasePipe } from '@angular/common';
import { UserManagementService } from '../../services';
import { UserRole } from '../../types';

@Component({
  selector: 'app-admin-view',
  imports: [UpperCasePipe],
  templateUrl: './admin-view.html',
  styleUrl: './admin-view.scss'
})
export class AdminViewComponent implements OnInit {
  private readonly userManagementService = inject(UserManagementService);

  readonly users = this.userManagementService.users;
  readonly totalUsers = this.userManagementService.totalUsers;
  readonly currentPage = this.userManagementService.currentPage;
  readonly pageSize = this.userManagementService.pageSize;
  readonly totalPages = this.userManagementService.totalPages;
  readonly isLoading = this.userManagementService.isLoading;
  readonly error = this.userManagementService.error;

  readonly UserRole = UserRole;

  // Computed property for pagination display
  readonly paginationPages = computed(() => {
    const total = this.totalPages();
    const current = this.currentPage();
    const pages: number[] = [];

    // Show max 5 pages around current
    const start = Math.max(1, current - 2);
    const end = Math.min(total, current + 2);

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    return pages;
  });

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(page: number = 1): void {
    this.userManagementService.fetchAllUsers(page, 10);
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.loadUsers(page);
    }
  }

  previousPage(): void {
    if (this.currentPage() > 1) {
      this.goToPage(this.currentPage() - 1);
    }
  }

  nextPage(): void {
    if (this.currentPage() < this.totalPages()) {
      this.goToPage(this.currentPage() + 1);
    }
  }

  isAdmin(role: UserRole): boolean {
    return role === UserRole.ADMIN;
  }
}



