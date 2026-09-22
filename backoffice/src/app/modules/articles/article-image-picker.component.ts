import { Component, EventEmitter, Input, OnInit, Output, inject } from '@angular/core';
import { MediaFile } from '../media/media.models';
import { MediaService } from '../media/media.service';

@Component({
  selector: 'app-article-image-picker',
  templateUrl: './article-image-picker.component.html',
  styleUrl: './article-image-picker.component.css',
})
export class ArticleImagePickerComponent implements OnInit {
  private readonly mediaApi = inject(MediaService);
  @Input() imageId: number | null = null;
  @Output() readonly imageIdChange = new EventEmitter<number | null>();
  protected images: MediaFile[] = [];
  protected loading = true;
  protected uploading = false;
  protected open = false;
  protected readonly previewUrls = new Map<number, string>();

  ngOnInit(): void {
    this.mediaApi.list().subscribe({
      next: (files) => { this.images = files.filter((file) => file.content_type.startsWith('image/')); this.images.forEach((image) => this.loadPreview(image)); this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  protected get selected(): MediaFile | undefined { return this.images.find((file) => file.id === this.imageId); }

  protected preview(image: MediaFile): string { return this.previewUrls.get(image.id) || ''; }

  protected select(image: MediaFile): void {
    this.imageIdChange.emit(image.id);
    this.open = false;
  }

  protected clear(): void { this.imageIdChange.emit(null); }

  protected chooseFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.uploading = true;
    this.mediaApi.upload([file]).subscribe({
      next: (files) => { const image = files.find((item) => item.content_type.startsWith('image/')); if (image) { this.images = [image, ...this.images]; this.loadPreview(image); this.select(image); } this.uploading = false; input.value = ''; },
      error: () => { this.uploading = false; input.value = ''; },
    });
  }

  private loadPreview(image: MediaFile): void {
    this.mediaApi.preview(image.id).subscribe({ next: (blob) => this.previewUrls.set(image.id, URL.createObjectURL(blob)) });
  }
}
