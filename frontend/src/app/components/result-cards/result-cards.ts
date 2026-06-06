import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-result-cards',
  imports: [],
  templateUrl: './result-cards.html',
  styleUrl: './result-cards.css'
})
export class ResultCardsComponent {
  @Input() result: any = null;
}