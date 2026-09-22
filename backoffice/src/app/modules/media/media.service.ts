import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { MediaFile, MediaFolder } from './media.models';

@Injectable({ providedIn: 'root' })
export class MediaService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/media/';

  list(query = '', folderId: number | null = null): Observable<MediaFile[]> {
    const params: Record<string, string> = {};
    if (query) params['q'] = query;
    if (folderId) params['folder_id'] = String(folderId);
    return this.http.get<MediaFile[]>(this.endpoint, { params });
  }

  upload(files: File[], folderId: number | null = null): Observable<MediaFile[]> {
    const form = new FormData();
    files.forEach((file) => form.append('files', file, file.name));
    if (folderId) form.append('folder_id', String(folderId));
    return this.http.post<MediaFile[]>(`${this.endpoint}upload/`, form);
  }

  folders(): Observable<MediaFolder[]> {
    return this.http.get<MediaFolder[]>(`${this.endpoint}folders/`);
  }

  createFolder(name: string, parentId: number | null = null): Observable<MediaFolder> {
    return this.http.post<MediaFolder>(`${this.endpoint}folders/`, { name, parent_id: parentId });
  }

  deleteFolder(id: number): Observable<void> {
    return this.http.delete<void>(`${this.endpoint}folders/${id}/`);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.endpoint}${id}/`);
  }

  download(id: number): Observable<Blob> {
    return this.http.get(`${this.endpoint}${id}/download/`, { responseType: 'blob' });
  }

  preview(id: number): Observable<Blob> {
    return this.http.get(`${this.endpoint}${id}/preview/`, { responseType: 'blob' });
  }
}
