export interface UserProfile {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  roles: string[];
  permissions: string[];
  avatar_url: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  session_id: string;
  refresh_expires_at: string;
  user: UserProfile;
}

export interface AuthSession {
  session_id: string;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
  revoked_at: string | null;
  user_agent: string;
  ip_address: string | null;
  active: boolean;
}
