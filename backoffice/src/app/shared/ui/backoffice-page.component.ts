import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@Component({
  selector: 'app-backoffice-page',
  imports: [MatButtonModule, MatProgressBarModule],
  templateUrl: './backoffice-page.component.html',
  styleUrl: './backoffice-page.component.css',
})
export class BackofficePageComponent {
  @Input() eyebrow = 'ANGULAR / BACKOFFICE';
  @Input() title = '';
  @Input() description = '';
  @Input() loading = false;
  @Input() error = '';

  @Output() readonly retry = new EventEmitter<void>();
}
