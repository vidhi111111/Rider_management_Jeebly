
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

@Injectable({
  providedIn: 'root'
})
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

    return this.http.get(`${this.apiUrl}/orders`, { params });
  }

  getAvailableRiders(): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/riders/available`
    );
  }

  getOrderById(orderId: number): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/orders/${orderId}`
    );
  }

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
