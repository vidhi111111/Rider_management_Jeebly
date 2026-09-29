import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationEnd, Router, RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';

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
    profile: 'Profile',
    settings: 'Settings'
  };

 constructor(public readonly router: Router) {
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

    this.breadcrumbs = [];
    let currentUrl = '';

    segments.forEach(segment => {
      currentUrl += `/${segment}`;

      this.breadcrumbs.push({
        label: this.routeLabels[segment] || this.formatLabel(segment),
        url: currentUrl
      });
    });
  }

  private formatLabel(segment: string): string {
    return segment
      .replace(/-/g, ' ')
      .replace(/\b\w/g, character => character.toUpperCase());
  }
}