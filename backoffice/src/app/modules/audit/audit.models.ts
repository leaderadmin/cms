export interface ActivityLog {
  id: number;
  timestamp: string;
  level: string;
  service: string;
  module: string;
  environment: string;
  host: string;
  message: string;
  trace_id: string | null;
  request_id: string | null;
  session_id: string | null;
  user_id: number | null;
  user_name: string | null;
  username: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  http_method: string;
  http_path: string;
  http_status: number | null;
  portal_id: string | null;
  method: string;
  path: string;
  status_code: number | null;
  error_code: string | null;
  error_type: string | null;
  stack_trace: string | null;
  changed_fields: unknown[];
  duration_ms: number | null;
  ip_address: string | null;
  user_agent: string;
  tags: string[];
  created_at: string;
}

export interface ActivityLogResponse {
  results: ActivityLog[];
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ActivityLogFilters {
  page: number;
  limit: number;
  action: string;
  path: string;
  status_code: string;
  level: string;
  username: string;
}
