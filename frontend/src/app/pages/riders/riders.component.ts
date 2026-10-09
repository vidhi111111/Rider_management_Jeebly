import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import {
  Component,
  OnDestroy,
  OnInit
} from '@angular/core';
import {
  FormControl,
  FormsModule,
  ReactiveFormsModule
} from '@angular/forms';

import { Subject, of } from 'rxjs';
import {
  catchError,
  debounceTime,
  distinctUntilChanged,
  finalize,
  switchMap,
  takeUntil
} from 'rxjs/operators';
import { environment } from '../../../environments/environment';


interface Rider {
  id: number;
  name: string;
  mobile: string | null;
  email: string | null;
  vehicle: string;
  status: string;
  availability: string;
  date: string;
  profile_image: string | null;
}

interface RidersResponse {
  success: boolean;
  message: string;
  data: {
    page: number;
    pageSize: number;
    riders: Rider[];
    totalPages: number;
    totalRecords: number;
  };
}

@Component({
  selector: 'app-riders',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './riders.component.html',
  styleUrls: ['./riders.component.css']
})
export class RidersComponent implements OnInit, OnDestroy {

  riders: Rider[] = [];

  isLoading = false;
  errorMessage = '';

  currentPage = 1;
  pageSize = 10;
  totalPages = 0;
  totalRecords = 0;

  search = '';
  searchControl = new FormControl('');

  selectedStatus = '';
  selectedAvailability = '';
  filtersExpanded = false;
  sortBy = 'id';
  sortOrder = 'asc';

  selectedRider: Rider | null = null;

  private readonly apiUrl = `${environment.apiUrl}/riders`;

  private readonly reload$ = new Subject<void>();
  private readonly destroy$ = new Subject<void>();

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {

    // Handle every list request through one stream.
    this.reload$
      .pipe(
        switchMap(() => this.loadRidersObservable()),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {

          if (!response) {
            return;
          }

          this.setRiderData(response);
        }
      });

    // Search automatically after the user stops typing.
    this.searchControl.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe((value) => {

        this.search = (value || '').trim();
        this.currentPage = 1;

        this.loadRiders();
      });

    this.loadRiders();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.reload$.complete();
  }

  private loadRidersObservable() {

    this.isLoading = true;
    this.errorMessage = '';

    let params = new HttpParams()
      .set('page', this.currentPage.toString())
      .set('pageSize', this.pageSize.toString())
      .set('sortBy', this.sortBy)
      .set('sortOrder', this.sortOrder);

    if (this.search) {
      params = params.set('search', this.search);
    }

    if (this.selectedStatus) {
      params = params.set(
        'status',
        this.selectedStatus
      );
    }

    if (this.selectedAvailability) {
      params = params.set(
        'availability',
        this.selectedAvailability
      );
    }

    return this.http
      .get<RidersResponse>(this.apiUrl, { params })
      .pipe(
        catchError(() => {

          this.errorMessage =
            'Unable to load riders. Please try again.';

          this.riders = [];
          this.totalPages = 0;
          this.totalRecords = 0;

          return of(null);
        }),
        finalize(() => {
          this.isLoading = false;
        })
      );
  }

  loadRiders(): void {
    this.reload$.next();
  }

  private setRiderData(
    response: RidersResponse
  ): void {

    const data = response.data;

    // Return to the last valid page if records have changed.
    if (
      data.totalPages > 0 &&
      this.currentPage > data.totalPages
    ) {
      this.currentPage = data.totalPages;
      this.loadRiders();
      return;
    }

    this.riders = data.riders || [];
    this.currentPage = data.page;
    this.pageSize = data.pageSize;
    this.totalPages = data.totalPages;
    this.totalRecords = data.totalRecords;

    if (this.totalPages === 0) {
      this.currentPage = 1;
    }
  }

  onSearch(): void {

    this.search =
      (this.searchControl.value || '').trim();

    this.currentPage = 1;

    // Avoid triggering a second delayed search request.
    this.searchControl.setValue(
      this.search,
      { emitEvent: false }
    );

    this.loadRiders();
  }

  onStatusChange(event: Event): void {

    const select =
      event.target as HTMLSelectElement;

    this.selectedStatus = select.value;
    this.currentPage = 1;

    this.loadRiders();
  }

  onAvailabilityChange(event: Event): void {

    const select =
      event.target as HTMLSelectElement;

    this.selectedAvailability = select.value;
    this.currentPage = 1;

    this.loadRiders();
  }

  onSortChange(event: Event): void {

    const select =
      event.target as HTMLSelectElement;

    this.sortBy = select.value;
    this.currentPage = 1;

    this.loadRiders();
  }

  toggleSortOrder(): void {

    this.sortOrder =
      this.sortOrder === 'asc' ? 'desc' : 'asc';

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

    this.searchControl.setValue(
      '',
      { emitEvent: false }
    );

    this.loadRiders();
  }

  goToPage(page: number): void {

    if (
      page < 1 ||
      page > this.totalPages ||
      page === this.currentPage
    ) {
      return;
    }

    this.currentPage = page;
    this.loadRiders();
  }

  previousPage(): void {

    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadRiders();
    }
  }

  nextPage(): void {

    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadRiders();
    }
  }

  changePageSize(event: Event): void {

    const select =
      event.target as HTMLSelectElement;

    this.pageSize = Number(select.value);
    this.currentPage = 1;

    this.loadRiders();
  }

  get pageNumbers(): number[] {

    return Array.from(
      { length: this.totalPages },
      (_, index) => index + 1
    );
  }

  viewRider(rider: Rider): void {
    this.selectedRider = rider;
  }

  closeRiderDetails(): void {
    this.selectedRider = null;
  }

}