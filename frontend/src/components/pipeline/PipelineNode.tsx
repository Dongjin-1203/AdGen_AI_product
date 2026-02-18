'use client';

import { Handle, Position, NodeProps } from 'reactflow';
import { StepStatus } from './PipelineMonitor';

interface NodeData {
  label: string;
  icon: string;
  stepNum: number;
  status: StepStatus;
  error?: string;
  result_url?: string;
}

const STATUS_CONFIG: Record<StepStatus, {
  bg: string;
  border: string;
  text: string;
  badge: string;
  badgeText: string;
  spinner: boolean;
}> = {
  pending: {
    bg: 'bg-white',
    border: 'border-gray-200',
    text: 'text-gray-400',
    badge: 'bg-gray-100 text-gray-400',
    badgeText: '대기',
    spinner: false,
  },
  running: {
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    text: 'text-blue-700',
    badge: 'bg-blue-100 text-blue-600',
    badgeText: '실행 중',
    spinner: true,
  },
  success: {
    bg: 'bg-green-50',
    border: 'border-green-300',
    text: 'text-green-700',
    badge: 'bg-green-100 text-green-600',
    badgeText: '완료',
    spinner: false,
  },
  failed: {
    bg: 'bg-red-50',
    border: 'border-red-300',
    text: 'text-red-700',
    badge: 'bg-red-100 text-red-600',
    badgeText: '실패',
    spinner: false,
  },
  skipped: {
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    text: 'text-gray-400',
    badge: 'bg-gray-100 text-gray-400',
    badgeText: '건너뜀',
    spinner: false,
  },
};

export default function PipelineNodeComponent({ data }: NodeProps<NodeData>) {
  const config = STATUS_CONFIG[data.status];

  return (
    <div
      className={`
        relative w-72 px-4 py-3 rounded-xl border-2 shadow-sm
        transition-all duration-300
        ${config.bg} ${config.border}
      `}
    >
      {/* 상단 핸들 (소스 연결) */}
      <Handle type="target" position={Position.Top} className="!bg-gray-300" />

      <div className="flex items-center gap-3">
        {/* 스텝 번호 */}
        <div
          className={`
            flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
            text-sm font-bold
            ${data.status === 'success' ? 'bg-green-500 text-white' :
              data.status === 'running' ? 'bg-blue-500 text-white' :
              data.status === 'failed'  ? 'bg-red-500 text-white' :
              'bg-gray-100 text-gray-500'}
          `}
        >
          {data.status === 'success' ? '✓' :
           data.status === 'failed'  ? '✕' :
           data.stepNum}
        </div>

        {/* 아이콘 + 라벨 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-base">{data.icon}</span>
            <span className={`text-sm font-medium truncate ${config.text}`}>
              {data.label}
            </span>
          </div>

          {/* 에러 메시지 */}
          {data.status === 'failed' && data.error && (
            <p className="text-xs text-red-500 mt-0.5 line-clamp-2">
              {data.error}
            </p>
          )}
        </div>

        {/* 상태 배지 */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {config.spinner && (
            <svg
              className="animate-spin h-3.5 w-3.5 text-blue-500"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12" cy="12" r="10"
                stroke="currentColor" strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          )}
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${config.badge}`}>
            {config.badgeText}
          </span>
        </div>
      </div>

      {/* 결과 이미지 (있는 경우) */}
      {data.status === 'success' && data.result_url && (
        <div className="mt-2 pt-2 border-t border-green-200">
          <img
            src={data.result_url}
            alt="step result"
            className="w-12 h-12 object-cover rounded-lg shadow-sm"
          />
        </div>
      )}

      {/* 하단 핸들 (타겟 연결) */}
      <Handle type="source" position={Position.Bottom} className="!bg-gray-300" />
    </div>
  );
}
