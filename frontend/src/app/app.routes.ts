import { Routes } from '@angular/router';

import { AuthGuard } from './core/guards/auth.guard';
import { LayoutComponent } from './layout/layout.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/login/login.component').then(
        m => m.LoginComponent
      )
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./pages/register/register.component').then(
        m => m.RegisterComponent
      )
  },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/dashboard/dashboard.component').then(
            m => m.DashboardComponent
          )
      },
      {
        path: 'riders',
        loadComponent: () =>
          import('./pages/riders/riders.component').then(
            m => m.RidersComponent
          )
      },
      {
        path: 'orders',
        loadComponent: () =>
          import('./pages/orders/orders.component').then(
            m => m.OrdersComponent
          )
      },
      {
        path: 'profile',
        loadComponent: () =>
          import('./pages/profile/profile.component').then(
            m => m.ProfileComponent
          )
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./pages/settings/settings.component').then(
            m => m.SettingsComponent
          )
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'login'
  }
];