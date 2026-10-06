import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';

interface Rider {
  id: number;
  name: string;
  status: string;
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
  imports: [CommonModule],
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

  selectedRider: Rider | null = null;

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.loadRiders();
  }

  loadRiders(): void {
    this.isLoading = true;
    this.errorMessage = '';

    const url =
      `https://rider-management-jeebly-backend.onrender.com/riders` +
      `?page=${this.currentPage}&pageSize=${this.pageSize}`;

    this.http.get<RidersResponse>(url).subscribe({
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

  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
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
    console.log("rider", rider)
    this.selectedRider = rider;
  }

  closeRiderDetails(): void {
    this.selectedRider = null;
  }
}