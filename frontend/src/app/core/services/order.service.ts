
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
}

export interface CreateOrderPayload {
  customer_name: string;
  mobile?: string;
  pickup?: string;
  delivery?: string;
  amount?: number | null;
  currency?: string;
}

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Get orders with server-side pagination and filters
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

    return this.http.get(`${this.apiUrl}/orders`, { params });
  }

  // Create an order in PostgreSQL
  createOrder(order: CreateOrderPayload): Observable<any> {
    return this.http.post(`${this.apiUrl}/orders`, order);
  }

  // Get riders available for assignment
  getAvailableRiders(): Observable<any> {
    return this.http.get(`${this.apiUrl}/riders/available`);
  }

  // Get one order by ID
  getOrderById(orderId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/orders/${orderId}`);
  }

  // Assign or unassign a rider
  assignRider(
    orderId: number,
    riderId: number | null
  ): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/orders/${orderId}/assign-rider`,
      { rider_id: riderId }
    );
  }
}
