import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { BreadcrumbComponent } from '../shared/breadcrumb/breadcrumb.component';
import { AuthService } from '../core/services/auth.service';

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
  isDarkMode = false;
  isSidebarOpen = false;
  isProfileMenuOpen = false;

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router
  ) {}

  ngOnInit(): void {
    const savedTheme = localStorage.getItem('theme');

    this.isDarkMode = savedTheme === 'dark';

    document.body.classList.toggle('dark-mode', this.isDarkMode);
  }

  get currentUser() {
    return this.authService.getUser();
  }

  getUserInitial(): string {
    const name = this.currentUser?.name || 'User';
    return name.charAt(0).toUpperCase();
  }

  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
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

  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;

    document.body.classList.toggle('dark-mode', this.isDarkMode);

    localStorage.setItem(
      'theme',
      this.isDarkMode ? 'dark' : 'light'
    );
  }

  logout(): void {
    this.isProfileMenuOpen = false;
    this.isSidebarOpen = false;

    this.authService.logout();

    localStorage.removeItem('theme');
    document.body.classList.remove('dark-mode');

    this.router.navigate(['/login']);
  }
}