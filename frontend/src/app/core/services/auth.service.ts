import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RegisterRequest {
  name: string;
  email: string;
  mobile: string;
  password: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  data?: {
    name: string;
    email: string;
    mobile: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  token: string;
  user: {
    id: number;
    name: string;
    email: string;
    mobile: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly apiUrl = 'https://rider-management-jeebly-backend.onrender.com';

  constructor(private readonly http: HttpClient) {}

  register(payload: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(
      `${this.apiUrl}/register`,
      payload
    );
  }

  login(payload: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/login`,
      payload
    );
  }
  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }
  getUser(): any {
    const user = localStorage.getItem('current_user');

    if (!user) {
      return null;
    }
    return JSON.parse(user);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
  }
}