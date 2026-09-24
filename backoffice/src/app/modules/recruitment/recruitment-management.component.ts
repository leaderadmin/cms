import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, RichEditorComponent, ToastService } from '../../shared/ui';
import { ArticleTagInputComponent } from '../articles/article-tag-input.component';
import { RecruitmentJob, RecruitmentJobInput, RecruitmentTaxonomy } from './recruitment.models';
import { RecruitmentService } from './recruitment.service';
@Component({ selector: 'app-recruitment-management', imports: [FormsModule, BackofficePageComponent, RichEditorComponent, ArticleTagInputComponent], templateUrl: './recruitment-management.component.html', styleUrl: './recruitment-management.component.css' })
export class RecruitmentManagementComponent {
  private readonly api = inject(RecruitmentService); private readonly toast = inject(ToastService);
  protected items: RecruitmentJob[] = []; protected tags: RecruitmentTaxonomy[] = []; protected regions: RecruitmentTaxonomy[] = []; protected areas: RecruitmentTaxonomy[] = []; protected businessUnits: RecruitmentTaxonomy[] = []; protected loading = true; protected saving = false; protected error = ''; protected query = ''; protected editorOpen = false; protected editingId: number | null = null; protected form = this.emptyForm();
  constructor() { this.load(); this.loadMetadata(); }
  protected loadMetadata(): void { this.api.tags().subscribe({ next: (items) => this.tags = items }); this.api.regions().subscribe({ next: (items) => this.regions = items }); }
  protected load(): void { this.loading = true; this.api.list(this.query.trim()).subscribe({ next: (items) => { this.items = items; this.loading = false; }, error: (response) => { this.error = response.error?.detail || 'Unable to load recruitment jobs'; this.loading = false; } }); }
  protected openCreate(): void { this.editingId = null; this.form = this.emptyForm(); this.editorOpen = true; this.error = ''; }
  protected edit(item: RecruitmentJob): void { this.editingId = item.id; this.form = { ...item }; this.editorOpen = true; if (item.region_id) { this.api.areas(item.region_id).subscribe({ next: (areas) => { this.areas = areas; if (item.area_id) { this.api.businessUnits(item.area_id).subscribe({ next: (units) => { this.businessUnits = units; } }); } } }); } }
  protected save(): void { if (!this.form.title.trim()) return; this.form.department = this.businessUnits.find((item) => item.id === this.form.business_unit_id)?.name || ''; this.form.department_id = null; this.saving = true; const request = this.editingId ? this.api.update(this.editingId, this.form) : this.api.create(this.form); request.subscribe({ next: () => { this.saving = false; this.editorOpen = false; this.toast.show('Recruitment job saved.'); this.load(); }, error: (response) => { this.error = response.error?.detail || 'Unable to save recruitment job'; this.saving = false; } }); }
  protected remove(item: RecruitmentJob): void { if (!window.confirm(`Delete recruitment job "${item.title}"?`)) return; this.api.delete(item.id).subscribe({ next: () => { this.toast.show('Recruitment job deleted.'); this.load(); }, error: (response) => this.error = response.error?.detail || 'Unable to delete recruitment job' }); }
  protected emptyForm(): RecruitmentJobInput { return { title: '', slug: '', department: '', department_id: null, region: '', region_id: null, area: '', area_id: null, business_unit: '', business_unit_id: null, location: '', employment_type: '', description: '', requirements: '', benefits: '', deadline: null, status: 0, tags: [], tag_ids: [] }; }
  protected selectRegion(id: number | null): void { this.form.region_id = id; this.form.area_id = null; this.form.business_unit_id = null; this.areas = []; this.businessUnits = []; if (id) this.api.areas(id).subscribe({ next: (items) => this.areas = items }); }
  protected selectArea(id: number | null): void { this.form.area_id = id; this.form.business_unit_id = null; this.businessUnits = []; if (id) this.api.businessUnits(id).subscribe({ next: (items) => this.businessUnits = items }); }
}
