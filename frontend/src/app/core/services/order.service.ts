
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface OrderFilters {
  page: number;
  pageSize: number;
  search?: string;
  status?: string;
  rider_id?: string;
  order_date?: string;
  sortBy?: string;
}

export interface CreateOrderPayload {
  customer_name: string;
  mobile?: string;
  pickup?: string;
  delivery?: string;
  amount?: number | null;
  currency?: string;
}

@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getOrders(filters: OrderFilters): Observable<any> {
    let params = new HttpParams()
      .set('page', String(filters.page))
      .set('pageSize', String(filters.pageSize));

    if (filters.search?.trim()) {
      params = params.set('search', filters.search.trim());
    }
    if (filters.status) {
      params = params.set('status', filters.status);
    }
    if (filters.rider_id) {
      params = params.set('rider_id', filters.rider_id);
    }
    if (filters.order_date) {
      params = params.set('order_date', filters.order_date);
    }
    if (filters.sortBy) {
      params = params.set('sortBy', filters.sortBy);
    }

    return this.http.get(`${this.apiUrl}/orders`, { params });
  }

  createOrder(order: CreateOrderPayload): Observable<any> {
    return this.http.post(`${this.apiUrl}/orders`, order);
  }

  getAvailableRiders(): Observable<any> {
    return this.http.get(`${this.apiUrl}/riders/available`);
  }

  getRiders(): Observable<any> {
    return this.http.get(`${this.apiUrl}/riders?page=1&pageSize=100`);
  }

  getOrderById(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/orders/${id}`);
  }

  assignRider(orderId: number, riderId: number | null): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/orders/${orderId}/assign-rider`,
      { rider_id: riderId }
    );
  }

  updateOrderStatus(orderId: number, status: string): Observable<any> {
    return this.http.patch(
      `${this.apiUrl}/orders/${orderId}/status`,
      { status }
    );
  }

  updateOrder(
    orderId: number,
    payload: Partial<CreateOrderPayload>
  ): Observable<any> {
    return this.http.put(`${this.apiUrl}/orders/${orderId}`, payload);
  }

  deleteOrder(orderId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/orders/${orderId}`);
  }
}
