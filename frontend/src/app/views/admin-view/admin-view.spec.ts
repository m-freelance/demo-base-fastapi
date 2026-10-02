import { ComponentFixture, TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';

import { AdminViewComponent } from './admin-view';
import { UserManagementService } from '../../services';
import { UserInfo, UserRole } from '../../types';

describe('AdminViewComponent', () => {
  let component: AdminViewComponent;
  let fixture: ComponentFixture<AdminViewComponent>;
  let mockUserManagementService: {
    users: Mock;
    totalUsers: Mock;
    currentPage: Mock;
    pageSize: Mock;
    totalPages: Mock;
    isLoading: Mock;
    error: Mock;
    fetchAllUsers: Mock;
  };

  const mockUsers: UserInfo[] = [
    { user_uuid: '1', email: 'admin@test.com', is_active: true, role: UserRole.ADMIN },
    { user_uuid: '2', email: 'user@test.com', is_active: true, role: UserRole.USER },
    { user_uuid: '3', email: 'inactive@test.com', is_active: false, role: UserRole.USER }
  ];

  beforeEach(async () => {
    mockUserManagementService = {
      users: vi.fn().mockReturnValue(mockUsers),
      totalUsers: vi.fn().mockReturnValue(25),
      currentPage: vi.fn().mockReturnValue(1),
      pageSize: vi.fn().mockReturnValue(10),
      totalPages: vi.fn().mockReturnValue(3),
      isLoading: vi.fn().mockReturnValue(false),
      error: vi.fn().mockReturnValue(null),
      fetchAllUsers: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [AdminViewComponent],
      providers: [
        { provide: UserManagementService, useValue: mockUserManagementService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AdminViewComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should load users on init', () => {
      expect(mockUserManagementService.fetchAllUsers).toHaveBeenCalledWith(1, 10);
    });
  });

  describe('computed signals', () => {
    it('should expose users signal from service', () => {
      expect(component.users()).toEqual(mockUsers);
    });

    it('should expose totalUsers signal from service', () => {
      expect(component.totalUsers()).toBe(25);
    });

    it('should expose currentPage signal from service', () => {
      expect(component.currentPage()).toBe(1);
    });

    it('should expose pageSize signal from service', () => {
      expect(component.pageSize()).toBe(10);
    });

    it('should expose totalPages signal from service', () => {
      expect(component.totalPages()).toBe(3);
    });

    it('should expose isLoading signal from service', () => {
      expect(component.isLoading()).toBe(false);
    });

    it('should expose error signal from service', () => {
      expect(component.error()).toBeNull();
    });
  });

  describe('paginationPages', () => {
    it('should return array of page numbers around current page', () => {
      mockUserManagementService.totalPages.mockReturnValue(10);
      mockUserManagementService.currentPage.mockReturnValue(5);

      // Re-create component to use new mock values
      fixture = TestBed.createComponent(AdminViewComponent);
      component = fixture.componentInstance;

      const pages = component.paginationPages();
      expect(pages).toEqual([3, 4, 5, 6, 7]);
    });

    it('should handle first page', () => {
      mockUserManagementService.totalPages.mockReturnValue(10);
      mockUserManagementService.currentPage.mockReturnValue(1);

      fixture = TestBed.createComponent(AdminViewComponent);
      component = fixture.componentInstance;

      const pages = component.paginationPages();
      expect(pages).toEqual([1, 2, 3]);
    });

    it('should handle last page', () => {
      mockUserManagementService.totalPages.mockReturnValue(10);
      mockUserManagementService.currentPage.mockReturnValue(10);

      fixture = TestBed.createComponent(AdminViewComponent);
      component = fixture.componentInstance;

      const pages = component.paginationPages();
      expect(pages).toEqual([8, 9, 10]);
    });

    it('should handle small number of pages', () => {
      mockUserManagementService.totalPages.mockReturnValue(2);
      mockUserManagementService.currentPage.mockReturnValue(1);

      fixture = TestBed.createComponent(AdminViewComponent);
      component = fixture.componentInstance;

      const pages = component.paginationPages();
      expect(pages).toEqual([1, 2]);
    });
  });

  describe('loadUsers', () => {
    it('should call fetchAllUsers with default values', () => {
      mockUserManagementService.fetchAllUsers.mockClear();

      component.loadUsers();

      expect(mockUserManagementService.fetchAllUsers).toHaveBeenCalledWith(1, 10);
    });

    it('should call fetchAllUsers with specified page', () => {
      mockUserManagementService.fetchAllUsers.mockClear();

      component.loadUsers(3);

      expect(mockUserManagementService.fetchAllUsers).toHaveBeenCalledWith(3, 10);
    });
  });

  describe('goToPage', () => {
    it('should load users for valid page', () => {
      mockUserManagementService.fetchAllUsers.mockClear();
      mockUserManagementService.totalPages.mockReturnValue(5);

      component.goToPage(3);

      expect(mockUserManagementService.fetchAllUsers).toHaveBeenCalledWith(3, 10);
    });

    it('should not load users for page less than 1', () => {
      mockUserManagementService.fetchAllUsers.mockClear();

      component.goToPage(0);

      expect(mockUserManagementService.fetchAllUsers).not.toHaveBeenCalled();
    });

    it('should not load users for page greater than totalPages', () => {
      mockUserManagementService.fetchAllUsers.mockClear();
      mockUserManagementService.totalPages.mockReturnValue(3);

      component.goToPage(5);

      expect(mockUserManagementService.fetchAllUsers).not.toHaveBeenCalled();
    });
  });

  describe('previousPage', () => {
    it('should go to previous page when not on first page', () => {
      mockUserManagementService.fetchAllUsers.mockClear();
      mockUserManagementService.currentPage.mockReturnValue(3);
      mockUserManagementService.totalPages.mockReturnValue(5);

      component.previousPage();

      expect(mockUserManagementService.fetchAllUsers).toHaveBeenCalledWith(2, 10);
    });

    it('should not go to previous page when on first page', () => {
      mockUserManagementService.fetchAllUsers.mockClear();
      mockUserManagementService.currentPage.mockReturnValue(1);

      component.previousPage();

      expect(mockUserManagementService.fetchAllUsers).not.toHaveBeenCalled();
    });
  });

  describe('nextPage', () => {
    it('should go to next page when not on last page', () => {
      mockUserManagementService.fetchAllUsers.mockClear();
      mockUserManagementService.currentPage.mockReturnValue(2);
      mockUserManagementService.totalPages.mockReturnValue(5);

      component.nextPage();

      expect(mockUserManagementService.fetchAllUsers).toHaveBeenCalledWith(3, 10);
    });

    it('should not go to next page when on last page', () => {
      mockUserManagementService.fetchAllUsers.mockClear();
      mockUserManagementService.currentPage.mockReturnValue(5);
      mockUserManagementService.totalPages.mockReturnValue(5);

      component.nextPage();

      expect(mockUserManagementService.fetchAllUsers).not.toHaveBeenCalled();
    });
  });

  describe('isAdmin', () => {
    it('should return true for admin role', () => {
      expect(component.isAdmin(UserRole.ADMIN)).toBe(true);
    });

    it('should return false for user role', () => {
      expect(component.isAdmin(UserRole.USER)).toBe(false);
    });
  });

  describe('UserRole', () => {
    it('should expose UserRole enum', () => {
      expect(component.UserRole).toBe(UserRole);
    });
  });
});


