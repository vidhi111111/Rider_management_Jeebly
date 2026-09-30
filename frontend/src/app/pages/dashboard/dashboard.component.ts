import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface RecentOrder {
  id: string;
  status: string;
  customer: string;
}

interface AvailableRider {
  name: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  isLoading = true;
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

    this.http.get<any>('https://rider-management-jeebly-backend.onrender.com/dashboard').subscribe({
      next: (response) => {
        const data = response.data || {};

        this.totalOrders = data.summary?.total_orders || 0;
        this.deliveredOrders = data.summary?.delivered_orders || 0;
        this.cancelledOrders = data.summary?.cancelled_orders || 0;
        this.inProgressOrders = data.summary?.in_progress_orders || 0;

        this.availableRiders = data.rider_summary?.available || 0;
        this.onOrderRiders = data.rider_summary?.on_order || 0;
        this.scheduledBreakRiders = data.rider_summary?.scheduled_break || 0;
        this.absentRiders = data.rider_summary?.absent || 0;

        this.recentOrders = data.recent_orders || [];
        this.availableRiderList = data.available_riders || [];

        this.calculatePercentages();
        this.isLoading = false;
      },
      error: () => {
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
}