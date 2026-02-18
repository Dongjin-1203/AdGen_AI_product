// Pipeline 관련 타입 정의

export type StepStatus = 'pending' | 'running' | 'success' | 'failed' | 'skipped';

export type PipelineStatus = 'pending' | 'running' | 'success' | 'failed';

export interface StepState {
  status: StepStatus;
  started_at?: string;
  completed_at?: string;
  error?: string;
  result_url?: string;
}

export interface PipelineState {
  job_id: string;
  status: PipelineStatus;
  current_step: number;
  steps: Record<string, StepState>;
  error?: string;
  error_step?: number;
  final_image_url?: string;
  updated_at: string;
}

export interface PipelineRunRequest {
  content_id: string;
  style: 'resort' | 'retro' | 'romantic';
  model_index?: number;
  user_prompt?: string;
}

export interface PipelineRunResponse {
  job_id: string;
  status: string;
  message: string;
  ws_url: string;
}