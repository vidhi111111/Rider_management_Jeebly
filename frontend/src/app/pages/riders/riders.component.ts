
import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subject, of } from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, finalize, takeUntil, timeout } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

type RiderStatus = 'assigned' | 'free' | 'waiting' | 'reject' | 'on_route';

interface Rider {
  id: number;
  name: string;
  mobile: string;
  email: string;
  vehicle: string;
  status: string;
  availability: string;
  date: string;
  profile_image: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: Record<string, string>;
}

interface RidersData {
  riders: Rider[];
  page: number;
  pageSize: number;
  totalPages: number;
  totalRecords: number;
}

@Component({
  selector: 'app-riders',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './riders.component.html',
  styleUrls: ['./riders.component.css']
})
export class RidersComponent implements OnInit, OnDestroy {
  riders: Rider[] = [];
  isLoading = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';
  formError = '';
  currentPage = 1;
  pageSize = 10;
  totalPages = 0;
  totalRecords = 0;
  search = '';
  selectedStatus = '';
  selectedAvailability = '';
  sortBy = 'id';
  sortOrder: 'asc' | 'desc' = 'asc';
  filtersExpanded = false;
  openActionMenuId: number | null = null;
  showRiderModal = false;
  showViewModal = false;
  editingRiderId: number | null = null;
  selectedRider: Rider | null = null;
  riderForm: FormGroup;

  readonly statuses: { value: RiderStatus; label: string }[] = [
    { value: 'assigned', label: 'Assigned' },
    { value: 'free', label: 'Free' },
    { value: 'waiting', label: 'Waiting' },
    { value: 'reject', label: 'Reject' },
    { value: 'on_route', label: 'On Route' }
  ];

  readonly vehicles = ['Bike', 'Scooter', 'Car', 'Van'];
  readonly availabilityOptions = [
    { value: 'available', label: 'Available' },
    { value: 'unavailable', label: 'Unavailable' }
  ];

  private readonly apiUrl = `${environment.apiUrl}/riders`;
  private readonly destroy$ = new Subject<void>();
  private readonly searchInput$ = new Subject<string>();
  private requestId = 0;

  constructor(
    private readonly http: HttpClient,
    private readonly fb: FormBuilder
  ) {
    this.riderForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]],
      mobile: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]],
      email: ['', [Validators.required, Validators.email, Validators.maxLength(120)]],
      vehicle: ['Bike', Validators.required],
      status: ['free', Validators.required],
      availability: ['available', Validators.required],
      date: [this.today(), Validators.required]
    });
  }

  ngOnInit(): void {
    this.searchInput$
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe(value => {
        this.search = value.trim();
        this.currentPage = 1;
        this.loadRiders();
      });

    this.loadRiders();
  }

  ngOnDestroy(): void {
    this.requestId++;
    this.destroy$.next();
    this.destroy$.complete();
    this.searchInput$.complete();
  }

  private today(): string {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  }

  get f() {
    return this.riderForm.controls;
  }

  get pageNumbers(): number[] {
    return Array.from({ length: this.totalPages }, (_, index) => index + 1);
  }

  get firstRecord(): number {
    return this.totalRecords === 0 ? 0 : (this.currentPage - 1) * this.pageSize + 1;
  }

  get lastRecord(): number {
    return Math.min(this.currentPage * this.pageSize, this.totalRecords);
  }

  onSearch(value: string): void {
    this.searchInput$.next(value);
  }

  onStatusChange(value: string): void {
    this.selectedStatus = value;
    this.currentPage = 1;
    this.loadRiders();
  }

  onAvailabilityChange(value: string): void {
    this.selectedAvailability = value;
    this.currentPage = 1;
    this.loadRiders();
  }

  onSortChange(value: string): void {
    this.sortBy = value;
    this.currentPage = 1;
    this.loadRiders();
  }

  toggleSortOrder(): void {
    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    this.currentPage = 1;
    this.loadRiders();
  }

  clearFilters(): void {
    this.search = '';
    this.selectedStatus = '';
    this.selectedAvailability = '';
    this.sortBy = 'id';
    this.sortOrder = 'asc';
    this.currentPage = 1;
    this.loadRiders();
  }

  changePageSize(value: string): void {
    this.pageSize = Number(value) || 10;
    this.currentPage = 1;
    this.loadRiders();
  }

  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }
    this.currentPage = page;
    this.loadRiders();
  }

  previousPage(): void {
    this.goToPage(this.currentPage - 1);
  }

  nextPage(): void {
    this.goToPage(this.currentPage + 1);
  }

  loadRiders(): void {
    const request = ++this.requestId;
    this.isLoading = true;
    this.errorMessage = '';

    let params = new HttpParams()
      .set('page', String(this.currentPage))
      .set('pageSize', String(this.pageSize))
      .set('sortBy', this.sortBy)
      .set('sortOrder', this.sortOrder);

    if (this.search) params = params.set('search', this.search);
    if (this.selectedStatus) params = params.set('status', this.selectedStatus);
    if (this.selectedAvailability) params = params.set('availability', this.selectedAvailability);

    this.http.get<ApiResponse<RidersData>>(this.apiUrl, { params })
      .pipe(
        timeout(15000),
        takeUntil(this.destroy$),
        finalize(() => {
          if (request === this.requestId) this.isLoading = false;
        })
      )
      .subscribe({
        next: response => {
          if (request !== this.requestId) return;

          const data = response?.data;
          if (!data || !Array.isArray(data.riders)) {
            this.riders = [];
            this.totalRecords = 0;
            this.totalPages = 0;
            this.errorMessage = 'Unexpected response from the riders API.';
            return;
          }

          this.riders = data.riders;
          this.totalRecords = Number(data.totalRecords) || 0;
          this.totalPages = Number(data.totalPages) || 0;
          this.currentPage = Number(data.page) || 1;
          this.pageSize = Number(data.pageSize) || this.pageSize;
        },
        error: error => {
          if (request !== this.requestId) return;
          this.errorMessage = error.name === 'TimeoutError'
            ? 'The riders request timed out. Check whether Flask is responding.'
            : error.error?.message || 'Unable to load riders. Check your login and backend.';
        }
      });
  }

  toggleActionMenu(riderId: number): void {
    this.openActionMenuId = this.openActionMenuId === riderId ? null : riderId;
  }

  closeActionMenu(): void {
    this.openActionMenuId = null;
  }

  openAddRider(): void {
    this.closeActionMenu();
    this.editingRiderId = null;
    this.formError = '';
    this.riderForm.reset({
      name: '',
      mobile: '',
      email: '',
      vehicle: 'Bike',
      status: 'free',
      availability: 'available',
      date: this.today()
    });
    this.showRiderModal = true;
  }

  openEditRider(rider: Rider): void {
    this.closeActionMenu();
    this.editingRiderId = rider.id;
    this.formError = '';
    this.riderForm.reset({
      name: rider.name || '',
      mobile: rider.mobile || '',
      email: rider.email || '',
      vehicle: rider.vehicle || 'Bike',
      status: this.normalizeStatus(rider.status),
      availability: (rider.availability || 'available').toLowerCase(),
      date: rider.date || this.today()
    });
    this.showRiderModal = true;
    this.isLoading = true;

    this.http.get<ApiResponse<Rider>>(`${this.apiUrl}/${rider.id}`)
      .pipe(
        timeout(15000),
        takeUntil(this.destroy$),
        finalize(() => this.isLoading = false)
      )
      .subscribe({
        next: response => {
          const details = response?.data as Rider;
          if (!details || details.id == null) {
            this.formError = 'Unable to refresh rider details. The existing row data is still available.';
            return;
          }

          this.riderForm.patchValue({
            name: details.name || '',
            mobile: details.mobile || '',
            email: details.email || '',
            vehicle: details.vehicle || 'Bike',
            status: this.normalizeStatus(details.status),
            availability: (details.availability || 'available').toLowerCase(),
            date: details.date || this.today()
          });
        },
        error: error => {
          this.formError = error.error?.message || 'Could not refresh rider details. You can still edit the loaded row data.';
        }
      });
  }

  openRiderView(rider: Rider): void {
    this.closeActionMenu();
    this.viewRider(rider);
  }

  openRiderEdit(rider: Rider): void {
    this.openEditRider(rider);
  }

  closeRiderModal(): void {
    if (this.isSaving) return;
    this.showRiderModal = false;
    this.editingRiderId = null;
    this.formError = '';
    this.riderForm.markAsPristine();
    this.riderForm.markAsUntouched();
  }

  saveRider(): void {
    this.riderForm.markAllAsTouched();
    this.formError = '';
    this.successMessage = '';

    if (this.riderForm.invalid) {
      this.formError = 'Please correct the highlighted fields.';
      return;
    }

    if (this.isSaving) return;

    const value = this.riderForm.getRawValue();
    const payload = {
      name: String(value.name).trim(),
      mobile: String(value.mobile).trim(),
      email: String(value.email).trim().toLowerCase(),
      vehicle: value.vehicle,
      status: value.status,
      availability: value.availability,
      date: value.date
    };

    this.isSaving = true;

    const request$ = this.editingRiderId !== null
      ? this.http.put<ApiResponse<Rider>>(`${this.apiUrl}/${this.editingRiderId}`, payload)
      : this.http.post<ApiResponse<Rider>>(this.apiUrl, payload);

    request$
      .pipe(
        timeout(15000),
        takeUntil(this.destroy$),
        finalize(() => this.isSaving = false)
      )
      .subscribe({
        next: response => {
          if (response?.success === false) {
            this.formError = response.message || 'Unable to save rider.';
            return;
          }

          this.showRiderModal = false;
          this.editingRiderId = null;
          this.successMessage = 'Rider saved successfully.';
          this.currentPage = 1;
          this.loadRiders();
        },
        error: error => {
          const errors = error.error?.errors as Record<string, string> | undefined;
          if (errors && Object.keys(errors).length) {
            this.formError = Object.entries(errors).map(([field, message]) => `${field}: ${message}`).join(' ');
          } else if (error.name === 'TimeoutError') {
            this.formError = 'The request timed out. Check Flask and try again.';
          } else {
            this.formError = error.error?.message || error.error?.error || 'Unable to save rider. Please check the API response.';
          }
        }
      });
  }

  viewRider(rider: Rider): void {
    this.selectedRider = rider;
    this.showViewModal = true;

    this.http.get<ApiResponse<Rider>>(`${this.apiUrl}/${rider.id}`)
      .pipe(
        timeout(15000),
        takeUntil(this.destroy$),
        catchError(error => {
          this.errorMessage = error.error?.message || 'Unable to refresh rider details. Showing available row data.';
          return of(null);
        })
      )
      .subscribe(response => {
        if (response?.data) this.selectedRider = response.data as Rider;
      });
  }

  closeViewModal(): void {
    this.showViewModal = false;
    this.selectedRider = null;
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (!this.isSaving) {
      this.closeRiderModal();
      this.closeViewModal();
      this.closeActionMenu();
    }
  }

  @HostListener('document:click')
  onDocumentClick(): void {
    this.closeActionMenu();
  }

  normalizeStatus(status: string | null | undefined): RiderStatus {
    const value = (status || '').toLowerCase().replace(/[\s-]+/g, '_');
    const aliases: Record<string, RiderStatus> = {
      available: 'free',
      free: 'free',
      on_order: 'assigned',
      assigned: 'assigned',
      scheduled_break: 'waiting',
      waiting: 'waiting',
      absent: 'reject',
      reject: 'reject',
      on_route: 'on_route'
    };
    return aliases[value] || 'free';
  }

  statusLabel(status: string): string {
    const normalized = this.normalizeStatus(status);
    return this.statuses.find(item => item.value === normalized)?.label || status;
  }

  statusClass(status: string): string {
    return `status-${this.normalizeStatus(status)}`;
  }

  availabilityClass(availability: string): string {
    return (availability || '').toLowerCase() === 'available'
      ? 'availability-available'
      : 'availability-unavailable';
  }

  riderInitial(name: string): string {
    return (name || 'R').trim().charAt(0).toUpperCase();
  }
}
