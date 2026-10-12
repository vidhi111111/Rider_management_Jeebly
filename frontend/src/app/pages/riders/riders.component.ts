
import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, finalize, takeUntil, timeout } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

type RiderStatus = 'active' | 'inactive';
type RiderAvailability = 'available' | 'busy' | 'unavailable';

interface Rider {
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
  isDeleting = false;

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
  showDeleteDialog = false;

  editingRiderId: number | null = null;
  selectedRider: Rider | null = null;
  deletingRider: Rider | null = null;

  selectedImageFile: File | null = null;
  imagePreviewUrl: string | null = null;
  currentImageUrl: string | null = null;

  riderForm: FormGroup;

  readonly statuses: { value: RiderStatus; label: string }[] = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' }
  ];

  readonly vehicles = ['Bike', 'Scooter', 'Car', 'Van'];

  readonly availabilityOptions: { value: RiderAvailability; label: string }[] = [
    { value: 'available', label: 'Available' },
    { value: 'busy', label: 'Busy' },
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
      status: ['active', Validators.required],
      availability: ['available', Validators.required],
      date: [this.today(), Validators.required]
    });

    this.riderForm.get('status')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(status => {
        const availability = this.riderForm.get('availability');

        if (status === 'inactive') {
          availability?.setValue('unavailable', { emitEvent: false });
          availability?.disable({ emitEvent: false });
        } else {
          availability?.enable({ emitEvent: false });

          if (availability?.value === 'unavailable') {
            availability.setValue('available', { emitEvent: false });
          }
        }
      });
  }

  ngOnInit(): void {
    this.searchInput$
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(value => {
        this.search = value.trim();
        this.currentPage = 1;
        this.loadRiders();
      });

    this.loadRiders();
  }

  ngOnDestroy(): void {
    this.requestId++;
    this.resetImageSelection();
    this.destroy$.next();
    this.destroy$.complete();
    this.searchInput$.complete();
  }

  private today(): string {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  }

  private unwrap<T>(response: any): T {
    if (response?.data?.data !== undefined) {
      return response.data.data as T;
    }

    if (response?.data !== undefined) {
      return response.data as T;
    }

    return response as T;
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

    if (this.search) {
      params = params.set('search', this.search);
    }

    if (this.selectedStatus) {
      params = params.set('status', this.selectedStatus);
    }

    if (this.selectedAvailability) {
      params = params.set('availability', this.selectedAvailability);
    }

    this.http.get<ApiResponse<RidersData>>(this.apiUrl, { params })
      .pipe(
        timeout(15000),
        takeUntil(this.destroy$),
        finalize(() => {
          if (request === this.requestId) {
            this.isLoading = false;
          }
        })
      )
      .subscribe({
        next: response => {
          if (request !== this.requestId) {
            return;
          }

          const data = this.unwrap<RidersData>(response);

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
          if (request !== this.requestId) {
            return;
          }

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
    this.resetImageSelection();
    this.editingRiderId = null;
    this.formError = '';

    this.riderForm.reset({
      name: '',
      mobile: '',
      email: '',
      vehicle: 'Bike',
      status: 'active',
      availability: 'available',
      date: this.today()
    });

    this.showRiderModal = true;
  }

  openEditRider(rider: Rider): void {
    this.closeActionMenu();
    this.resetImageSelection();
    this.editingRiderId = rider.id;
    this.currentImageUrl = rider.profile_image || null;
    this.formError = '';

    this.riderForm.reset({
      name: rider.name || '',
      mobile: rider.mobile || '',
      email: rider.email || '',
      vehicle: rider.vehicle || 'Bike',
      status: this.normalizeStatus(rider.status),
      availability: this.normalizeAvailability(rider.availability),
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
          const details = this.unwrap<Rider>(response);

          if (!details || details.id == null) {
            this.formError = 'Unable to refresh rider details.';
            return;
          }

          this.currentImageUrl = details.profile_image || null;

          this.riderForm.patchValue({
            name: details.name || '',
            mobile: details.mobile || '',
            email: details.email || '',
            vehicle: details.vehicle || 'Bike',
            status: this.normalizeStatus(details.status),
            availability: this.normalizeAvailability(details.availability),
            date: details.date || this.today()
          });
        },
        error: error => {
          this.formError = error.error?.message || 'Could not refresh rider details.';
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
    if (this.isSaving) {
      return;
    }

    this.showRiderModal = false;
    this.editingRiderId = null;
    this.formError = '';
    this.resetImageSelection();
    this.riderForm.markAsPristine();
    this.riderForm.markAsUntouched();
  }

  onImageSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    this.formError = '';

    if (!file) {
      return;
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

    if (!allowedTypes.includes(file.type)) {
      this.formError = 'Only JPG, PNG and WEBP images are allowed.';
      input.value = '';
      return;
    }

    if (file.size === 0 || file.size > 5 * 1024 * 1024) {
      this.formError = 'Image must not be empty or exceed 5 MB.';
      input.value = '';
      return;
    }

    this.selectedImageFile = file;
    this.imagePreviewUrl = null;

    const reader = new FileReader();

    reader.onload = () => {
      if (typeof reader.result === 'string') {
        this.imagePreviewUrl = reader.result;
      } else {
        this.formError = 'Unable to preview this image.';
      }
    };

    reader.onerror = () => {
      this.imagePreviewUrl = null;
      this.formError = 'Unable to read this image. Please select another file.';
    };

    reader.readAsDataURL(file);
  }

  private resetImageSelection(): void {
    this.selectedImageFile = null;
    this.imagePreviewUrl = null;
    this.currentImageUrl = null;
  }

  saveRider(): void {
    this.riderForm.markAllAsTouched();
    this.formError = '';
    this.successMessage = '';

    if (this.riderForm.invalid) {
      this.formError = 'Please correct the highlighted fields.';
      return;
    }

    if (this.isSaving) {
      return;
    }

    const value = this.riderForm.getRawValue();
    const status = this.normalizeStatus(value.status);
    const availability = status === 'inactive'
      ? 'unavailable'
      : this.normalizeAvailability(value.availability);

    const formData = new FormData();
    formData.append('name', String(value.name).trim());
    formData.append('mobile', String(value.mobile).trim());
    formData.append('email', String(value.email).trim().toLowerCase());
    formData.append('vehicle', String(value.vehicle));
    formData.append('status', status);
    formData.append('availability', availability);
    formData.append('date', String(value.date));

    if (this.selectedImageFile) {
      formData.append('profile_image', this.selectedImageFile, this.selectedImageFile.name);
    }

    this.isSaving = true;

    const request$ = this.editingRiderId !== null
      ? this.http.put<ApiResponse<Rider>>(`${this.apiUrl}/${this.editingRiderId}`, formData)
      : this.http.post<ApiResponse<Rider>>(this.apiUrl, formData);

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
          this.resetImageSelection();
          this.successMessage = response?.message || 'Rider saved successfully.';
          this.currentPage = 1;
          this.loadRiders();
        },
        error: error => {
          const errors = error.error?.errors as Record<string, string> | undefined;

          if (errors && Object.keys(errors).length) {
            this.formError = Object.entries(errors)
              .map(([field, message]) => `${field}: ${message}`)
              .join(' ');
          } else if (error.name === 'TimeoutError') {
            this.formError = 'The request timed out. Check Flask and try again.';
          } else {
            this.formError = error.error?.message || 'Unable to save rider. Check the API response.';
          }
        }
      });
  }

  viewRider(rider: Rider): void {
    this.selectedRider = { ...rider };
    this.showViewModal = true;
  }

  closeViewModal(): void {
    this.showViewModal = false;
    this.selectedRider = null;
  }

  requestDeleteRider(rider: Rider): void {
    this.closeActionMenu();
    this.deletingRider = rider;
    this.showDeleteDialog = true;
    this.errorMessage = '';
  }

  cancelDeleteRider(): void {
    if (this.isDeleting) {
      return;
    }

    this.showDeleteDialog = false;
    this.deletingRider = null;
  }

  confirmDeleteRider(): void {
    if (!this.deletingRider || this.isDeleting) {
      return;
    }

    const riderId = this.deletingRider.id;
    this.isDeleting = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.http.delete<ApiResponse<{ id: number }>>(`${this.apiUrl}/${riderId}`)
      .pipe(
        timeout(15000),
        takeUntil(this.destroy$),
        finalize(() => this.isDeleting = false)
      )
      .subscribe({
        next: response => {
          this.showDeleteDialog = false;
          this.deletingRider = null;
          this.successMessage = response?.message || 'Rider deleted successfully.';

          if (this.riders.length === 1 && this.currentPage > 1) {
            this.currentPage--;
          }

          if (this.selectedRider?.id === riderId) {
            this.closeViewModal();
          }

          this.loadRiders();
        },
        error: error => {
          this.errorMessage = error.error?.message || 'Unable to delete rider.';
        }
      });
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (!this.isSaving && !this.isDeleting) {
      this.closeRiderModal();
      this.closeViewModal();
      this.closeActionMenu();
      this.cancelDeleteRider();
    }
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;

    if (!target.closest('.rider-action-menu')) {
      this.closeActionMenu();
    }
  }

  normalizeStatus(status: string | null | undefined): RiderStatus {
    return (status || '').toLowerCase() === 'inactive' ? 'inactive' : 'active';
  }

  normalizeAvailability(availability: string | null | undefined): RiderAvailability {
    const value = (availability || '').toLowerCase();

    if (value === 'busy') {
      return 'busy';
    }

    if (value === 'unavailable') {
      return 'unavailable';
    }

    return 'available';
  }

  statusLabel(status: string): string {
    return this.normalizeStatus(status) === 'active' ? 'Active' : 'Inactive';
  }

  statusClass(status: string): string {
    return `status-${this.normalizeStatus(status)}`;
  }

  availabilityClass(availability: string): string {
    return `availability-${this.normalizeAvailability(availability)}`;
  }

  riderInitial(name: string): string {
    return (name || 'R').trim().charAt(0).toUpperCase();
  }
}
