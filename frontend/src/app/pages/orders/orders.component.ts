
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';

import {
  OrderService,
  CreateOrderPayload
} from '../../core/services/order.service';

interface RiderOption {
  id: string;
  name: string;
}

interface Order {
  id: number;
  customer: string;
  mobile: string;
  pickup: string;
  delivery: string;
  amount: number;
  currency: string;
  rider: string;
  riderId: string;
  status: string;
  date: string;
}

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.css']
})
export class OrdersComponent implements OnInit {
  searchText = '';
  selectedStatus = '';
  selectedRider = '';
  selectedDate = '';
  sortBy = 'newest';

  pageSize = 10;
  currentPage = 1;
  totalRecords = 0;
  totalPages = 1;

  isLoading = false;
  isSaving = false;
  assigningOrderId: number | null = null;

  showOrderModal = false;
  isEditing = false;
  editingOrderId: number | null = null;

  successMessage = '';
  errorMessage = '';

  orders: Order[] = [];
  riders: RiderOption[] = [];

  newOrder = this.emptyOrder();

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
    this.loadRiders();
  }

  private emptyOrder() {
    return {
      customer: '',
      mobile: '',
      pickup: '',
      delivery: '',
      amount: 0,
      currency: 'AED',
      status: 'Pending',
      date: new Date().toISOString().slice(0, 10)
    };
  }

  private getPayload(response: any): any {
    return response?.data ?? response?.result ?? response;
  }

  private normalizeStatus(status: unknown): string {
    const value = String(status ?? '').trim().toLowerCase();

    const statusMap: Record<string, string> = {
      pending: 'Pending',
      accepted: 'Accepted',
      picked_up: 'Picked Up',
      'picked up': 'Picked Up',
      on_the_way: 'On The Way',
      'on the way': 'On The Way',
      in_transit: 'In Transit',
      'in transit': 'In Transit',
      delivered: 'Delivered',
      completed: 'Delivered',
      cancelled: 'Cancelled'
    };

    return statusMap[value] ??
      (value
        ? value.charAt(0).toUpperCase() + value.slice(1)
        : 'Pending');
  }

  private mapOrder(item: any): Order {
    const rider = item?.rider ?? null;

    return {
      id: Number(item.id),
      customer: item.customer_name ?? item.customer ?? '',
      mobile: item.mobile ?? '',
      pickup: item.pickup ?? '',
      delivery: item.delivery ?? '',
      amount: Number(item.amount ?? 0),
      currency: item.currency ?? 'AED',
      rider: rider?.name ?? 'Unassigned',
      riderId: item.rider_id != null ? String(item.rider_id) : '',
      status: this.normalizeStatus(item.status),
      date: item.created_at
        ? String(item.created_at).slice(0, 10)
        : ''
    };
  }

  loadOrders(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.orderService.getOrders({
      page: this.currentPage,
      pageSize: this.pageSize,
      search: this.searchText,
      status: this.selectedStatus,
      rider_id: this.selectedRider
    })
    .pipe(finalize(() => {
      this.isLoading = false;
    }))
    .subscribe({
      next: (response: any) => {
        const data = this.getPayload(response);

        const items = Array.isArray(data?.orders)
          ? data.orders
          : Array.isArray(data)
            ? data
            : [];

        this.orders = items.map(
          (item: any) => this.mapOrder(item)
        );

        this.totalRecords = Number(
          data?.totalRecords ?? this.orders.length
        );

        this.totalPages = Math.max(
          1,
          Number(
            data?.totalPages ??
            Math.ceil(this.totalRecords / this.pageSize)
          )
        );

        this.currentPage = Number(
          data?.page ?? this.currentPage
        );

        if (
          this.totalRecords > 0 &&
          this.currentPage > this.totalPages
        ) {
          this.currentPage = this.totalPages;
          this.loadOrders();
        }
      },
      error: (error) => {
        console.error('Orders API error:', error);

        this.orders = [];
        this.totalRecords = 0;
        this.totalPages = 1;

        this.errorMessage = error?.status === 401
          ? 'Session expired. Please log in again.'
          : 'Unable to load orders from the backend.';
      }
    });
  }

  loadRiders(): void {
    this.orderService.getAvailableRiders().subscribe({
      next: (response: any) => {
        const data = this.getPayload(response);

        const items = Array.isArray(data?.riders)
          ? data.riders
          : Array.isArray(data)
            ? data
            : [];

        const uniqueRiders = new Map<string, RiderOption>();

        for (const item of items) {
          if (item?.id == null) {
            continue;
          }

          const id = String(item.id);

          if (!uniqueRiders.has(id)) {
            uniqueRiders.set(id, {
              id,
              name: String(item.name ?? `Rider ${id}`)
            });
          }
        }

        this.riders = Array.from(uniqueRiders.values());
      },
      error: (error) => {
        console.error('Available riders API error:', error);

        if (error?.status === 401) {
          this.errorMessage = 'Session expired. Please log in again.';
        } else {
          this.errorMessage =
            'Unable to load available riders from the backend.';
        }
      }
    });
  }

  get filteredOrders(): Order[] {
    return this.orders;
  }

  get paginatedOrders(): Order[] {
    return this.orders;
  }

  get startRecord(): number {
    return this.totalRecords === 0
      ? 0
      : (this.currentPage - 1) * this.pageSize + 1;
  }

  get endRecord(): number {
    return Math.min(
      this.currentPage * this.pageSize,
      this.totalRecords
    );
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadOrders();
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedStatus = '';
    this.selectedRider = '';
    this.selectedDate = '';
    this.sortBy = 'newest';
    this.currentPage = 1;
    this.loadOrders();
  }

  changePage(page: number): void {
    if (page < 1 || page > this.totalPages) {
      return;
    }

    this.currentPage = page;
    this.loadOrders();
  }

  changePageSize(value: string | number): void {
    const size = Number(value);

    if (![5, 10, 25, 50].includes(size)) {
      return;
    }

    this.pageSize = size;
    this.currentPage = 1;
    this.loadOrders();
  }

  assignRider(order: Order, riderId: string): void {
    const parsedRiderId = riderId ? Number(riderId) : null;

    if (
      riderId &&
      (!Number.isInteger(parsedRiderId) ||
        Number(parsedRiderId) <= 0)
    ) {
      this.errorMessage = 'Please select a valid rider.';
      return;
    }

    this.assigningOrderId = order.id;
    this.clearMessages();

    this.orderService.assignRider(order.id, parsedRiderId)
      .pipe(finalize(() => {
        this.assigningOrderId = null;
      }))
      .subscribe({
        next: (response: any) => {
          this.successMessage =
            response?.message ??
            'Rider assignment updated successfully.';

          this.loadOrders();
          this.loadRiders();
        },
        error: (error) => {
          console.error('Assign Rider API error:', error);

          this.errorMessage =
            error?.error?.message ??
            'Unable to assign rider. Check availability and try again.';
        }
      });
  }

  openCreateOrder(): void {
    this.clearMessages();
    this.isEditing = false;
    this.editingOrderId = null;
    this.newOrder = this.emptyOrder();
    this.showOrderModal = true;
  }

  openEditOrder(order: Order): void {
    this.clearMessages();
    this.errorMessage =
      'Edit Order API is not implemented in the backend yet.';
  }

  saveOrder(): void {
    this.clearMessages();

    const customerName = this.newOrder.customer.trim();

    if (!customerName) {
      this.errorMessage = 'Customer name is required.';
      return;
    }

    if (customerName.length > 100) {
      this.errorMessage =
        'Customer name cannot exceed 100 characters.';
      return;
    }

    if (this.newOrder.mobile.trim().length > 20) {
      this.errorMessage =
        'Mobile number cannot exceed 20 characters.';
      return;
    }

    if (
      !Number.isFinite(Number(this.newOrder.amount)) ||
      Number(this.newOrder.amount) < 0
    ) {
      this.errorMessage =
        'Amount must be a valid non-negative number.';
      return;
    }

    const payload: CreateOrderPayload = {
      customer_name: customerName,
      mobile: this.newOrder.mobile.trim(),
      pickup: this.newOrder.pickup.trim(),
      delivery: this.newOrder.delivery.trim(),
      amount: Number(this.newOrder.amount),
      currency: this.newOrder.currency.trim() || 'AED'
    };

    this.isSaving = true;

    this.orderService.createOrder(payload)
      .pipe(finalize(() => {
        this.isSaving = false;
      }))
      .subscribe({
        next: (response: any) => {
          this.successMessage =
            response?.message ?? 'Order created successfully.';

          this.showOrderModal = false;
          this.resetForm();
          this.currentPage = 1;
          this.loadOrders();
        },
        error: (error) => {
          console.error('Create Order API error:', error);

          this.errorMessage =
            error?.error?.message ??
            'Unable to create order. Please check the backend logs.';
        }
      });
  }

  deleteOrder(order: Order): void {
    this.clearMessages();
    this.errorMessage =
      'Delete Order API is not implemented in the backend yet.';
  }

  closeOrderModal(): void {
    this.showOrderModal = false;
    this.resetForm();
    this.clearMessages();
  }

  resetForm(): void {
    this.newOrder = this.emptyOrder();
  }

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }
}
