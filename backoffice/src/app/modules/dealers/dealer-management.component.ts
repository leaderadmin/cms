import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { Dealer, DealerInput, DealerType } from './dealer.models';
import { DealerService } from './dealer.service';
@Component({ selector: 'app-dealer-management', imports: [FormsModule, BackofficePageComponent], templateUrl: './dealer-management.component.html', styleUrl: './dealer-management.component.css' })
export class DealerManagementComponent {
  private readonly api = inject(DealerService); private readonly toast = inject(ToastService);
  protected items: Dealer[] = []; protected regions: { id: number; name: string }[] = []; protected areas: { id: number; name: string; region_id: number }[] = []; protected loading = true; protected saving = false; protected error = ''; protected query = ''; protected selectedType: DealerType | '' = ''; protected editorOpen = false; protected editingId: number | null = null; protected form = this.emptyForm();
  protected readonly dealerTypes: { value: DealerType; label: string }[] = [{ value: 'branch', label: 'Chi nhánh' }, { value: 'atm', label: 'ATM' }, { value: 'transaction_office', label: 'Phòng giao dịch' }];
  constructor() { this.load(); this.api.regions().subscribe({ next: (items) => this.regions = items }); this.api.areas().subscribe({ next: (items) => this.areas = items }); }
  protected load(): void { this.loading = true; this.api.list(this.query.trim(), this.selectedType).subscribe({ next: (items) => { this.items = items; this.loading = false; }, error: (response) => { this.error = response.error?.detail || 'Unable to load dealers'; this.loading = false; } }); }
  protected openCreate(): void { this.editingId = null; this.form = this.emptyForm(); this.editorOpen = true; this.areas = []; }
  protected edit(item: Dealer): void { this.editingId = item.id; this.form = { ...item, region_id: item.region_id }; this.editorOpen = true; this.loadAreas(item.region_id || undefined); }
  protected regionChanged(): void { this.form.area_id = null; this.loadAreas(this.form.region_id || undefined); }
  protected loadAreas(regionId?: number | null): void { this.api.areas(regionId || undefined).subscribe({ next: (items) => this.areas = items }); }
  protected save(): void { if (!this.form.name.trim() || !this.form.code.trim() || !this.form.area_id) return; this.saving = true; const request = this.editingId ? this.api.update(this.editingId, this.form) : this.api.create(this.form); request.subscribe({ next: () => { this.editorOpen = false; this.saving = false; this.toast.show(this.editingId ? 'Đã cập nhật đơn vị.' : 'Đã tạo đơn vị.'); this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to save dealer'; this.saving = false; } }); }
  protected remove(item: Dealer): void { if (!window.confirm(`Delete dealer "${item.name}"?`)) return; this.api.delete(item.id).subscribe({ next: () => { this.toast.show('Dealer deleted.'); this.load(); }, error: (response) => this.error = response.error?.detail || 'Unable to delete dealer' }); }
  protected typeLabel(type: DealerType): string { return this.dealerTypes.find((item) => item.value === type)?.label || type; }
  private emptyForm(): DealerInput { return { name: '', code: '', dealer_type: 'branch', province_city: '', address: '', hotline: '', email: '', latitude: null, longitude: null, opening_hours: '', status: 1, area_id: null, area: '', region_id: null, region: '' }; }
}
