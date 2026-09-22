export interface ArticleTranslationSummary {
  id: number;
  language_code: string;
  title: string;
  status: number;
}

export interface Article {
  id: number;
  legacy_id: string | null;
  name: string;
  type: string;
  status: number;
  status_label: string;
  view_count: number;
  public_date: string | null;
  categories: { id: number; title: string; name: string }[];
  tags: string[];
  tag_ids: number[];
  image: { id: number; name: string; url: string } | null;
  cta: { label: string; url: string; phone: string } | null;
  translation: { language_code: string; title: string; sub_title?: string; content?: string; short_description: string; url_key?: string; seo_title?: string; meta_description?: string } | null;
  translations: ArticleTranslationSummary[];
}

export interface ArticleTag {
  id: number;
  name: string;
  slug: string;
  usage_count: number;
}

export interface ArticleCategory {
  id: number;
  legacy_id?: string | null;
  name: string;
  title: string;
  type: string;
  status: number;
  parent_id?: number | null;
  ordering?: number;
  translation?: { language_code: string; title: string; description: string; url_key: string; meta_keyword: string; meta_description: string } | null;
}

export interface ArticleCategoryInput {
  name: string;
  type: string;
  status: number;
  parent_id: number | null;
  ordering: number;
  translation: { language_code: string; title: string; description: string; url_key: string; meta_keyword: string; meta_description: string };
}

export interface ArticleInput {
  name: string;
  type: string;
  status: number;
  category_ids: number[];
  tags: string[];
  tag_ids: number[];
  image_id: number | null;
  cta: { label: string; url: string; phone: string };
  translation: {
    language_code: string;
    title: string;
    sub_title: string;
    content: string;
    short_description: string;
    url_key: string;
    seo_title: string;
    meta_description: string;
  };
  translations?: ArticleInput['translation'][];
}

export interface ArticlePage {
  count: number;
  page: number;
  page_size: number;
  next: number | null;
  previous: number | null;
  results: Article[];
}
