export interface ManagedUser {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_staff: boolean;
  roles: string[];
  date_joined: string;
  last_login: string | null;
  display_name: string;
  job_title: string;
  phone: string;
  location: string;
  bio: string;
}

export interface ManagedRole {
  id: number;
  name: string;
  permissions: string[];
}

export interface ManagedPermission {
  id: number;
  code: string;
  module: string;
  route: string;
}
