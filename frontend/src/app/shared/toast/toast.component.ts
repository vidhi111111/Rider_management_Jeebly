
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css']
})
export class ToastComponent {
  @Input() message = '';
  @Input() type: ToastType = 'success';
  @Input() visible = false;

  @Output() dismissed = new EventEmitter<void>();

  closeToast(): void {
    this.visible = false;
    this.dismissed.emit();
  }
}
