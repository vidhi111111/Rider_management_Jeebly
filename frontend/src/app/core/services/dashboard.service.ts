import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface DashboardSummary {
  total_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  in_progress_orders: number;
}

export interface RiderSummary {
  available: number;
  on_order: number;
  scheduled_break: number;
  absent: number;
}

export interface RecentOrder {
  id: number | string;
  status: string;
  customer: string;
}

export interface AvailableRider {
  id?: number;
  name: string;
  status?: string;
}

export interface DashboardResponse {
  success: boolean;
  message: string;
  data: {
    summary: DashboardSummary;
    rider_summary: RiderSummary;
    recent_orders: RecentOrder[];
    available_riders: AvailableRider[];
  };
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private readonly apiUrl = `${environment.apiUrl}/dashboard`;

  constructor(private readonly http: HttpClient) {}

  getDashboardData(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(this.apiUrl);
  }
}
