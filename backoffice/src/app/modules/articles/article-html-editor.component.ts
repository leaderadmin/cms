import { AfterViewInit, Component, ElementRef, EventEmitter, Input, OnChanges, OnDestroy, Output, SimpleChanges, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import Quill from 'quill';

@Component({
  selector: 'app-article-html-editor',
  imports: [FormsModule],
  templateUrl: './article-html-editor.component.html',
  styleUrl: './article-html-editor.component.css',
})
export class ArticleHtmlEditorComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() content = '';
  @Output() readonly contentChange = new EventEmitter<string>();
  @ViewChild('editor') private editor?: ElementRef<HTMLDivElement>;
  protected sourceMode = false;
  protected source = '';
  private quill?: Quill;

  ngAfterViewInit(): void {
    if (!this.editor) return;
    this.quill = new Quill(this.editor.nativeElement, {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ header: [2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['blockquote', 'code-block', 'link'],
          [{ align: [] }],
          ['clean'],
        ],
      },
      formats: ['header', 'bold', 'italic', 'underline', 'strike', 'list', 'blockquote', 'code-block', 'link', 'align'],
    });
    if (this.content) this.quill.root.innerHTML = this.content;
    this.quill.on('text-change', () => this.emitEditorContent());
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['content'] && !changes['content'].firstChange && this.quill && !this.sourceMode && this.quill.root.innerHTML !== this.content) {
      this.quill.root.innerHTML = this.content;
    }
  }

  protected toggleSource(): void {
    if (this.sourceMode) {
      this.content = this.source;
      this.sourceMode = false;
      if (this.quill) this.quill.root.innerHTML = this.content;
      this.contentChange.emit(this.content);
    } else {
      this.source = this.content;
      this.sourceMode = true;
    }
  }

  protected updateSource(): void {
    this.content = this.source;
    this.contentChange.emit(this.content);
  }

  protected emitEditorContent(): void {
    this.content = this.quill?.root.innerHTML || '';
    this.contentChange.emit(this.content);
  }

  ngOnDestroy(): void { this.quill?.off('text-change'); }
}
