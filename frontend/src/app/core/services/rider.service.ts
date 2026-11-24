import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export type RiderStatus = 'active' | 'inactive';
export type RiderAvailability = 'available' | 'busy' | 'unavailable';

export interface Rider {
  id: number;
  name: string;
  mobile: string;
  email: string;
  vehicle: string;
  status: RiderStatus | string;
  availability: RiderAvailability | string;
  date: string;
  profile_image: string | null;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: Record<string, string>;
}

export interface RidersData {
  riders: Rider[];
  page: number;
  pageSize: number;
  totalPages: number;
  totalRecords: number;
}

export interface RiderQueryFilters {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: string;
  availability?: string;
  date_from?: string;
  date_to?: string;
  created_from?: string;
  created_to?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

@Injectable({
  providedIn: 'root'
})
export class RiderService {
  private readonly apiUrl = `${environment.apiUrl}/riders`;

  constructor(private readonly http: HttpClient) {}

  getRiders(filters: RiderQueryFilters = {}): Observable<ApiResponse<RidersData>> {
    let params = new HttpParams()
      .set('page', String(filters.page || 1))
      .set('pageSize', String(filters.pageSize || 10));

    if (filters.search?.trim()) {
      params = params.set('search', filters.search.trim());
    }
    if (filters.status) {
      params = params.set('status', filters.status);
    }
    if (filters.availability) {
      params = params.set('availability', filters.availability);
    }
    if (filters.date_from) {
      params = params.set('date_from', filters.date_from);
    }
    if (filters.date_to) {
      params = params.set('date_to', filters.date_to);
    }
    if (filters.created_from) {
      params = params.set('created_from', filters.created_from);
    }
    if (filters.created_to) {
      params = params.set('created_to', filters.created_to);
    }
    if (filters.sortBy) {
      params = params.set('sortBy', filters.sortBy);
    }
    if (filters.sortOrder) {
      params = params.set('sortOrder', filters.sortOrder);
    }

    return this.http.get<ApiResponse<RidersData>>(this.apiUrl, { params });
  }

  getAvailableRiders(): Observable<ApiResponse<{ riders: Rider[] }>> {
    return this.http.get<ApiResponse<{ riders: Rider[] }>>(`${this.apiUrl}/available`);
  }

  getRiderById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`);
  }

  createRider(payload: FormData | Record<string, any>): Observable<ApiResponse<Rider>> {
    return this.http.post<ApiResponse<Rider>>(this.apiUrl, payload);
  }

  updateRider(id: number, payload: FormData | Record<string, any>): Observable<ApiResponse<Rider>> {
    return this.http.put<ApiResponse<Rider>>(`${this.apiUrl}/${id}`, payload);
  }

  deleteRider(id: number): Observable<ApiResponse<{ id: number }>> {
    return this.http.delete<ApiResponse<{ id: number }>>(`${this.apiUrl}/${id}`);
  }
}
