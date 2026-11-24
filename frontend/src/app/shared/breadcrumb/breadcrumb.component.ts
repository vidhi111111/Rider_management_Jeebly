import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';
import { LanguageService } from '../../core/services/language.service';

@Component({
  selector: 'app-breadcrumb',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './breadcrumb.component.html',
  styleUrls: ['./breadcrumb.component.css']
})
export class BreadcrumbComponent {
  breadcrumbs: { label: string; url: string }[] = [];

  private readonly routeLabels: { [key: string]: string } = {
    dashboard: 'Dashboard',
    riders: 'Riders',
    orders: 'Orders',
    profile: 'Account Profile',
    'change-password': 'Security & Password'
  };

  constructor(
    public readonly router: Router,
    public readonly langService: LanguageService
  ) {
    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd)
      )
      .subscribe(() => {
        this.generateBreadcrumbs();
      });

    this.generateBreadcrumbs();
  }

  private generateBreadcrumbs(): void {
    const url = this.router.url.split('?')[0];
    const segments = url.split('/').filter(segment => segment);

    this.breadcrumbs = [
      {
        label: 'Home',
        url: '/dashboard'
      }
    ];

    let currentUrl = '';

    segments.forEach(segment => {
      currentUrl += `/${segment}`;
      this.breadcrumbs.push({
        label: this.routeLabels[segment] || segment,
        url: currentUrl
      });
    });
  }
}
