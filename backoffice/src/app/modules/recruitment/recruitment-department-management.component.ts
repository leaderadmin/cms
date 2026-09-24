import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { RecruitmentTaxonomy } from './recruitment.models';
import { RecruitmentService } from './recruitment.service';

@Component({
  selector: 'app-recruitment-department-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './recruitment-department-management.component.html',
  styleUrl: './recruitment-department-management.component.css',
})
export class RecruitmentDepartmentManagementComponent {
  private readonly api = inject(RecruitmentService);
  private readonly toast = inject(ToastService);
  protected items: RecruitmentTaxonomy[] = [];
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected editingId: number | null = null;
  protected name = '';

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.api.departments().subscribe({
      next: (items) => { this.items = items; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load departments'; this.loading = false; },
    });
  }

  protected openCreate(): void { this.editingId = null; this.name = ''; this.editorOpen = true; }
  protected edit(item: RecruitmentTaxonomy): void { this.editingId = item.id; this.name = item.name; this.editorOpen = true; }
  protected save(): void {
    if (!this.name.trim()) return;
    this.saving = true;
    const request = this.editingId ? this.api.updateDepartment(this.editingId, this.name) : this.api.createDepartment(this.name);
    request.subscribe({
      next: () => { this.editorOpen = false; this.saving = false; this.toast.show('Department saved.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to save department'; this.saving = false; },
    });
  }

  protected remove(item: RecruitmentTaxonomy): void {
    if (!window.confirm(`Delete department "${item.name}"?`)) return;
    this.api.deleteDepartment(item.id).subscribe({
      next: () => { this.toast.show('Department deleted.'); this.load(); },
      error: (response) => this.error = response.error?.detail || 'Unable to delete department',
    });
  }
}
