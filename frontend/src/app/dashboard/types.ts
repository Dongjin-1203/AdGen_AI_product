/**
 * Dashboard 타입 정의
 */

export interface Content {
  content_id: string;
  product_name?: string;
  category?: string;
  image_url: string;
  thumbnail_url?: string;
}

export interface StepData {
  id: string;
  title: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  content?: React.ReactNode;
  timestamp: Date;
}

export interface StyleOption {
  value: string;
  label: string;
  emoji: string;
  description: string;
}

export const AVAILABLE_STYLES: readonly StyleOption[] = [
  { value: 'resort', label: '리조트', emoji: '🏖️', description: '밝고 경쾌한 휴양지 분위기' },
  { value: 'retro', label: '레트로', emoji: '📻', description: '빈티지하고 복고적인 감성' },
  { value: 'romantic', label: '로맨틱', emoji: '💕', description: '부드럽고 여성스러운 분위기' },
] as const;

export interface AdInputs {
  discount: string;
  period: string;
  brand: string;
  keywords: string;
  mustInclude: string;
}