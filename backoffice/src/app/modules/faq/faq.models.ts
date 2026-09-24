export interface FAQQuestion { id: number; category_id: number; question_vi: string; answer_vi: string; question_en: string; answer_en: string; ordering: number; status: number; }
export interface FAQCategory { id: number; name: string; slug: string; ordering: number; status: number; questions: FAQQuestion[]; }
export interface FAQCategoryInput { name: string; slug: string; ordering: number; status: number; }
export type FAQQuestionInput = Omit<FAQQuestion, 'id'>;
