
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Order {
  id: string;
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

interface RiderOption {
  id: string;
  name: string;
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

  showOrderModal = false;
  isEditing = false;
  editingOrderId = '';
  successMessage = '';
  errorMessage = '';

  newOrder = {
    customer: '',
    mobile: '',
    pickup: '',
    delivery: '',
    amount: 0,
    currency: 'AED',
    status: 'Pending',
    date: new Date().toISOString().slice(0, 10)
  };

  riders: RiderOption[] = [
    { id: '1', name: 'Vidhi Garg' },
    { id: '2', name: 'kirti' },
    { id: '3', name: 'kritika' },
    { id: '4', name: 'kriti' },
    { id: '5', name: 'Vidhi Garg' }
  ];

  orders: Order[] = [
    {
      id: 'ORD-JB114972',
      customer: 'Vidhi Garg',
      mobile: '9416535200',
      pickup: 'noida',
      delivery: 'bihar',
      amount: 10000,
      currency: 'AED',
      rider: 'Unassigned',
      riderId: '',
      status: 'Pending',
      date: '2026-10-12'
    },
    {
      id: 'ORD-JB114976',
      customer: 'kirti',
      mobile: '1234567899',
      pickup: 'noida',
      delivery: 'delhi',
      amount: 1000,
      currency: 'AED',
      rider: 'kritika',
      riderId: '3',
      status: 'Pending',
      date: '2026-10-12'
    },
    {
      id: 'ORD-JB114981',
      customer: 'kritika',
      mobile: '9876543210',
      pickup: 'gurgaon',
      delivery: 'jaipur',
      amount: 2500,
      currency: 'AED',
      rider: 'kriti',
      riderId: '4',
      status: 'In Transit',
      date: '2026-10-11'
    },
    {
      id: 'ORD-JB114986',
      customer: 'kriti',
      mobile: '9876543299',
      pickup: 'delhi',
      delivery: 'chandigarh',
      amount: 1800,
      currency: 'AED',
      rider: 'Unassigned',
      riderId: '',
      status: 'Delivered',
      date: '2026-10-10'
    },
    {
      id: 'ORD-JB114990',
      customer: 'Vidhi Garg',
      mobile: '9416535300',
      pickup: 'karnal',
      delivery: 'gurgaon',
      amount: 3200,
      currency: 'AED',
      rider: 'Vidhi Garg',
      riderId: '1',
      status: 'In Transit',
      date: '2026-10-09'
    }
  ];

  ngOnInit(): void {}

  get filteredOrders(): Order[] {
    let result = this.orders.filter(order => {
      const search = this.searchText.trim().toLowerCase();

      const matchesSearch =
        !search ||
        order.id.toLowerCase().includes(search) ||
        order.customer.toLowerCase().includes(search) ||
        order.mobile.includes(search);

      const matchesStatus =
        !this.selectedStatus || order.status === this.selectedStatus;

      const matchesRider =
        !this.selectedRider || order.riderId === this.selectedRider;

      const matchesDate =
        !this.selectedDate || order.date === this.selectedDate;

      return matchesSearch && matchesStatus && matchesRider && matchesDate;
    });

    result = [...result].sort((a, b) => {
      if (this.sortBy === 'oldest') {
        return a.date.localeCompare(b.date);
      }

      if (this.sortBy === 'amountHigh') {
        return b.amount - a.amount;
      }

      if (this.sortBy === 'amountLow') {
        return a.amount - b.amount;
      }

      return b.date.localeCompare(a.date);
    });

    return result;
  }

  get paginatedOrders(): Order[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredOrders.slice(start, start + this.pageSize);
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.filteredOrders.length / this.pageSize));
  }

  get startRecord(): number {
    return this.filteredOrders.length === 0
      ? 0
      : (this.currentPage - 1) * this.pageSize + 1;
  }

  get endRecord(): number {
    return Math.min(this.currentPage * this.pageSize, this.filteredOrders.length);
  }

  onFilterChange(): void {
    this.currentPage = 1;
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedStatus = '';
    this.selectedRider = '';
    this.selectedDate = '';
    this.sortBy = 'newest';
    this.currentPage = 1;
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  changePageSize(value: string | number): void {
    this.pageSize = Number(value);
    this.currentPage = 1;
  }

  openCreateOrder(): void {
    this.isEditing = false;
    this.editingOrderId = '';
    this.resetForm();
    this.clearMessages();
    this.showOrderModal = true;
  }

  openEditOrder(order: Order): void {
    this.isEditing = true;
    this.editingOrderId = order.id;
    this.newOrder = {
      customer: order.customer,
      mobile: order.mobile,
      pickup: order.pickup,
      delivery: order.delivery,
      amount: order.amount,
      currency: order.currency,
      status: order.status,
      date: order.date
    };
    this.clearMessages();
    this.showOrderModal = true;
  }

  saveOrder(): void {
    if (
      !this.newOrder.customer.trim() ||
      !this.newOrder.mobile.trim() ||
      !this.newOrder.pickup.trim() ||
      !this.newOrder.delivery.trim() ||
      Number(this.newOrder.amount) <= 0 ||
      !this.newOrder.date
    ) {
      this.errorMessage = 'Please fill all required fields correctly.';
      return;
    }

    if (this.isEditing) {
      this.orders = this.orders.map(order =>
        order.id === this.editingOrderId
          ? {
              ...order,
              customer: this.newOrder.customer.trim(),
              mobile: this.newOrder.mobile.trim(),
              pickup: this.newOrder.pickup.trim(),
              delivery: this.newOrder.delivery.trim(),
              amount: Number(this.newOrder.amount),
              currency: this.newOrder.currency,
              status: this.newOrder.status,
              date: this.newOrder.date
            }
          : order
      );

      this.successMessage = 'Order updated successfully.';
    } else {
      const order: Order = {
        id: 'ORD-JB' + Date.now().toString().slice(-6),
        customer: this.newOrder.customer.trim(),
        mobile: this.newOrder.mobile.trim(),
        pickup: this.newOrder.pickup.trim(),
        delivery: this.newOrder.delivery.trim(),
        amount: Number(this.newOrder.amount),
        currency: this.newOrder.currency,
        rider: 'Unassigned',
        riderId: '',
        status: this.newOrder.status,
        date: this.newOrder.date
      };

      this.orders = [order, ...this.orders];
      this.clearFilters();
      this.successMessage = 'Order created successfully.';
    }

    this.showOrderModal = false;
    this.resetForm();
  }

  assignRider(order: Order, riderId: string): void {
    const rider = this.riders.find(item => item.id === riderId);

    order.riderId = riderId;
    order.rider = rider ? rider.name : 'Unassigned';
    this.successMessage = rider
      ? `Rider ${rider.name} assigned to ${order.id}.`
      : `Rider unassigned from ${order.id}.`;
  }

  deleteOrder(order: Order): void {
    if (!window.confirm(`Are you sure you want to delete ${order.id}?`)) {
      return;
    }

    this.orders = this.orders.filter(item => item.id !== order.id);
    this.currentPage = Math.min(this.currentPage, this.totalPages);
    this.successMessage = 'Order deleted successfully.';
  }

  closeOrderModal(): void {
    this.showOrderModal = false;
    this.resetForm();
    this.errorMessage = '';
  }

  resetForm(): void {
    this.newOrder = {
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

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }
}
