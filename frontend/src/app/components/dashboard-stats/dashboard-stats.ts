import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-dashboard-stats',
  imports: [],
  templateUrl: './dashboard-stats.html',
  styleUrl: './dashboard-stats.css'
})
export class DashboardStatsComponent {
  @Input() dashboardStats: any = null;
}