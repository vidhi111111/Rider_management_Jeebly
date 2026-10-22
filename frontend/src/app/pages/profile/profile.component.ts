import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule
} from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;

  private apiUrl = environment.apiUrl;

  loadingProfile = false;
  updatingProfile = false;

  successMessage = '';
  errorMessage = '';

  userEmail = '';
  userName = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.profileForm = this.fb.group({
      name: ['', [
        Validators.required,
        Validators.maxLength(100)
      ]],
      mobile: ['', [
        Validators.required,
        Validators.pattern(/^[0-9]{10}$/)
      ]]
    });

    this.loadProfile();
  }

  loadProfile(): void {
    this.loadingProfile = true;
    this.clearMessages();

    this.http.get<any>(`${this.apiUrl}/profile`).subscribe({
      next: (response) => {
        const user = response?.user ?? response?.data ?? response;

        this.profileForm.patchValue({
          name: user?.name || '',
          mobile: user?.mobile || ''
        });

        this.userName = user?.name || '';
        this.userEmail = user?.email || '';

        this.updateStoredUser({
          name: this.userName,
          email: this.userEmail,
          mobile: user?.mobile || ''
        });

        this.loadingProfile = false;
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.message || 'Unable to load profile.';
        this.loadingProfile = false;
      }
    });
  }

  updateProfile(): void {
    this.clearMessages();

    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.updatingProfile = true;

    const payload = {
      name: String(this.profileForm.value.name || '').trim(),
      mobile: String(this.profileForm.value.mobile || '').trim()
    };

    this.http.put<any>(
      `${this.apiUrl}/profile`,
      payload
    ).subscribe({
      next: (response) => {
        const responseUser =
          response?.user ?? response?.data ?? response;

        const updatedName = responseUser?.name || payload.name;
        const updatedMobile =
          responseUser?.mobile || payload.mobile;

        this.userName = updatedName;
        this.userEmail = responseUser?.email || this.userEmail;

        this.profileForm.patchValue({
          name: updatedName,
          mobile: updatedMobile
        });

        this.updateStoredUser({
          ...responseUser,
          name: updatedName,
          email: this.userEmail,
          mobile: updatedMobile
        });

        this.successMessage =
          response?.message || 'Profile updated successfully.';

        this.updatingProfile = false;
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.message || 'Unable to update profile.';
        this.updatingProfile = false;
      }
    });
  }

  private updateStoredUser(updatedFields: any): void {
    try {
      const storageKeys = ['current_user', 'user'];

      for (const key of storageKeys) {
        const storedValue = localStorage.getItem(key);

        if (!storedValue) {
          continue;
        }

        const storedUser = JSON.parse(storedValue);

        if (
          storedUser &&
          typeof storedUser === 'object' &&
          !Array.isArray(storedUser)
        ) {
          localStorage.setItem(
            key,
            JSON.stringify({
              ...storedUser,
              ...updatedFields
            })
          );
        }
      }
    } catch (error) {
      console.error('Unable to update stored user information.', error);
    }
  }

  getInitial(): string {
    return (this.userName || 'U').charAt(0).toUpperCase();
  }

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }
}