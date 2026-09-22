import { Component, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BackofficePageComponent, ToastService } from '../../shared/ui';
import { AuthService } from '../auth';
import { MediaFile, MediaFolder } from './media.models';
import { MediaService } from './media.service';

@Component({
  selector: 'app-media-manager',
  imports: [FormsModule, DatePipe, BackofficePageComponent],
  templateUrl: './media-manager.component.html',
  styleUrl: './media-manager.component.css',
})
export class MediaManagerComponent {
  private readonly mediaApi = inject(MediaService);
  private readonly toast = inject(ToastService);
  protected readonly auth = inject(AuthService);
  protected files: MediaFile[] = [];
  protected search = '';
  protected loading = true;
  protected uploading = false;
  protected error = '';
  protected selectedFiles: File[] = [];
  protected activeSection = 'drive';
  protected viewMode: 'grid' | 'list' = 'grid';
  protected folders: MediaFolder[] = [];
  protected activeFolderId: number | null = null;
  protected expandedFolders = new Set<number>();
  protected previewUrls = new Map<number, string>();

  constructor() { this.loadFolders(); this.load(); }

  protected loadFolders(): void {
    this.mediaApi.folders().subscribe({
      next: (folders) => { this.folders = folders; this.expandedFolders = new Set(folders.map((folder) => folder.id)); },
      error: (response) => { this.error = response.error?.detail || 'Unable to load folders.'; },
    });
  }

  protected load(): void {
    this.loading = true;
    this.mediaApi.list(this.search, this.activeFolderId).subscribe({
      next: (files) => { this.revokePreviewUrls(); this.files = files; this.loadImagePreviews(files); this.loading = false; this.error = ''; },
      error: (response) => { this.error = response.error?.detail || 'Unable to load media files.'; this.loading = false; },
    });
  }

  protected chooseFiles(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFiles = Array.from(input.files || []);
  }

  protected upload(): void {
    if (!this.selectedFiles.length) return;
    this.uploading = true;
    this.mediaApi.upload(this.selectedFiles, this.activeFolderId).subscribe({
      next: () => { this.selectedFiles = []; this.uploading = false; this.toast.show('Files uploaded successfully.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to upload files.'; this.uploading = false; },
    });
  }

  protected remove(file: MediaFile): void {
    if (!window.confirm(`Delete "${file.name}"?`)) return;
    this.mediaApi.delete(file.id).subscribe({
      next: () => { this.toast.show('File deleted successfully.'); this.load(); },
      error: (response) => { this.error = response.error?.detail || 'Unable to delete file.'; },
    });
  }

  protected download(file: MediaFile): void {
    this.mediaApi.download(file.id).subscribe({
      next: (content) => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(content);
        link.download = file.name;
        link.click();
        URL.revokeObjectURL(link.href);
      },
      error: (response) => { this.error = response.error?.detail || 'Unable to download file.'; },
    });
  }

  protected isImage(file: MediaFile): boolean {
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(file.extension);
  }

  protected previewUrl(file: MediaFile): string | null {
    return this.previewUrls.get(file.id) || null;
  }

  protected can(permission: string): boolean {
    return this.auth.user()?.permissions.includes(permission) || false;
  }

  protected get filteredFiles(): MediaFile[] {
    if (this.activeSection === 'recent') {
      return this.files.slice(0, 8);
    }
    if (this.activeSection === 'documents') {
      return this.files.filter((file) => ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'].includes(file.extension));
    }
    if (this.activeSection === 'images') {
      return this.files.filter((file) => ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(file.extension));
    }
    return this.files;
  }

  protected get documentCount(): number {
    return this.files.filter((file) => ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'].includes(file.extension)).length;
  }

  protected get imageCount(): number {
    return this.files.filter((file) => ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(file.extension)).length;
  }

  protected get totalSize(): number {
    return this.files.reduce((total, file) => total + file.size, 0);
  }

  protected get storagePercent(): number {
    return Math.min(100, (this.totalSize / (10 * 1024 * 1024 * 1024)) * 100);
  }

  protected get sectionLabel(): string {
    if (this.activeSection === 'folder') return this.folders.find((folder) => folder.id === this.activeFolderId)?.name || 'Folder';
    return { drive: 'My Drive', documents: 'Documents', images: 'Images', recent: 'Recent' }[this.activeSection] || 'My Drive';
  }

  protected selectSection(section: string): void {
    this.activeSection = section;
    this.activeFolderId = null;
    this.load();
  }

  protected selectFolder(folder: MediaFolder): void {
    this.activeSection = 'folder';
    this.activeFolderId = folder.id;
    this.load();
  }

  protected toggleFolder(folder: MediaFolder, event: Event): void {
    event.stopPropagation();
    const expanded = new Set(this.expandedFolders);
    if (expanded.has(folder.id)) expanded.delete(folder.id);
    else expanded.add(folder.id);
    this.expandedFolders = expanded;
  }

  protected isFolderExpanded(folder: MediaFolder): boolean {
    return this.expandedFolders.has(folder.id);
  }

  protected get visibleFolders(): Array<MediaFolder & { depth: number }> {
    const result: Array<MediaFolder & { depth: number }> = [];
    const append = (parentId: number | null, depth: number): void => {
      this.folders.filter((folder) => folder.parent_id === parentId).forEach((folder) => {
        result.push({ ...folder, depth });
        if (this.isFolderExpanded(folder)) append(folder.id, depth + 1);
      });
    };
    append(null, 0);
    return result;
  }

  protected removeFolder(folder: MediaFolder): void {
    if (!window.confirm(`Delete folder "${folder.name}" and its subfolders? Files will be kept in My Drive.`)) return;
    this.mediaApi.deleteFolder(folder.id).subscribe({
      next: () => {
        if (this.activeFolderId !== null && this.isWithinFolder(this.activeFolderId, folder.id)) this.selectSection('drive');
        this.toast.show('Folder deleted successfully.');
        this.loadFolders();
        this.load();
      },
      error: (response) => { this.error = response.error?.detail || 'Unable to delete folder.'; },
    });
  }

  private isWithinFolder(folderId: number, ancestorId: number): boolean {
    let current = this.folders.find((folder) => folder.id === folderId);
    while (current) {
      if (current.id === ancestorId) return true;
      current = current.parent_id === null ? undefined : this.folders.find((folder) => folder.id === current?.parent_id);
    }
    return false;
  }

  protected createFolder(): void {
    const name = window.prompt('Folder name');
    if (!name?.trim()) return;
    this.mediaApi.createFolder(name.trim(), this.activeFolderId).subscribe({
      next: (folder) => { this.folders = [...this.folders, folder].sort((left, right) => left.name.localeCompare(right.name)); this.toast.show('Folder created successfully.'); },
      error: (response) => { this.error = response.error?.detail || 'Unable to create folder.'; },
    });
  }

  protected fileIcon(file: MediaFile): string {
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(file.extension)) return 'bi-file-earmark-image';
    if (file.extension === 'pdf') return 'bi-file-earmark-pdf';
    if (['doc', 'docx'].includes(file.extension)) return 'bi-file-earmark-word';
    if (['xls', 'xlsx', 'csv'].includes(file.extension)) return 'bi-file-earmark-spreadsheet';
    if (['zip', 'rar', '7z'].includes(file.extension)) return 'bi-file-earmark-zip';
    return 'bi-file-earmark-text';
  }

  protected fileTone(file: MediaFile): string {
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(file.extension)) return 'image';
    if (file.extension === 'pdf') return 'pdf';
    if (['doc', 'docx'].includes(file.extension)) return 'word';
    if (['xls', 'xlsx', 'csv'].includes(file.extension)) return 'sheet';
    if (['zip', 'rar', '7z'].includes(file.extension)) return 'archive';
    return 'text';
  }

  protected formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  private loadImagePreviews(files: MediaFile[]): void {
    files.filter((file) => this.isImage(file)).forEach((file) => {
      this.mediaApi.preview(file.id).subscribe({
        next: (content) => this.previewUrls.set(file.id, URL.createObjectURL(content)),
      });
    });
  }

  private revokePreviewUrls(): void {
    this.previewUrls.forEach((url) => URL.revokeObjectURL(url));
    this.previewUrls.clear();
  }
}
