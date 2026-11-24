
import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';

import {
  OrderService,
  CreateOrderPayload
} from '../../core/services/order.service';
import { LanguageService } from '../../core/services/language.service';
import { ToastComponent, ToastType } from '../../shared/toast/toast.component';
import * as XLSX from 'xlsx';

declare const google: any;

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
  imports: [CommonModule, FormsModule, ToastComponent],
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.css']
})
export class OrdersComponent implements OnInit, OnDestroy {
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
  createdFrom = '';
  createdTo = '';
  dateRangeError = '';
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
  selectedViewOrder: Order | null = null;
  updatedOrderIds = new Set<number>();

  openViewOrder(order: Order): void {
    this.selectedViewOrder = order;
  }

  closeViewOrder(): void {
    this.selectedViewOrder = null;
  }

  highlightOrder(orderId: number): void {
    this.updatedOrderIds.add(orderId);
    setTimeout(() => {
      this.updatedOrderIds.delete(orderId);
    }, 3000);
  }

  successMessage = '';
  errorMessage = '';

  toastMessage = '';
  toastType: ToastType = 'success';
  showToast = false;
  private toastTimer: ReturnType<typeof setTimeout> | null = null;

  showCreateConfirmation = false;
  showDeleteDialog = false;
  deletingOrder: Order | null = null;

  orders: Order[] = [];

  // All riders are used by the filter dropdown.
  allRiders: RiderOption[] = [];

  // Only available riders are used by assignment dropdowns.
  riders: RiderOption[] = [];

  newOrder = this.emptyOrder();

  showDownloadDropdown = false;
  isDownloadingReport = false;

  constructor(
    private orderService: OrderService,
    public langService: LanguageService
  ) {}

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.report-dropdown-wrapper')) {
      this.showDownloadDropdown = false;
    }
  }

  lastGeneratedReportUrl: string | null = null;
  lastGeneratedReportName: string | null = null;

  toggleDownloadDropdown(): void {
    this.showDownloadDropdown = !this.showDownloadDropdown;
  }

  downloadReport(format: 'xlsx' | 'csv'): void {
    this.showDownloadDropdown = false;
    this.isDownloadingReport = true;

    this.orderService.exportOrders({
      search: this.searchText,
      status: this.selectedStatus ? this.statusForApi(this.selectedStatus) : '',
      rider_id: this.selectedRider,
      order_date: this.selectedDate,
      created_from: this.createdFrom,
      created_to: this.createdTo,
      sortBy: this.sortBy
    }, format).subscribe({
      next: (blob: Blob) => {
        // Verify response is actually a binary blob and not an error JSON
        if (blob.size > 0 && blob.type !== 'application/json') {
          this.saveReportBlob(blob, format);
        } else {
          this.generateClientSideReport(format);
        }
      },
      error: () => {
        // Fallback to client-side report using complete order database records
        this.generateClientSideReport(format);
      }
    });
  }

  saveReportBlob(blob: Blob, format: 'xlsx' | 'csv'): void {
    this.isDownloadingReport = false;
    const filename = `Jeebly_Order_Report.${format}`;
    const url = window.URL.createObjectURL(blob);
    this.lastGeneratedReportUrl = url;
    this.lastGeneratedReportName = filename;

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    setTimeout(() => {
      if (this.lastGeneratedReportUrl === url) {
        window.URL.revokeObjectURL(url);
      }
    }, 30000);

    this.showNotification(`Order report downloaded successfully (${format.toUpperCase()}).`, 'success');
  }

  deleteGeneratedReport(): void {
    this.showDownloadDropdown = false;
    if (this.lastGeneratedReportUrl) {
      window.URL.revokeObjectURL(this.lastGeneratedReportUrl);
      this.lastGeneratedReportUrl = null;
      const name = this.lastGeneratedReportName || 'report';
      this.lastGeneratedReportName = null;
      this.showNotification(`Generated file "${name}" has been deleted successfully.`, 'success');
    } else {
      this.showNotification('No active generated report file to delete.', 'info');
    }
  }

  private generateClientSideReport(format: 'xlsx' | 'csv'): void {
    this.orderService.getOrders({
      page: 1,
      pageSize: 5000,
      search: this.searchText,
      status: this.selectedStatus ? this.statusForApi(this.selectedStatus) : '',
      rider_id: this.selectedRider,
      order_date: this.selectedDate,
      created_from: this.createdFrom,
      created_to: this.createdTo,
      sortBy: this.sortBy
    }).subscribe({
      next: (response: any) => {
        const data = this.getPayload(response);
        const rawItems = Array.isArray(data?.orders)
          ? data.orders
          : Array.isArray(data?.items)
            ? data.items
            : Array.isArray(data)
              ? data
              : [];

        const headers = [
          'Order ID',
          'Customer Name',
          'Customer Mobile',
          'Pickup Location',
          'Delivery Destination',
          'Order Amount',
          'Currency',
          'Order Status',
          'Order Created Date',
          'Assigned Rider ID',
          'Assigned Rider Name',
          'Rider Contact Mobile',
          'Rider Email',
          'Rider Vehicle',
          'Rider Status',
          'Rider Availability'
        ];

        const rows = rawItems.map((item: any) => {
          const rider = item?.rider ?? null;
          const riderId = item?.rider_id ?? rider?.id ?? null;
          return [
            item?.id ? `ORD-JB${item.id}` : '',
            item?.customer_name ?? item?.customer ?? '',
            item?.mobile ?? '',
            item?.pickup ?? '',
            item?.delivery ?? '',
            item?.amount != null ? Number(item.amount) : 0,
            item?.currency ?? 'AED',
            this.normalizeStatus(item?.status),
            item?.created_at ?? item?.createdAt ?? '',
            riderId != null ? `RIDER-${riderId}` : 'N/A',
            rider?.name ?? item?.rider_name ?? 'Unassigned',
            rider?.mobile ?? 'N/A',
            rider?.email ?? 'N/A',
            rider?.vehicle ?? 'N/A',
            rider?.status ? String(rider.status).toUpperCase() : 'N/A',
            rider?.availability ? String(rider.availability).toUpperCase() : 'N/A'
          ];
        });

        if (format === 'xlsx') {
          try {
            const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
            const colWidths = headers.map((h: string, i: number) => {
              const maxLen = Math.max(h.length, ...rows.map((r: any[]) => String(r[i] ?? '').length));
              return { wch: Math.min(35, Math.max(12, maxLen + 3)) };
            });
            worksheet['!cols'] = colWidths;
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, 'Orders Report');
            const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
            const blob = new Blob([excelBuffer], {
              type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });
            this.saveReportBlob(blob, 'xlsx');
          } catch (e) {
            console.error('XLSX client generation error:', e);
            this.downloadCsvDirect(headers, rows);
          }
        } else {
          this.downloadCsvDirect(headers, rows);
        }
      },
      error: (err: any) => {
        this.isDownloadingReport = false;
        console.error('Client-side order export fetch error:', err);
        this.showNotification('Failed to generate order report. Please check your network.', 'error');
      }
    });
  }

  private downloadCsvDirect(headers: string[], rows: any[][]): void {
    const csvContent = [
      headers.map(h => `"${String(h).replace(/"/g, '""')}"`).join(','),
      ...rows.map(row => row.map(val => `"${String(val ?? '').replace(/"/g, '""')}"`).join(','))
    ].join('\r\n');

    const blob = new Blob(['\uFEFF' + csvContent], {
      type: 'text/csv;charset=utf-8;'
    });
    this.saveReportBlob(blob, 'csv');
  }


  showNotification(message: string, type: ToastType = 'success', durationMs = 2500): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }

    this.toastMessage = this.langService.t(message);
    this.toastType = type;
    this.showToast = true;

    this.toastTimer = setTimeout(() => {
      this.dismissToast();
    }, durationMs);
  }

  dismissToast(): void {
    this.showToast = false;
    this.toastMessage = '';
    this.successMessage = '';

    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }
  }

  ngOnDestroy(): void {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }
  }

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
      created_from: this.createdFrom,
      created_to: this.createdTo,
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
      },
      error: (error: any) => {
        console.error('Available riders API error:', error);
        this.errorMessage =
          error?.error?.message ?? 'Unable to load available riders.';
      }
    });
  }

  getRiderOptionsForOrder(order: Order): RiderOption[] {
    if (order.riderId && order.rider && order.rider !== 'Unassigned') {
      const exists = this.riders.some(r => r.id === order.riderId);
      if (!exists) {
        return [{ id: order.riderId, name: order.rider }, ...this.riders];
      }
    }
    return this.riders;
  }

  trackByOrderId(index: number, order: Order): number {
    return order.id;
  }

  trackByRiderId(index: number, rider: RiderOption): string {
    return rider.id;
  }

  onAssignRiderChange(order: Order, event: Event): void {
    const target = event.target as HTMLSelectElement;
    const newRiderId = target.value;
    if (newRiderId === order.riderId) {
      return;
    }
    this.assignRider(order, newRiderId);
  }

  getStatusOptionsForOrder(order: Order): string[] {
    if (order.riderId) {
      return this.orderStatuses.filter(s => s !== 'Cancelled');
    }
    return this.orderStatuses;
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

  onDateRangeChange(): void {
    if (this.createdFrom && this.createdTo && this.createdFrom > this.createdTo) {
      this.dateRangeError = 'Created From date cannot be later than Created To date.';
      return;
    }
    this.dateRangeError = '';
    this.onFilterChange();
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedStatus = '';
    this.selectedRider = '';
    this.selectedDate = '';
    this.createdFrom = '';
    this.createdTo = '';
    this.dateRangeError = '';
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

    if (newStatus === 'Cancelled' && order.riderId) {
      this.errorMessage = 'An order cannot be cancelled once a rider has been assigned.';
      this.showNotification(this.errorMessage, 'error', 3500);
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
        this.highlightOrder(order.id);
        const msg = response?.message ?? 'Order status updated successfully.';
        this.showNotification(msg, 'success', 2500);
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

        this.highlightOrder(order.id);
        const msg = response?.message ?? 'Order assignment updated successfully.';
        this.showNotification(msg, 'success', 2500);

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
    setTimeout(() => this.initPlacesAutocomplete(), 200);
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
    setTimeout(() => this.initPlacesAutocomplete(), 200);
  }

  initPlacesAutocomplete(): void {
    if (typeof google !== 'undefined' && google?.maps?.places) {
      try {
        const pickupInput = document.getElementById('pickupAddress') as HTMLInputElement;
        const deliveryInput = document.getElementById('deliveryAddress') as HTMLInputElement;

        if (pickupInput && !(pickupInput as any)._autocompleteInitialized) {
          const pickupAuto = new google.maps.places.Autocomplete(pickupInput);
          (pickupInput as any)._autocompleteInitialized = true;
          pickupAuto.addListener('place_changed', () => {
            const place = pickupAuto.getPlace();
            if (place?.formatted_address) {
              this.newOrder.pickup = place.formatted_address;
            }
          });
        }

        if (deliveryInput && !(deliveryInput as any)._autocompleteInitialized) {
          const deliveryAuto = new google.maps.places.Autocomplete(deliveryInput);
          (deliveryInput as any)._autocompleteInitialized = true;
          deliveryAuto.addListener('place_changed', () => {
            const place = deliveryAuto.getPlace();
            if (place?.formatted_address) {
              this.newOrder.delivery = place.formatted_address;
            }
          });
        }
      } catch (e) {
        console.warn('Google Places autocomplete init warning:', e);
      }
    }
  }

  getTimelineStepState(order: Order | null, step: string): 'completed' | 'active' | 'pending' {
    if (!order) return 'pending';
    const status = order.status;

    if (status === 'Cancelled') {
      return step === 'placed' ? 'completed' : 'pending';
    }

    const orderStages = ['Pending', 'Accepted', 'Picked Up', 'On The Way', 'Delivered'];
    const currentIdx = orderStages.indexOf(status);

    switch (step) {
      case 'placed':
        return currentIdx >= 0 ? 'completed' : 'active';
      case 'assigned':
        if (order.riderId && order.rider && order.rider !== 'Unassigned') {
          return currentIdx >= 1 ? 'completed' : 'active';
        }
        return currentIdx >= 1 ? 'completed' : 'pending';
      case 'accepted':
        if (currentIdx > 1) return 'completed';
        if (currentIdx === 1) return 'active';
        return 'pending';
      case 'picked_up':
        if (currentIdx > 2) return 'completed';
        if (currentIdx === 2) return 'active';
        return 'pending';
      case 'on_the_way':
        if (currentIdx > 3) return 'completed';
        if (currentIdx === 3) return 'active';
        return 'pending';
      case 'delivered':
        if (currentIdx === 4) return 'completed';
        return 'pending';
      default:
        return 'pending';
    }
  }

  cancelCreateOrder(): void {
    if (this.isSaving) return;
    this.showCreateConfirmation = false;
  }

  confirmCreateOrder(): void {
    if (this.isSaving) return;
    this.showCreateConfirmation = false;
    this.executeSaveOrder();
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

    const mobile = this.newOrder.mobile.trim();
    if (!mobile) {
      this.errorMessage = 'Customer mobile number is required.';
      return;
    }

    const digitsOnly = mobile.replace(/[^0-9]/g, '');
    if (digitsOnly.length < 7 || mobile.length > 20) {
      this.errorMessage = 'Please enter a valid customer contact number (10 digits).';
      return;
    }

    const pickup = this.newOrder.pickup.trim();
    if (!pickup) {
      this.errorMessage = 'Pickup location address is required.';
      return;
    }

    if (pickup.length > 255) {
      this.errorMessage = 'Pickup address cannot exceed 255 characters.';
      return;
    }

    const delivery = this.newOrder.delivery.trim();
    if (!delivery) {
      this.errorMessage = 'Delivery destination address is required.';
      return;
    }

    if (delivery.length > 255) {
      this.errorMessage = 'Delivery destination cannot exceed 255 characters.';
      return;
    }

    const amount = Number(this.newOrder.amount);
    if (!Number.isFinite(amount) || amount <= 0) {
      this.errorMessage = 'Order value / amount is required and must be greater than 0.';
      return;
    }

    if (!this.newOrder.currency || !this.newOrder.currency.trim()) {
      this.errorMessage = 'Currency is required.';
      return;
    }

    if (this.isSaving) {
      return;
    }

    if (!this.isEditMode) {
      this.showCreateConfirmation = true;
      return;
    }

    this.executeSaveOrder();
  }

  executeSaveOrder(): void {
    if (this.isSaving) return;

    const customerName = this.newOrder.customer.trim();
    const amount = Number(this.newOrder.amount);

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
        if (this.modalOrderId) {
          this.highlightOrder(this.modalOrderId);
        }
        const msg = response?.message ??
          (this.isEditMode
            ? 'Order updated successfully.'
            : 'Order created successfully.');

        this.showNotification(msg, 'success', 2500);

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

  requestDeleteOrder(order: Order): void {
    this.deletingOrder = order;
    this.showDeleteDialog = true;
  }

  cancelDeleteOrder(): void {
    if (this.deletingOrderId !== null) return;
    this.showDeleteDialog = false;
    this.deletingOrder = null;
  }

  confirmDeleteOrder(): void {
    if (!this.deletingOrder || this.deletingOrderId !== null) return;

    const order = this.deletingOrder;
    this.clearMessages();
    this.deletingOrderId = order.id;

    this.orderService.deleteOrder(order.id)
      .pipe(finalize(() => {
        this.deletingOrderId = null;
      }))
      .subscribe({
        next: (response: any) => {
          this.showDeleteDialog = false;
          this.deletingOrder = null;
          const msg =
            response?.message ?? 'Order deleted successfully.';
          this.showNotification(msg, 'success', 2500);

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
          this.showNotification(this.errorMessage, 'error', 4000);
        }
      });
  }

  deleteOrder(order: Order): void {
    this.requestDeleteOrder(order);
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
