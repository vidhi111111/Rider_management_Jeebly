import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  mobile: string;
  profile_image?: string | null;
  avatar?: string | null;
}

export interface ProfileResponse {
  success: boolean;
  message: string;
  data?: UserProfile;
  user?: UserProfile;
}

export interface UpdateProfilePayload {
  name?: string;
  mobile?: string;
  profile_image?: string | null;
  remove_photo?: boolean;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export interface SettingsResponse {
  success: boolean;
  message: string;
  data: {
    user_id: number;
    settings: {
      notifications: boolean;
      dark_mode: boolean;
    };
  };
}

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  getProfile(): Observable<ProfileResponse> {
    return this.http.get<ProfileResponse>(`${this.apiUrl}/profile`);
  }

  updateProfile(payload: UpdateProfilePayload | FormData): Observable<ProfileResponse> {
    return this.http.put<ProfileResponse>(`${this.apiUrl}/profile`, payload);
  }

  uploadAvatar(file: File): Observable<ProfileResponse> {
    const formData = new FormData();
    formData.append('profile_image', file);
    return this.http.post<ProfileResponse>(`${this.apiUrl}/profile/avatar`, formData);
  }

  removeAvatar(): Observable<ProfileResponse> {
    return this.http.delete<ProfileResponse>(`${this.apiUrl}/profile/avatar`);
  }

  changePassword(payload: ChangePasswordPayload): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/change-password`, payload);
  }

  getSettings(): Observable<SettingsResponse> {
    return this.http.get<SettingsResponse>(`${this.apiUrl}/settings`);
  }
}
