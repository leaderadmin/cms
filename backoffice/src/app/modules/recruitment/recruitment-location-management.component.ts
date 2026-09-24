import { Component, inject, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { RecruitmentService } from './recruitment.service';
import { RecruitmentTaxonomy } from './recruitment.models';

@Component({
  selector: 'app-recruitment-location-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './recruitment-location-management.component.html',
  styleUrl: './recruitment-location-management.component.css',
})
export class RecruitmentLocationManagementComponent implements OnChanges {
  private readonly api = inject(RecruitmentService);
  private readonly toast = inject(ToastService);
  @Input() isArea = false;
  protected items: (RecruitmentTaxonomy & { region_id?: number })[] = [];
  protected regions: RecruitmentTaxonomy[] = [];
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected editingId: number | null = null;
  protected name = '';
  protected regionId: number | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['isArea']) {
      this.editorOpen = false;
      this.load();
    }
  }

  protected load(): void {
    this.loading = true;
    if (this.isArea) {
      this.api.regions().subscribe({ next: (regions) => { this.regions = regions; this.api.allAreas().subscribe({ next: (items) => { this.items = items; this.loading = false; }, error: (response) => this.fail(response) }); }, error: (response) => this.fail(response) });
    } else {
      this.api.regions().subscribe({ next: (items) => { this.items = items; this.loading = false; }, error: (response) => this.fail(response) });
    }
  }

  protected openCreate(): void { this.editingId = null; this.name = ''; this.regionId = null; this.editorOpen = true; }
  protected edit(item: RecruitmentTaxonomy & { region_id?: number }): void { this.editingId = item.id; this.name = item.name; this.regionId = item.region_id || null; this.editorOpen = true; }
  protected regionName(regionId?: number): string { return this.regions.find((region) => region.id === regionId)?.name || '-'; }
  protected save(): void {
    if (!this.name.trim() || (this.isArea && !this.regionId)) return;
    this.saving = true;
    const request = this.isArea
      ? (this.editingId ? this.api.updateArea(this.editingId, this.name, this.regionId!) : this.api.createArea(this.name, this.regionId!))
      : (this.editingId ? this.api.updateRegion(this.editingId, this.name) : this.api.createRegion(this.name));
    request.subscribe({ next: () => { this.editorOpen = false; this.saving = false; this.toast.show(`${this.isArea ? 'Area' : 'Region'} saved.`); this.load(); }, error: (response) => this.fail(response) });
  }
  protected remove(item: RecruitmentTaxonomy): void {
    if (!window.confirm(`Delete ${this.isArea ? 'area' : 'region'} "${item.name}"?`)) return;
    const request = this.isArea ? this.api.deleteArea(item.id) : this.api.deleteRegion(item.id);
    request.subscribe({ next: () => { this.toast.show(`${this.isArea ? 'Area' : 'Region'} deleted.`); this.load(); }, error: (response) => this.fail(response) });
  }
  private fail(response: any): void { this.error = response.error?.detail || `Unable to load ${this.isArea ? 'areas' : 'regions'}`; this.loading = false; this.saving = false; }
}
