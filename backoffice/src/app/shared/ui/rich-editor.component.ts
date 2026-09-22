import { AfterViewInit, Component, ElementRef, EventEmitter, Input, OnChanges, OnDestroy, Output, SimpleChanges, ViewChild, inject } from '@angular/core';
import Quill from 'quill';
import { MediaService } from '../../modules/media/media.service';

const CardLayoutEmbed = Quill.import('blots/block/embed') as any;
class CardLayoutBlot extends CardLayoutEmbed {
  static blotName = 'card-layout';
  static tagName = 'div';
  static className = 'ql-card-layout-embed';

  static create(value: string): HTMLElement {
    const node = super.create() as HTMLElement;
    node.setAttribute('contenteditable', 'false');
    node.setAttribute('aria-label', 'Card layout preview');
    node.innerHTML = value;
    return node;
  }
}

Quill.register(CardLayoutBlot as any);

@Component({
  selector: 'app-rich-editor',
  standalone: true,
  template: '<div class="rich-editor-shell" [class.plain-mode]="mode === \'plain\'"><div #toolbar class="rich-editor-toolbar"><span class="ql-formats"><button class="ql-bold" type="button"></button><button class="ql-italic" type="button"></button><button class="ql-underline" type="button"></button><button class="ql-strike" type="button"></button></span><span class="ql-formats"><select class="ql-header"><option value="1"></option><option value="2"></option><option value="3"></option><option selected></option></select></span><span class="ql-formats"><button class="ql-list" value="ordered" type="button"></button><button class="ql-list" value="bullet" type="button"></button></span><span class="ql-formats"><button class="ql-blockquote" type="button"></button><button class="ql-code-block" type="button"></button><button class="ql-link" type="button"></button><button class="ql-image" type="button"></button><button #cardLayoutButton class="card-layout-button" type="button" title="Chèn layout card" (click)="insertCardLayout()"></button></span><span class="ql-formats"><select class="ql-align"></select><button class="ql-clean" type="button"></button></span></div><div #editor class="rich-editor-canvas" [attr.aria-label]="ariaLabel"></div><input #imageInput class="image-input" type="file" accept="image/png,image/jpeg,image/gif,image/webp" (change)="uploadImage($event)" aria-label="Upload image"></div>',
  styleUrl: './rich-editor.component.css',
})
export class RichEditorComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() value = '';
  @Input() mode: 'html' | 'plain' = 'html';
  @Input() ariaLabel = 'Rich text editor';
  @Output() readonly valueChange = new EventEmitter<string>();
  @ViewChild('editor') private editor?: ElementRef<HTMLDivElement>;
  @ViewChild('toolbar') private toolbar?: ElementRef<HTMLDivElement>;
  @ViewChild('imageInput') private imageInput?: ElementRef<HTMLInputElement>;
  private readonly mediaApi = inject(MediaService);
  private quill?: Quill;

  private get editorValue(): string {
    if (!this.quill) return this.value;
    const hasCardLayout = Boolean(this.quill.root.querySelector('.ql-card-layout-embed'));
    return this.mode === 'html' || hasCardLayout ? this.quill.root.innerHTML : this.quill.root.textContent || '';
  }

  private setEditorValue(value: string): void {
    if (!this.quill) return;
    if (this.mode === 'html' || value.includes('ql-card-layout-embed')) this.quill.root.innerHTML = value || '';
    else this.quill.root.textContent = value || '';
  }

  private readonly cardPreset = `<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin:24px 0;font-family:Arial,sans-serif"><article style="overflow:hidden;border:1px solid #e3e9ef;border-radius:8px;background:#fff;text-align:center"><div style="height:150px;background:linear-gradient(135deg,#ffd9a8,#ffb45d);display:grid;place-items:center;color:#fff;font-size:42px">✦</div><h2 style="margin:18px 16px 8px;color:#08a7a1;font-size:20px">Tiết kiệm Tích lũy Tâm An</h2><p style="min-height:42px;margin:0 16px 18px;color:#66727a">Tiết kiệm tích lũy hấp dẫn</p><ul style="min-height:110px;margin:0;padding:18px 24px;border-top:1px solid #e3e9ef;text-align:left;color:#66727a;line-height:1.5"><li>Lãi suất top đầu thị trường</li><li>Thiết lập khoản tiết kiệm theo mục tiêu</li><li>Mọi tác vụ hoàn toàn trực tuyến</li></ul><a href="#" style="display:inline-block;margin:16px;padding:10px 22px;border-radius:5px;background:#ff8b22;color:#fff;text-decoration:none;font-weight:700">XEM CHI TIẾT</a></article><article style="overflow:hidden;border:1px solid #e3e9ef;border-radius:8px;background:#fff;text-align:center"><div style="height:150px;background:linear-gradient(135deg,#ffd9a8,#ffb45d);display:grid;place-items:center;color:#fff;font-size:42px">✦</div><h2 style="margin:18px 16px 8px;color:#08a7a1;font-size:20px">Tiết kiệm Tích lũy Tâm An</h2><p style="min-height:42px;margin:0 16px 18px;color:#66727a">Tiết kiệm tích lũy hấp dẫn</p><ul style="min-height:110px;margin:0;padding:18px 24px;border-top:1px solid #e3e9ef;text-align:left;color:#66727a;line-height:1.5"><li>Lãi suất top đầu thị trường</li><li>Thiết lập khoản tiết kiệm theo mục tiêu</li><li>Mọi tác vụ hoàn toàn trực tuyến</li></ul><a href="#" style="display:inline-block;margin:16px;padding:10px 22px;border-radius:5px;background:#ff8b22;color:#fff;text-decoration:none;font-weight:700">XEM CHI TIẾT</a></article><article style="overflow:hidden;border:1px solid #e3e9ef;border-radius:8px;background:#fff;text-align:center"><div style="height:150px;background:linear-gradient(135deg,#12c8c8,#00a2ad);display:grid;place-items:center;color:#ffd800;font-size:42px">✦</div><h2 style="margin:18px 16px 8px;color:#08a7a1;font-size:20px">Tiết kiệm An Thịnh</h2><p style="min-height:42px;margin:0 16px 18px;color:#66727a">Chủ động rút gốc linh hoạt</p><ul style="min-height:110px;margin:0;padding:18px 24px;border-top:1px solid #e3e9ef;text-align:left;color:#66727a;line-height:1.5"><li>Khách hàng có thể rút gốc một phần</li><li>Thủ tục đơn giản, nhanh chóng</li><li>Được ủy quyền, chuyển quyền sở hữu</li></ul><a href="#" style="display:inline-block;margin:16px;padding:10px 22px;border-radius:5px;background:#ff8b22;color:#fff;text-decoration:none;font-weight:700">XEM CHI TIẾT</a></article></div><p><br></p>`;

  ngAfterViewInit(): void {
    if (!this.editor) return;
    this.quill = new Quill(this.editor.nativeElement, {
      theme: 'snow',
      modules: { toolbar: this.toolbar?.nativeElement },
      formats: ['bold', 'italic', 'underline', 'strike', 'header', 'list', 'blockquote', 'code-block', 'link', 'image', 'align', 'card-layout'],
    });
    if (this.mode === 'html') {
      const toolbarModule = this.quill.getModule('toolbar') as { addHandler: (name: string, handler: () => void) => void };
      toolbarModule.addHandler('image', () => this.imageInput?.nativeElement.click());
    }
    this.setEditorValue(this.value);
    this.quill.on('text-change', () => this.valueChange.emit(this.editorValue));
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['value'] && !changes['value'].firstChange && this.editorValue !== this.value) this.setEditorValue(this.value);
  }

  protected uploadImage(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    if (!file || !file.type.startsWith('image/')) return;
    this.mediaApi.upload([file]).subscribe({
      next: (files) => {
        const image = files.find((item) => item.content_type.startsWith('image/'));
        if (!image || !this.quill) return;
        const selection = this.quill.getSelection(true);
        this.quill.insertEmbed(selection?.index ?? this.quill.getLength(), 'image', `/api/media/${image.id}/preview/`, 'user');
        this.quill.setSelection((selection?.index ?? this.quill.getLength()) + 1, 0, 'silent');
      },
    });
  }

  protected insertCardLayout(): void {
    if (!this.quill) return;
    const index = this.quill.getSelection(true)?.index ?? this.quill.getLength();
    this.quill.insertEmbed(index, 'card-layout', this.cardPreset, 'user');
    this.quill.setSelection(index + 1, 0, 'silent');
  }

  ngOnDestroy(): void { this.quill?.off('text-change'); }
}
