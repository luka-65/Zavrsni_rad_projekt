import { Component, EventEmitter, Input, Output } from '@angular/core';
@Component({
  selector: 'app-simulation-history',
  imports: [],
  templateUrl: './simulation-history.html',
  styleUrl: './simulation-history.css'
})
export class SimulationHistoryComponent {
  @Input() simulations: any[] = [];
  @Output() selectSimulationEvent = new EventEmitter<number>();
}