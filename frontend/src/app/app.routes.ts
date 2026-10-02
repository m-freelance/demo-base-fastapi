import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './guards';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./views/login-view').then(m => m.LoginViewComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./views/registration-view').then(m => m.RegistrationViewComponent)
  },
  {
    path: 'home',
    loadComponent: () => import('./views/home-view').then(m => m.HomeViewComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./views/profile-view').then(m => m.ProfileViewComponent),
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    loadComponent: () => import('./views/admin-view').then(m => m.AdminViewComponent),
    canActivate: [authGuard, adminGuard]
  },
  {
    path: '**',
    redirectTo: 'home'
  }
];
