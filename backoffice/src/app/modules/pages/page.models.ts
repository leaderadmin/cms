export type PageStatus = 'draft' | 'published' | 'archived';
export type PageModuleType = 'card' | 'form' | 'table' | 'modal';

export interface PageModule {
  id?: string;
  type: PageModuleType;
  name: string;
  settings: { columns?: number; visible?: boolean; [key: string]: unknown };
  content: Record<string, unknown>;
}

export interface PageComponent {
  id: string;
  name: string;
  key: string;
  modules: PageModule[];
}

export interface Page {
  id: number;
  name: string;
  slug: string;
  template_key: string;
  status: PageStatus;
  components: PageComponent[];
  created_by: string | null;
  created_at: string;
  updated_at: string;
  template_id: number | null;
  draft_version_id: number | null;
  published_version_id: number | null;
}

export interface PageInput {
  name: string;
  slug: string;
  template_key: string;
  status: PageStatus;
  components: PageComponent[];
}

export interface PageTemplateRegion {
  id?: string;
  key?: string;
  label: string;
  locked: boolean;
  maxBlocks?: number | null;
  allowedBlocks?: string[];
  max_blocks: number | null;
  allowed_blocks: string[];
}

export interface PageTemplate {
  id: number;
  name: string;
  key: string;
  regions: PageTemplateRegion[];
  tokens: { primary_color: string; radius: string; font: string; [key: string]: string };
  status: PageStatus;
  page_count: number;
  affected_pages: Array<{ name: string; slug: string }>;
  updated_at: string;
}

export type PageComponentStatus = PageStatus;

export interface ReusablePageComponent {
  id: number;
  name: string;
  block_name: string;
  html: string;
  css: string;
  js: string;
  content: string;
  status: PageComponentStatus;
  created_at: string;
  updated_at: string;
}

export type ReusablePageComponentInput = Omit<ReusablePageComponent, 'id' | 'created_at' | 'updated_at'>;

export interface PageComponentDefinition {
  id: number;
  name: string;
  component_key: string;
  prehtml: string;
  html: string;
  css: string;
  js: string;
  content: string;
  backhtml: string;
  blocks: ComponentBlockPlacement[];
  status: PageComponentStatus;
  created_at: string;
  updated_at: string;
}

export interface ComponentBlockPlacement {
  block_name: string;
  position: number;
}

export type PageComponentDefinitionInput = Omit<PageComponentDefinition, 'id' | 'created_at' | 'updated_at'>;

export type PageTemplateInput = Omit<PageTemplate, 'id' | 'page_count' | 'affected_pages' | 'updated_at'>;
