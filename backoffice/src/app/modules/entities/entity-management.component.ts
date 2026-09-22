import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { SchemaColumn, SchemaTable } from './entity.models';
import { EntityService } from './entity.service';

@Component({
  selector: 'app-entity-management',
  imports: [FormsModule, BackofficePageComponent],
  templateUrl: './entity-management.component.html',
  styleUrl: './entity-management.component.css',
})
export class EntityManagementComponent {
  private readonly entityApi = inject(EntityService);
  private readonly toast = inject(ToastService);
  protected tables: SchemaTable[] = [];
  protected selected: SchemaTable | null = null;
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected search = '';
  protected addOpen = false;
  protected renameColumn: SchemaColumn | null = null;
  protected editColumn: SchemaColumn | null = null;
  protected newColumn = { name: '', type: 'varchar', nullable: true, default: '' };
  protected columnEditor = { type: 'varchar', length: null as number | null, precision: null as number | null, scale: null as number | null, nullable: true, default: '' };
  protected renamedName = '';

  constructor() { this.loadCatalog(); }

  protected loadCatalog(): void {
    this.loading = true;
    this.entityApi.catalog().subscribe({
      next: (tables) => { this.tables = tables; this.loading = false; if (tables.length) this.selectTable(this.selected?.name || tables[0].name); },
      error: () => { this.error = 'Unable to load database schema'; this.loading = false; },
    });
  }

  protected selectTable(name: string): void {
    this.entityApi.table(name).subscribe({
      next: (table) => { this.selected = table; this.addOpen = false; this.renameColumn = null; this.editColumn = null; this.error = ''; },
      error: () => { this.error = 'Unable to load table structure'; },
    });
  }

  protected get filteredTables(): SchemaTable[] {
    const query = this.search.trim().toLowerCase();
    return query ? this.tables.filter((table) => table.name.toLowerCase().includes(query)) : this.tables;
  }

  protected openAdd(): void { this.addOpen = true; this.renameColumn = null; this.newColumn = { name: '', type: 'varchar', nullable: true, default: '' }; }

  protected add(): void {
    if (!this.selected || !this.newColumn.name.trim()) return;
    this.saving = true;
    this.entityApi.addColumn(this.selected.name, this.newColumn).subscribe({
      next: (table) => { this.selected = table; this.addOpen = false; this.saving = false; this.toast.show('Column added successfully.'); this.loadCatalog(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to add column'; this.saving = false; },
    });
  }

  protected openRename(column: SchemaColumn): void { this.renameColumn = column; this.renamedName = column.name; this.addOpen = false; this.editColumn = null; }

  protected openEdit(column: SchemaColumn): void {
    this.editColumn = column;
    this.renameColumn = null;
    this.addOpen = false;
    this.columnEditor = {
      type: column.db_type === 'character varying' ? 'varchar' : column.db_type === 'timestamp with time zone' ? 'timestamp' : column.db_type,
      length: column.length,
      precision: column.precision,
      scale: column.scale,
      nullable: column.nullable,
      default: column.default == null ? '' : String(column.default),
    };
  }

  protected update(): void {
    if (!this.selected || !this.editColumn) return;
    if (!window.confirm(`Apply structure changes to "${this.editColumn.name}"?`)) return;
    this.saving = true;
    this.entityApi.updateColumn(this.selected.name, this.editColumn.name, this.columnEditor).subscribe({
      next: (table) => { this.selected = table; this.editColumn = null; this.saving = false; this.toast.show('Column structure saved successfully.'); this.loadCatalog(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to update column structure'; this.saving = false; },
    });
  }

  protected rename(): void {
    if (!this.selected || !this.renameColumn || !this.renamedName.trim()) return;
    this.saving = true;
    this.entityApi.updateColumn(this.selected.name, this.renameColumn.name, { name: this.renamedName }).subscribe({
      next: (table) => { this.selected = table; this.renameColumn = null; this.saving = false; this.toast.show('Column renamed successfully.'); this.loadCatalog(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to rename column'; this.saving = false; },
    });
  }

  protected drop(column: SchemaColumn): void {
    if (!this.selected || column.primary_key || !window.confirm(`Drop column "${column.name}" from ${this.selected.name}?`)) return;
    this.entityApi.dropColumn(this.selected.name, column.name).subscribe({
      next: (table) => { this.selected = table; this.toast.show('Column deleted successfully.'); this.loadCatalog(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to drop column'; },
    });
  }
}
