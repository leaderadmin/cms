export interface MediaFile {
  id: number;
  name: string;
  size: number;
  content_type: string;
  uploaded_by: string | null;
  created_at: string;
  download_url: string;
  extension: string;
  folder_id: number | null;
}

export interface MediaFolder {
  id: number;
  name: string;
  parent_id: number | null;
  file_count: number;
}
