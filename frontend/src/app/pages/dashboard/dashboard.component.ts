import { CommonModule } from '@angular/common';
import {
  Component,
  OnDestroy,
  OnInit
} from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import {
  DashboardService,
  DashboardResponse,
  DashboardSummary,
  RiderSummary,
  RecentOrder,
  AvailableRider
} from '../../core/services/dashboard.service';
import { LanguageService } from '../../core/services/language.service';

export {
  DashboardSummary,
  RiderSummary,
  RecentOrder,
  AvailableRider,
  DashboardResponse
};

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  private readonly destroy$ = new Subject<void>();

  isLoading = false;
  errorMessage = '';

  totalOrders = 0;
  deliveredOrders = 0;
  cancelledOrders = 0;
  inProgressOrders = 0;

  totalOrdersPercentage = 0;
  deliveredPercentage = 0;
  cancelledPercentage = 0;
  inProgressPercentage = 0;

  availableRiders = 0;
  busyRiders = 0;
  activeRiders = 0;
  inactiveRiders = 0;

  recentOrders: RecentOrder[] = [];
  availableRiderList: AvailableRider[] = [];

  constructor(
    private readonly dashboardService: DashboardService,
    public readonly langService: LanguageService
  ) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.dashboardService
      .getDashboardData()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (!response.success) {
            this.isLoading = false;
            this.errorMessage =
              response.message || 'Unable to load dashboard data.';
            return;
          }

          const data = response.data;

          this.totalOrders = data.summary?.total_orders || 0;
          this.deliveredOrders = data.summary?.delivered_orders || 0;
          this.cancelledOrders = data.summary?.cancelled_orders || 0;
          this.inProgressOrders = data.summary?.in_progress_orders || 0;

          this.availableRiders = data.rider_summary?.available || 0;
          this.busyRiders = data.rider_summary?.busy || 0;
          this.activeRiders = data.rider_summary?.active || 0;
          this.inactiveRiders = data.rider_summary?.inactive || 0;

          this.recentOrders = data.recent_orders || [];
          this.availableRiderList = data.available_riders || [];

          this.calculatePercentages();
          this.isLoading = false;
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage =
            error?.error?.message ||
            'Unable to load dashboard data. Please try again.';
        }
      });
  }

  getBarHeight(percentage: number): number {
    if (this.totalOrders === 0) {
      return 12;
    }
    return Math.max(percentage, 12);
  }

  private calculatePercentages(): void {
    if (this.totalOrders > 0) {
      this.totalOrdersPercentage = 100;
      this.deliveredPercentage = Math.round(
        (this.deliveredOrders / this.totalOrders) * 100
      );
      this.inProgressPercentage = Math.round(
        (this.inProgressOrders / this.totalOrders) * 100
      );
      this.cancelledPercentage = Math.round(
        (this.cancelledOrders / this.totalOrders) * 100
      );
    } else {
      this.totalOrdersPercentage = 0;
      this.deliveredPercentage = 0;
      this.inProgressPercentage = 0;
      this.cancelledPercentage = 0;
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
