export interface Menu {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface MenuItem {
  id: number;
  menu_id: number;
  label: string;
  href: string;
  view: string;
  icon: string;
  required_permission: string;
  parent_id: number | null;
  sort_order: number;
  is_active: boolean;
}

export interface MenuItemPayload {
  menu_id: number;
  label: string;
  href: string;
  view: string;
  icon: string;
  required_permission: string;
  parent_id: number | null;
  sort_order: number;
  is_active: boolean;
}

export interface RoutePermission {
  id: number;
  code: string;
  module: string;
  route: string;
}

export interface MenuPayload {
  name: string;
  slug: string;
  is_active: boolean;
}
