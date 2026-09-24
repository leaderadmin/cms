import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { DynamicForm, DynamicFormField, DynamicFormFieldType, DynamicFormInput } from './page.models';
import { PageService as ContentService } from './page.service';

@Component({
  selector: 'app-form-management',
  imports: [FormsModule, DatePipe, BackofficePageComponent],
  templateUrl: './form-management.component.html',
  styleUrl: './form-management.component.css',
})
export class FormManagementComponent {
  private readonly formsApi = inject(ContentService);
  private readonly toast = inject(ToastService);
  protected forms: DynamicForm[] = [];
  protected selected: DynamicForm | null = null;
  protected form: DynamicFormInput = this.emptyForm();
  protected query = '';
  protected loading = true;
  protected saving = false;
  protected error = '';
  protected editorOpen = false;
  protected readonly fieldTypes: Array<{ value: DynamicFormFieldType; label: string }> = [
    { value: 'text', label: 'Text' }, { value: 'textarea', label: 'Textarea' }, { value: 'email', label: 'Email' },
    { value: 'number', label: 'Number' }, { value: 'select', label: 'Select' }, { value: 'checkbox', label: 'Checkbox' },
    { value: 'date', label: 'Date' }, { value: 'file', label: 'File' },
  ];

  constructor() { this.load(); }

  protected load(): void {
    this.loading = true;
    this.formsApi.forms(this.query.trim()).subscribe({
      next: (forms) => { this.forms = forms; this.selected = this.selected ? forms.find((item) => item.id === this.selected?.id) || null : forms[0] || null; this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Không thể tải danh sách form.'; this.loading = false; },
    });
  }
  protected create(): void { this.selected = null; this.form = this.emptyForm(); this.editorOpen = true; }
  protected edit(item: DynamicForm): void { this.selected = item; this.form = structuredClone(item); this.editorOpen = true; }
  protected cancel(): void { this.editorOpen = false; }
  protected addField(): void { this.form.fields = [...this.form.fields, this.emptyField(this.form.fields.length + 1)]; }
  protected removeField(index: number): void { this.form.fields = this.form.fields.filter((_, position) => position !== index); }
  protected fieldOptions(field: DynamicFormField): string { return field.options.map((option) => `${option.label}|${option.value}`).join('\n'); }
  protected setFieldOptions(field: DynamicFormField, value: string): void { field.options = value.split('\n').map((line) => line.trim()).filter(Boolean).map((line) => { const [label, optionValue] = line.split('|'); return { label: label.trim(), value: (optionValue || label).trim() }; }); }
  protected save(): void {
    if (!this.form.name.trim() || !this.form.short_code.trim() || this.form.fields.some((field) => !field.key.trim() || !field.label.trim())) return;
    this.saving = true;
    const request = this.selected ? this.formsApi.updateForm(this.selected.id, this.form) : this.formsApi.createForm(this.form);
    request.subscribe({ next: (form) => { this.toast.show(this.selected ? 'Đã cập nhật form.' : 'Đã tạo form.'); this.selected = form; this.editorOpen = false; this.saving = false; this.load(); }, error: (response) => { this.error = response.error?.detail || 'Không thể lưu form.'; this.saving = false; } });
  }
  protected remove(item: DynamicForm): void { if (!window.confirm(`Xóa form ${item.name}?`)) return; this.formsApi.deleteForm(item.id).subscribe({ next: () => { this.toast.show('Đã xóa form.'); this.selected = null; this.load(); }, error: (response) => { this.error = response.error?.detail || 'Không thể xóa form.'; } }); }
  private emptyField(index: number): DynamicFormField { return { key: `field_${index}`, label: `Trường ${index}`, type: 'text', placeholder: '', default: '', options: [], rules: {} }; }
  private emptyForm(): DynamicFormInput { return { name: '', short_code: '', description: '', submit_url: '', fields: [this.emptyField(1)], status: 'draft' }; }
}
