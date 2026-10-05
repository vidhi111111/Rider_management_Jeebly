import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import {
  Component,
  OnDestroy,
  OnInit
} from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

interface DashboardSummary {
  total_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  in_progress_orders: number;
}

interface RiderSummary {
  available: number;
  on_order: number;
  scheduled_break: number;
  absent: number;
}

interface RecentOrder {
  id: number | string;
  status: string;
  customer: string;
}

interface AvailableRider {
  id?: number;
  name: string;
  status?: string;
}

interface DashboardResponse {
  success: boolean;
  message: string;
  data: {
    summary: DashboardSummary;
    rider_summary: RiderSummary;
    recent_orders: RecentOrder[];
    available_riders: AvailableRider[];
  };
}

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

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.http
      .get<DashboardResponse>(
        'https://rider-management-jeebly-backend.onrender.com/dashboard'
      )
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
    if (this.totalOrders === 0) {
      this.totalOrdersPercentage = 0;
      this.deliveredPercentage = 0;
      this.cancelledPercentage = 0;
      this.inProgressPercentage = 0;
      return;
    }

    this.totalOrdersPercentage = 100;

    this.deliveredPercentage = Math.round(
      (this.deliveredOrders / this.totalOrders) * 100
    );

    this.cancelledPercentage = Math.round(
      (this.cancelledOrders / this.totalOrders) * 100
    );

    this.inProgressPercentage = Math.round(
      (this.inProgressOrders / this.totalOrders) * 100
    );
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}