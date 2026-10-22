
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
  createdAt: string;
}

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.css']
})
export class OrdersComponent implements OnInit {
  readonly orderStatuses = [
    'Pending',
    'Accepted',
    'Picked Up',
    'On The Way',
    'Delivered',
    'Cancelled'
  ];

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
  updatingStatusOrderId: number | null = null;
  editingOrderId: number | null = null;
  deletingOrderId: number | null = null;

  showOrderModal = false;
  isEditMode = false;
  modalOrderId: number | null = null;

  successMessage = '';
  errorMessage = '';

  orders: Order[] = [];

  // All riders are used by the filter dropdown.
  allRiders: RiderOption[] = [];

  // Only available riders are used by assignment dropdowns.
  riders: RiderOption[] = [];

  newOrder = this.emptyOrder();

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
    this.loadAllRiders();
    this.loadRiders();
  }

  private emptyOrder() {
    return {
      customer: '',
      mobile: '',
      pickup: '',
      delivery: '',
      amount: 0,
      currency: 'AED'
    };
  }

  private getPayload(response: any): any {
    return response?.data ?? response?.result ?? response;
  }

  private normalizeStatus(status: unknown): string {
    const value = String(status ?? '').trim().toLowerCase();

    const statusMap: Record<string, string> = {
      pending: 'Pending',
      created: 'Pending',
      assigned: 'Accepted',
      accept: 'Accepted',
      accepted: 'Accepted',
      picked_up: 'Picked Up',
      'picked up': 'Picked Up',
      dispatch: 'On The Way',
      on_the_way: 'On The Way',
      'on the way': 'On The Way',
      in_transit: 'On The Way',
      'in transit': 'On The Way',
      delivered: 'Delivered',
      completed: 'Delivered',
      cancelled: 'Cancelled',
      canceled: 'Cancelled'
    };

    return statusMap[value] ??
      (value
        ? value.charAt(0).toUpperCase() + value.slice(1)
        : 'Pending');
  }

  private statusForApi(status: string): string {
    const map: Record<string, string> = {
      Pending: 'pending',
      Accepted: 'accepted',
      'Picked Up': 'picked_up',
      'On The Way': 'in_transit',
      Delivered: 'delivered',
      Cancelled: 'cancelled'
    };

    return map[status] ?? status.toLowerCase();
  }

  private mapOrder(item: any): Order {
    const rider = item?.rider ?? null;
    const riderId = item?.rider_id ?? rider?.id ?? null;

    return {
      id: Number(item.id),
      customer: item.customer_name ?? item.customer ?? '',
      mobile: item.mobile ?? '',
      pickup: item.pickup ?? '',
      delivery: item.delivery ?? '',
      amount: Number(item.amount ?? 0),
      currency: item.currency ?? 'AED',
      rider: rider?.name ?? item.rider_name ?? 'Unassigned',
      riderId: riderId != null ? String(riderId) : '',
      status: this.normalizeStatus(item.status),
      createdAt: item.created_at ?? item.createdAt ?? ''
    };
  }

  loadOrders(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.orderService.getOrders({
      page: this.currentPage,
      pageSize: this.pageSize,
      search: this.searchText,
      status: this.selectedStatus
        ? this.statusForApi(this.selectedStatus)
        : '',
      rider_id: this.selectedRider,
      order_date: this.selectedDate,
      sortBy: this.sortBy
    })
    .pipe(finalize(() => {
      this.isLoading = false;
    }))
    .subscribe({
      next: (response: any) => {
        const data = this.getPayload(response);

        const items = Array.isArray(data?.orders)
          ? data.orders
          : Array.isArray(data?.items)
            ? data.items
            : Array.isArray(data)
              ? data
              : [];

        this.orders = items.map((item: any) => this.mapOrder(item));

        this.totalRecords = Number(
          data?.totalRecords ??
          data?.total_records ??
          data?.total ??
          this.orders.length
        );

        this.totalPages = Math.max(
          1,
          Number(
            data?.totalPages ??
            data?.total_pages ??
            Math.ceil(this.totalRecords / this.pageSize)
          )
        );

        this.currentPage = Number(data?.page ?? this.currentPage);

        if (this.currentPage > this.totalPages) {
          this.currentPage = this.totalPages;
          this.loadOrders();
        }
      },
      error: (error: any) => {
        console.error('Orders API error:', error);
        this.orders = [];
        this.totalRecords = 0;
        this.totalPages = 1;
        this.errorMessage = error?.status === 401
          ? 'Session expired. Please log in again.'
          : error?.error?.message ?? 'Unable to load orders.';
      }
    });
  }

  loadAllRiders(): void {
    this.orderService.getRiders().subscribe({
      next: (response: any) => {
        const data = this.getPayload(response);
        const items = Array.isArray(data?.riders)
          ? data.riders
          : Array.isArray(data)
            ? data
            : [];

        const unique = new Map<string, RiderOption>();

        items.forEach((item: any) => {
          if (item?.id == null) return;

          const id = String(item.id);
          unique.set(id, {
            id,
            name: String(item.name ?? `Rider ${id}`)
          });
        });

        this.allRiders = Array.from(unique.values());
      },
      error: (error: any) => {
        console.error('All riders API error:', error);
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

        const unique = new Map<string, RiderOption>();

        items.forEach((item: any) => {
          if (item?.id == null) return;

          const id = String(item.id);
          unique.set(id, {
            id,
            name: String(item.name ?? `Rider ${id}`)
          });
        });

        this.riders = Array.from(unique.values());

        // Keep a currently assigned rider visible in the row dropdown
        // even if the API now marks that rider as busy.
        this.orders.forEach(order => {
          if (
            order.riderId &&
            order.rider !== 'Unassigned' &&
            !this.riders.some(rider => rider.id === order.riderId)
          ) {
            this.riders.push({
              id: order.riderId,
              name: order.rider
            });
          }
        });
      },
      error: (error: any) => {
        console.error('Available riders API error:', error);
        this.errorMessage =
          error?.error?.message ?? 'Unable to load available riders.';
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
    return Math.min(this.currentPage * this.pageSize, this.totalRecords);
  }

  get pageNumbers(): number[] {
    return Array.from(
      { length: this.totalPages },
      (_, index) => index + 1
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
    if (page < 1 || page > this.totalPages || this.isLoading) {
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

  isTerminalStatus(status: string): boolean {
    const value = (status || '').trim().toLowerCase();

    return [
      'delivered',
      'completed',
      'cancelled',
      'canceled'
    ].includes(value);
  }

  statusClass(status: string): string {
    if (status === 'Pending') return 'status-pending';
    if (status === 'Delivered') return 'status-delivered';
    if (status === 'Cancelled') return 'status-cancelled';
    return 'status-transit';
  }

  updateStatus(order: Order, newStatus: string): void {
    if (
      !this.orderStatuses.includes(newStatus) ||
      newStatus === order.status ||
      this.updatingStatusOrderId === order.id ||
      this.isTerminalStatus(order.status)
    ) {
      return;
    }

    const previousStatus = order.status;
    this.clearMessages();
    this.updatingStatusOrderId = order.id;

    this.orderService.updateOrderStatus(
      order.id,
      this.statusForApi(newStatus)
    )
    .pipe(finalize(() => {
      this.updatingStatusOrderId = null;
    }))
    .subscribe({
      next: (response: any) => {
        this.successMessage =
          response?.message ?? 'Order status updated successfully.';
        this.loadOrders();
        this.loadRiders();
        this.loadAllRiders();
      },
      error: (error: any) => {
        console.error('Update order status API error:', error);
        order.status = previousStatus;
        this.errorMessage =
          error?.error?.message ?? 'Unable to update order status.';
        this.loadOrders();
      }
    });
  }

  
assignRider(order: Order, riderId: string): void {
  if (this.isTerminalStatus(order.status) ||
      this.assigningOrderId === order.id) {
    return;
  }

  const parsedRiderId = riderId ? Number(riderId) : null;

  if (riderId &&
      (!Number.isInteger(parsedRiderId) || Number(parsedRiderId) <= 0)) {
    this.errorMessage = 'Please select a valid rider.';
    return;
  }

  const previousRiderId = order.riderId;
  const previousRiderName = order.rider;

  this.clearMessages();
  this.assigningOrderId = order.id;

  this.orderService.assignRider(order.id, parsedRiderId)
    .pipe(finalize(() => {
      this.assigningOrderId = null;
    }))
    .subscribe({
      next: (response: any) => {
        const data = this.getPayload(response);
        const updatedOrder = data?.order ?? data;

        if (updatedOrder && updatedOrder.id != null) {
          const mapped = this.mapOrder(updatedOrder);
          order.riderId = mapped.riderId;
          order.rider = mapped.rider;
          order.status = mapped.status;
        } else if (parsedRiderId === null) {
          order.riderId = '';
          order.rider = 'Unassigned';
        } else {
          const selected = [...this.allRiders, ...this.riders]
            .find(r => r.id === String(parsedRiderId));

          order.riderId = String(parsedRiderId);
          order.rider = selected?.name ?? 'Assigned rider';
        }

        this.successMessage =
          response?.message ?? 'Rider assignment updated successfully.';

        this.loadOrders();
        this.loadRiders();
        this.loadAllRiders();
      },
      error: (error: any) => {
        console.error('Assign rider API error:', error);
        order.riderId = previousRiderId;
        order.rider = previousRiderName;

        this.errorMessage = error?.error?.message ??
          'Unable to assign rider. Check rider availability.';

        this.loadOrders();
        this.loadRiders();
      }
    });
}


  openCreateOrder(): void {
    this.clearMessages();
    this.isEditMode = false;
    this.modalOrderId = null;
    this.newOrder = this.emptyOrder();
    this.showOrderModal = true;
  }

  saveOrder(): void {
    this.clearMessages();

    const customerName = this.newOrder.customer.trim();

    if (!customerName) {
      this.errorMessage = 'Customer name is required.';
      return;
    }

    if (customerName.length > 100) {
      this.errorMessage = 'Customer name cannot exceed 100 characters.';
      return;
    }

    if (this.newOrder.mobile.trim().length > 20) {
      this.errorMessage = 'Mobile number cannot exceed 20 characters.';
      return;
    }

    const amount = Number(this.newOrder.amount);

    if (!Number.isFinite(amount) || amount < 0) {
      this.errorMessage = 'Amount must be a valid non-negative number.';
      return;
    }

    const payload: CreateOrderPayload = {
      customer_name: customerName,
      mobile: this.newOrder.mobile.trim(),
      pickup: this.newOrder.pickup.trim(),
      delivery: this.newOrder.delivery.trim(),
      amount,
      currency: this.newOrder.currency.trim() || 'AED'
    };

    this.isSaving = true;

    const request = this.isEditMode && this.modalOrderId !== null
      ? this.orderService.updateOrder(this.modalOrderId, payload)
      : this.orderService.createOrder(payload);

    request.pipe(finalize(() => {
      this.isSaving = false;
    }))
    .subscribe({
      next: (response: any) => {
        this.successMessage = response?.message ??
          (this.isEditMode
            ? 'Order updated successfully.'
            : 'Order created successfully.');

        this.showOrderModal = false;
        this.newOrder = this.emptyOrder();
        this.isEditMode = false;
        this.modalOrderId = null;
        this.currentPage = 1;
        this.loadOrders();
      },
      error: (error: any) => {
        console.error('Save order API error:', error);
        this.errorMessage =
          error?.error?.message ?? 'Unable to save order.';
      }
    });
  }

  openEditOrder(order: Order): void {
    if (this.isTerminalStatus(order.status)) {
      this.errorMessage = 'Delivered or Cancelled orders cannot be edited.';
      return;
    }

    this.clearMessages();
    this.isEditMode = true;
    this.modalOrderId = order.id;

    this.newOrder = {
      customer: order.customer,
      mobile: order.mobile,
      pickup: order.pickup,
      delivery: order.delivery,
      amount: order.amount,
      currency: order.currency || 'AED'
    };

    this.showOrderModal = true;
  }

  deleteOrder(order: Order): void {
    if (this.deletingOrderId === order.id) return;

    if (!confirm(`Are you sure you want to delete ORD-JB${order.id}?`)) {
      return;
    }

    this.clearMessages();
    this.deletingOrderId = order.id;

    this.orderService.deleteOrder(order.id)
      .pipe(finalize(() => {
        this.deletingOrderId = null;
      }))
      .subscribe({
        next: (response: any) => {
          this.successMessage =
            response?.message ?? 'Order deleted successfully.';

          if (this.orders.length === 1 && this.currentPage > 1) {
            this.currentPage--;
          }

          this.loadOrders();
          this.loadRiders();
          this.loadAllRiders();
        },
        error: (error: any) => {
          console.error('Delete order API error:', error);
          this.errorMessage =
            error?.error?.message ?? 'Unable to delete order.';
        }
      });
  }

  closeOrderModal(): void {
    if (this.isSaving) return;

    this.showOrderModal = false;
    this.newOrder = this.emptyOrder();
    this.isEditMode = false;
    this.modalOrderId = null;
    this.clearMessages();
  }

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }
}
