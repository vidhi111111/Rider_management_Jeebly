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
  onOrderRiders = 0;
  scheduledBreakRiders = 0;
  absentRiders = 0;

  recentOrders: RecentOrder[] = [];
  availableRiderList: AvailableRider[] = [];

  constructor(private readonly dashboardService: DashboardService) {}

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
          this.onOrderRiders = data.rider_summary?.on_order || 0;
          this.scheduledBreakRiders =
            data.rider_summary?.scheduled_break || 0;
          this.absentRiders = data.rider_summary?.absent || 0;

          this.recentOrders = data.recent_orders || [];
          this.availableRiderList = data.available_riders || [];

          this.calculatePercentages();

          this.isLoading = false;
        },
        error: (error) => {
          console.error('Dashboard API error:', error);
          this.isLoading = false;
          this.errorMessage = 'Unable to load dashboard data.';
        }
      });
  }

  private calculatePercentages(): void {
    const total = this.totalOrders || 1;

    this.totalOrdersPercentage = Math.round(
      (this.totalOrders / total) * 100
    );
    this.deliveredPercentage = Math.round(
      (this.deliveredOrders / total) * 100
    );
    this.cancelledPercentage = Math.round(
      (this.cancelledOrders / total) * 100
    );
    this.inProgressPercentage = Math.round(
      (this.inProgressOrders / total) * 100
    );
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
