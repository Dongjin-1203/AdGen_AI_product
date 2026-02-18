'use client';

import { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  NodeTypes,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import PipelineNodeComponent from './PipelineNode';

// ===== 타입 =====
export type StepStatus = 'pending' | 'running' | 'success' | 'failed' | 'skipped';

export interface StepState {
  status: StepStatus;
  started_at?: string;
  completed_at?: string;
  error?: string;
  result_url?: string;
}

export interface PipelineStateMsg {
  job_id: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  current_step: number;
  steps: Record<string, StepState>;
  error?: string;
  error_step?: number;
  final_image_url?: string;
  updated_at: string;
}

// ===== 단계 정의 =====
const PIPELINE_STEPS = [
  { key: 'select_image',        label: '상품 이미지 선택',       icon: '🖼️' },
  { key: 'remove_background',   label: '배경 제거 (RMBG-2.0)',   icon: '✂️' },
  { key: 'virtual_fitting',     label: '가상 모델 피팅',          icon: '👗' },
  { key: 'generate_background', label: '배경 생성 (RealvisXL)',   icon: '🎨' },
  { key: 'generate_caption',    label: '광고 캡션 생성',          icon: '✍️' },
  { key: 'generate_html',       label: 'HTML 광고 페이지',        icon: '📄' },
  { key: 'save_image',          label: '이미지 저장',             icon: '💾' },
];

const nodeTypes: NodeTypes = {
  pipelineNode: PipelineNodeComponent,
};

// ===== 노드 위치 (수직 레이아웃) =====
const NODE_X = 300;
const NODE_Y_START = 50;
const NODE_Y_GAP = 120;

function buildNodes(steps: Record<string, StepState>): Node[] {
  return PIPELINE_STEPS.map((step, i) => ({
    id: step.key,
    type: 'pipelineNode',
    position: { x: NODE_X, y: NODE_Y_START + i * NODE_Y_GAP },
    data: {
      label: step.label,
      icon: step.icon,
      stepNum: i + 1,
      status: steps[step.key]?.status ?? 'pending',
      error: steps[step.key]?.error,
      result_url: steps[step.key]?.result_url,
    },
  }));
}

function buildEdges(): Edge[] {
  return PIPELINE_STEPS.slice(0, -1).map((step, i) => ({
    id: `e-${step.key}`,
    source: step.key,
    target: PIPELINE_STEPS[i + 1].key,
    animated: false,
    style: { stroke: '#94a3b8', strokeWidth: 2 },
  }));
}

// ===== 메인 컴포넌트 =====
interface PipelineMonitorProps {
  jobId: string;
  apiBaseUrl: string;
}

export default function PipelineMonitor({ jobId, apiBaseUrl }: PipelineMonitorProps) {
  const [pipelineState, setPipelineState] = useState<PipelineStateMsg | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState(buildEdges());
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  // WebSocket 연결
  useEffect(() => {
    if (!jobId) return;

    const wsUrl = apiBaseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsUrl}/ws/pipeline/${jobId}`);

    ws.onopen = () => {
      setWsStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'ping') return;

        const msg = data as PipelineStateMsg;
        setPipelineState(msg);

        // 노드 상태 업데이트
        setNodes(buildNodes(msg.steps));

        // 실행 중인 엣지 애니메이션
        setEdges(
          buildEdges().map((edge) => {
            const sourceIdx = PIPELINE_STEPS.findIndex((s) => s.key === edge.source);
            const sourceStatus = msg.steps[edge.source]?.status;
            return {
              ...edge,
              animated: sourceStatus === 'running',
              style: {
                stroke:
                  sourceStatus === 'success' ? '#22c55e' :
                  sourceStatus === 'failed'  ? '#ef4444' :
                  sourceStatus === 'running' ? '#3b82f6' :
                  '#94a3b8',
                strokeWidth: 2,
              },
            };
          })
        );
      } catch (e) {
        console.error('WS 메시지 파싱 오류:', e);
      }
    };

    ws.onclose = () => {
      setWsStatus('disconnected');
    };

    ws.onerror = () => {
      setWsStatus('disconnected');
    };

    return () => ws.close();
  }, [jobId, apiBaseUrl]);

  // 초기 노드 렌더링
  useEffect(() => {
    const emptySteps = Object.fromEntries(
      PIPELINE_STEPS.map((s) => [s.key, { status: 'pending' as StepStatus }])
    );
    setNodes(buildNodes(emptySteps));
  }, []);

  const statusColor = {
    pending: 'text-gray-500',
    running: 'text-blue-500',
    success: 'text-green-500',
    failed: 'text-red-500',
  };

  return (
    <div className="flex flex-col h-full gap-4">
      {/* 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 bg-white rounded-xl shadow-sm border">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">광고 생성 파이프라인</h2>
          <p className="text-xs text-gray-400 mt-0.5">job: {jobId}</p>
        </div>
        <div className="flex items-center gap-3">
          {/* WS 연결 상태 */}
          <div className="flex items-center gap-1.5 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                wsStatus === 'connected' ? 'bg-green-400 animate-pulse' :
                wsStatus === 'connecting' ? 'bg-yellow-400' : 'bg-gray-300'
              }`}
            />
            <span className="text-gray-500">
              {wsStatus === 'connected' ? '실시간 연결됨' :
               wsStatus === 'connecting' ? '연결 중...' : '연결 끊김'}
            </span>
          </div>

          {/* 전체 상태 */}
          {pipelineState && (
            <span className={`text-sm font-medium ${statusColor[pipelineState.status]}`}>
              {pipelineState.status === 'pending' ? '대기 중' :
               pipelineState.status === 'running' ? '⚡ 실행 중' :
               pipelineState.status === 'success' ? '✅ 완료' : '❌ 실패'}
            </span>
          )}
        </div>
      </div>

      {/* ReactFlow */}
      <div className="flex-1 bg-gray-50 rounded-xl border overflow-hidden" style={{ minHeight: 900 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
        >
          <Background color="#e2e8f0" gap={20} />
          <Controls />
        </ReactFlow>
      </div>

      {/* 에러 메시지 */}
      {pipelineState?.error && (
        <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
          <span className="font-medium">오류 (Step {pipelineState.error_step}):</span>{' '}
          {pipelineState.error}
        </div>
      )}

      {/* 최종 결과 */}
      {pipelineState?.final_image_url && (
        <div className="px-4 py-4 bg-green-50 border border-green-200 rounded-xl">
          <p className="text-sm font-medium text-green-700 mb-2">✅ 광고 생성 완료!</p>
          <img
            src={pipelineState.final_image_url}
            alt="생성된 광고"
            className="w-48 h-48 object-cover rounded-lg shadow"
          />
        </div>
      )}
    </div>
  );
}
