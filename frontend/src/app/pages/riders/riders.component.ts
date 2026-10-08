import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

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
  imports: [CommonModule , FormsModule],
  templateUrl: './riders.component.html',
  styleUrls: ['./riders.component.css']
})
export class RidersComponent implements OnInit {

  riders: Rider[] = [];

  isLoading = false;
  errorMessage = '';

  currentPage = 1;
  pageSize = 10;
  totalPages = 0;
  totalRecords = 0;

  search = '';
  selectedStatus = '';
  selectedAvailability = '';

  sortBy = 'id';
  sortOrder = 'asc';

  selectedRider: Rider | null = null;

  private readonly apiUrl =
    'https://rider-management-jeebly-backend.onrender.com/riders';

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.loadRiders();
  }

  loadRiders(): void {
    this.isLoading = true;
    this.errorMessage = '';

    let params = new HttpParams()
      .set('page', this.currentPage.toString())
      .set('pageSize', this.pageSize.toString())
      .set('sortBy', this.sortBy)
      .set('sortOrder', this.sortOrder);

    if (this.search.trim()) {
      params = params.set('search', this.search.trim());
    }

    if (this.selectedStatus) {
      params = params.set('status', this.selectedStatus);
    }
    
    if (this.selectedAvailability) {
      params = params.set(
        'availability',
        this.selectedAvailability
      );
    }

    this.http.get<RidersResponse>(
      this.apiUrl,
      { params }
    ).subscribe({
      next: (response) => {
        this.riders = response.data.riders || [];

        this.currentPage = response.data.page;
        this.pageSize = response.data.pageSize;
        this.totalPages = response.data.totalPages;
        this.totalRecords = response.data.totalRecords;

        this.isLoading = false;
      },

      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Unable to load riders.';
      }
    });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadRiders();
  }

  onStatusChange(event: Event): void {
    const select = event.target as HTMLSelectElement;

    this.selectedStatus = select.value;
    this.currentPage = 1;

    this.loadRiders();
  }

  onAvailabilityChange(event: Event): void {
    const select = event.target as HTMLSelectElement;

    this.selectedAvailability = select.value;
    this.currentPage = 1;

    this.loadRiders();
  }

  onSortChange(event: Event): void {
    const select = event.target as HTMLSelectElement;

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
    const select = event.target as HTMLSelectElement;

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
    console.log('rider', rider);
    this.selectedRider = rider;
  }

  closeRiderDetails(): void {
    this.selectedRider = null;
  }
}