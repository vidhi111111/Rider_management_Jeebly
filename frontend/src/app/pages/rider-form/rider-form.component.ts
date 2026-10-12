
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-rider-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './rider-form.component.html',
  styleUrls: ['./rider-form.component.css']
})
export class RiderFormComponent implements OnInit {
  riderId: number | null = null;
  isEditMode = false;
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';

  private readonly apiUrl = `${environment.apiUrl}/riders`;

  riderForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    mobile: ['', [
      Validators.required,
      Validators.pattern(/^[0-9]{10,15}$/)
    ]],
    email: ['', [Validators.required, Validators.email]],
    vehicle: ['Bike', Validators.required],
    status: ['Available', Validators.required],
    availability: ['Available', Validators.required],
    date: [new Date().toISOString().slice(0, 10), Validators.required]
  });

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    if (id) {
      this.riderId = Number(id);
      this.isEditMode = true;
      this.loadRider();
    }
  }

  loadRider(): void {
    if (!this.riderId) return;

    this.isLoading = true;
    this.errorMessage = '';

    this.http.get<any>(`${this.apiUrl}/${this.riderId}`).subscribe({
      next: (response) => {
        const rider = response?.data?.rider
          ?? response?.data
          ?? response?.rider
          ?? response;

        if (!rider || !rider.id) {
          this.errorMessage = 'Rider data not found.';
          this.isLoading = false;
          return;
        }

        this.riderForm.patchValue({
          name: rider.name ?? '',
          mobile: rider.mobile ?? '',
          email: rider.email ?? '',
          vehicle: rider.vehicle ?? 'Bike',
          status: rider.status ?? 'Available',
          availability: rider.availability ?? 'Available',
          date: rider.date ? String(rider.date).slice(0, 10) : ''
        });

        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage =
          error.error?.message || 'Unable to load rider details.';
        this.isLoading = false;
      }
    });
  }

  saveRider(): void {
    if (this.riderForm.invalid || this.isSaving) {
      this.riderForm.markAllAsTouched();
      return;
    }

    this.isSaving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const payload = this.riderForm.getRawValue();

    const request = this.isEditMode && this.riderId
      ? this.http.put<any>(`${this.apiUrl}/${this.riderId}`, payload)
      : this.http.post<any>(this.apiUrl, payload);

    request.subscribe({
      next: (response) => {
        if (response?.success === false) {
          this.errorMessage = response.message || 'Unable to save rider.';
          this.isSaving = false;
          return;
        }

        this.successMessage = this.isEditMode
          ? 'Rider updated successfully!'
          : 'Rider added successfully!';

        this.isSaving = false;
        this.router.navigate(['/riders']);
      },
      error: (error) => {
        this.errorMessage =
          error.error?.message || 'Unable to save rider. Please try again.';
        this.isSaving = false;
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/riders']);
  }

  get f() {
    return this.riderForm.controls;
  }
}
