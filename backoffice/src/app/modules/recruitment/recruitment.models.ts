export interface RecruitmentJob {
  id: number; title: string; slug: string; department: string; department_id: number | null; region: string; region_id: number | null; area: string; area_id: number | null; business_unit: string; business_unit_id: number | null; location: string; employment_type: string;
  description: string; requirements: string; benefits: string; deadline: string | null; status: number; status_label: string; tags: string[]; tag_ids: number[];
}
export type RecruitmentJobInput = Omit<RecruitmentJob, 'id' | 'status_label'>;
export interface RecruitmentTaxonomy { id: number; name: string; slug: string; status: number; usage_count: number; }
