import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { LanguageService } from '../../core/services/language.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginError = '';
  loginSuccess = '';
  isLoading = false;
  showPassword = false;

  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
    rememberMe: [false]
  });

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router,
    public readonly langService: LanguageService
  ) {}

  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }

  isInvalid(controlName: string): boolean {
    const control = this.loginForm.get(controlName);
    return !!control && control.invalid && (control.dirty || control.touched);
  }

  socialLogin(provider: string): void {
    this.loginError = '';
    this.loginSuccess = `${provider} sign-in integration will be enabled soon.`;
  }

  submit(): void {
    this.loginError = '';
    this.loginSuccess = '';

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    if (this.isLoading) {
      return;
    }

    const { email, password } = this.loginForm.value;

    this.isLoading = true;

    this.authService.login({
      email,
      password
    }).subscribe({
      next: (response) => {
        localStorage.setItem('access_token', response.token);
        localStorage.setItem('current_user', JSON.stringify(response.user));
        this.isLoading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.isLoading = false;

        if (error.status === 401) {
          this.loginError = 'Invalid email or password.';
        } else {
          this.loginError = error?.error?.message || 'Something went wrong. Please try again.';
        }
      }
    });
  }
}
