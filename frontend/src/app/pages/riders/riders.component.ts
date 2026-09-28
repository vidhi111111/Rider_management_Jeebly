import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-riders',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './riders.component.html',
  styleUrls: ['./riders.component.css']
})
export class RidersComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

}
