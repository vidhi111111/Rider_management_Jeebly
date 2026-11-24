import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { BreadcrumbComponent } from '../shared/breadcrumb/breadcrumb.component';
import { AuthService } from '../core/services/auth.service';
import { LanguageService } from '../core/services/language.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    BreadcrumbComponent
  ],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css']
})
export class LayoutComponent implements OnInit {
  isSidebarOpen = false; // Mobile drawer open
  isSidebarCollapsed = false; // Desktop collapse mode
  isProfileMenuOpen = false;

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router,
    public readonly langService: LanguageService
  ) {}

  ngOnInit(): void {
    // Clean up any legacy dark-mode class
    document.body.classList.remove('dark-mode');
    localStorage.removeItem('theme');

    const savedCollapse = localStorage.getItem('sidebar_collapsed');
    this.isSidebarCollapsed = savedCollapse === 'true';
  }

  get currentUser() {
    return this.authService.getUser();
  }

  get userAvatar(): string | null {
    return localStorage.getItem('profile_avatar') || this.currentUser?.avatar || null;
  }

  getUserInitial(): string {
    const name = this.currentUser?.name || 'User';
    return name.charAt(0).toUpperCase();
  }

  toggleSidebar(): void {
    if (window.innerWidth <= 900) {
      this.isSidebarOpen = !this.isSidebarOpen;
    } else {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
      localStorage.setItem('sidebar_collapsed', String(this.isSidebarCollapsed));
    }
  }

  closeSidebar(): void {
    this.isSidebarOpen = false;
  }

  toggleProfileMenu(): void {
    this.isProfileMenuOpen = !this.isProfileMenuOpen;
  }

  openProfile(): void {
    this.isProfileMenuOpen = false;
    this.router.navigate(['/profile']);
  }

  openChangePassword(): void {
    this.isProfileMenuOpen = false;
    this.router.navigate(['/change-password']);
  }

  logout(): void {
    this.isProfileMenuOpen = false;
    this.isSidebarOpen = false;

    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
