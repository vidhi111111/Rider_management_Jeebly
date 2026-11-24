import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { LanguageService } from '../../core/services/language.service';

function passwordValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.value;

  if (!password) {
    return null;
  }

  const errors: ValidationErrors = {};

  if (!/[A-Z]/.test(password)) {
    errors['uppercase'] = true;
  }

  if (!/[a-z]/.test(password)) {
    errors['lowercase'] = true;
  }

  if (!/[0-9]/.test(password)) {
    errors['number'] = true;
  }

  if (!/[^A-Za-z0-9]/.test(password)) {
    errors['special'] = true;
  }

  if (/\s/.test(password)) {
    errors['space'] = true;
  }

  return Object.keys(errors).length ? errors : null;
}

function passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.get('password')?.value;
  const confirmPassword = control.get('confirmPassword')?.value;
  if (!password || !confirmPassword) {
    return null;
  }
  return password === confirmPassword ? null : { passwordMismatch: true };
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  isSubmitting = false;
  successMessage = '';
  errorMessage = '';
  showPassword = false;
  showConfirmPassword = false;

  registerForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    mobile: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]],
    password: ['', [
      Validators.required,
      Validators.minLength(8),
      passwordValidator
    ]],
    confirmPassword: ['', [Validators.required]]
  }, { validators: passwordMatchValidator });

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router,
    public readonly langService: LanguageService
  ) {}

  get name() {
    return this.registerForm.get('name');
  }

  get email() {
    return this.registerForm.get('email');
  }

  get mobile() {
    return this.registerForm.get('mobile');
  }

  get password() {
    return this.registerForm.get('password');
  }

  get confirmPassword() {
    return this.registerForm.get('confirmPassword');
  }

  get passwordErrorMessage(): string {
    const control = this.password;
    if (!control || !control.invalid || (!control.dirty && !control.touched)) {
      return '';
    }

    if (control.hasError('required')) {
      return this.langService.t('passwordRequired');
    }

    if (this.langService.isArabic) {
      const arErrors: string[] = [];
      if (control.hasError('minlength')) arErrors.push('8 أحرف على الأقل');
      if (control.hasError('uppercase')) arErrors.push('حرف كبير واحد');
      if (control.hasError('lowercase')) arErrors.push('حرف صغير واحد');
      if (control.hasError('number')) arErrors.push('رقم واحد');
      if (control.hasError('special')) arErrors.push('رمز خاص');
      if (control.hasError('space')) arErrors.push('بدون مسافات');
      return arErrors.join('، ');
    }

    const errors: string[] = [];

    if (control.hasError('minlength')) {
      errors.push('At least 8 characters');
    }

    if (control.hasError('uppercase')) {
      errors.push('At least 1 uppercase letter');
    }

    if (control.hasError('lowercase')) {
      errors.push('At least 1 lowercase letter');
    }

    if (control.hasError('number')) {
      errors.push('At least 1 number');
    }

    if (control.hasError('special')) {
      errors.push('At least 1 special character');
    }

    if (control.hasError('space')) {
      errors.push('Must not contain spaces');
    }

    return errors.join(', ');
  }

  isInvalid(controlName: string): boolean {
    const control = this.registerForm.get(controlName);
    return !!control && control.invalid && (control.dirty || control.touched);
  }

  socialLogin(provider: string): void {
    this.errorMessage = '';
    this.successMessage = `${provider} sign-in integration will be enabled soon.`;
  }

  submit(): void {
    this.successMessage = '';
    this.errorMessage = '';

    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;

    const formValues = this.registerForm.value;
    const name = formValues.name;
    const email = formValues.email;
    const password = formValues.password;
    const mobile = formValues.mobile.trim();

    this.authService.register({
      name,
      email,
      mobile,
      password
    }).subscribe({
      next: (response) => {
        this.isSubmitting = false;
        this.successMessage = response.message;
        this.registerForm.reset();
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 1500);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = error?.error?.message || 'Unable to register';
      }
    });
  }
}
