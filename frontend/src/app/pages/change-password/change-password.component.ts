import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
  AbstractControl,
  ValidationErrors
} from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { environment } from '../../../environments/environment';

function passwordMatchValidator(
  control: AbstractControl
): ValidationErrors | null {
  const password = control.get('new_password')?.value;
  const confirmPassword = control.get('confirm_password')?.value;

  if (!password || !confirmPassword) {
    return null;
  }

  return password === confirmPassword
    ? null
    : { passwordMismatch: true };
}

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent {
  passwordForm: FormGroup;

  private apiUrl = environment.apiUrl;

  changingPassword = false;
  successMessage = '';
  errorMessage = '';

  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    this.passwordForm = this.fb.group({
      current_password: ['', Validators.required],
      new_password: ['', [
        Validators.required,
        Validators.minLength(8)
      ]],
      confirm_password: ['', Validators.required]
    }, {
      validators: passwordMatchValidator
    });
  }

  changePassword(): void {
    this.successMessage = '';
    this.errorMessage = '';

    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    const {
      current_password,
      new_password,
      confirm_password
    } = this.passwordForm.value;

    if (current_password === new_password) {
      this.errorMessage =
        'New password must differ from your current password.';
      return;
    }

    if (new_password !== confirm_password) {
      this.errorMessage = 'New passwords do not match.';
      return;
    }

    this.changingPassword = true;

    this.http.put<any>(
      `${this.apiUrl}/change-password`,
      {
        current_password,
        new_password
      }
    ).subscribe({
      next: (response) => {
        this.successMessage =
          response?.message || 'Password changed successfully.';

        this.passwordForm.reset();
        this.changingPassword = false;
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.message || 'Unable to change password.';
        this.changingPassword = false;
      }
    });
  }
}
