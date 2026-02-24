'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuthStore } from '@/lib/store';
import { Content, StepData, AVAILABLE_STYLES, AdInputs } from './types';
import GallerySelector from './components/GallerySelector';
import StyleSelector from './components/StyleSelector';
import GenerateButton from './components/GenerateButton';
import StepCard from './components/StepCard';
import AdInputForm from './components/AdInputForm';
import { API_URL } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const { token, user } = useAuthStore();
  const scrollRef = useRef<HTMLDivElement>(null);
  const isInitialized = useRef(false);

  // 핵심 상태만 유지
  const [steps, setSteps] = useState<StepData[]>([]);
  const [progress, setProgress] = useState(0);
  const [contents, setContents] = useState<Content[]>([]);
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<string>('');
  const [userPrompt, setUserPrompt] = useState('');
  const [finalImageUrl, setFinalImageUrl] = useState<string>('');
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const [adInputs, setAdInputs] = useState<AdInputs>({
    discount: '40% OFF',
    period: '',
    brand: 'SPRING SALE',
    keywords: '',
    mustInclude: '',
  });

  // ===== 초기화 =====
  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }
    
    if (!isInitialized.current) {
      isInitialized.current = true;
      
      addStep({
        id: 'select-image',
        title: '1️⃣ 이미지 선택',
        status: 'processing',
        content: null,
        timestamp: new Date(),
      });
      
      fetchContents();
    }
  }, []);

  // 자동 스크롤
  useEffect(() => {
    if (scrollRef.current) {
      setTimeout(() => {
        scrollRef.current?.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: 'smooth',
        });
      }, 100);
    }
  }, [steps]);

  // WebSocket cleanup
  useEffect(() => {
    return () => {
      if (wsConnection) {
        wsConnection.close();
        setWsConnection(null);
      }
    };
  }, [wsConnection]);

  // ===== Helper Functions =====
  const addStep = (step: StepData) => {
    setSteps(prev => [...prev, step]);
  };

  const updateStep = (id: string, updates: Partial<StepData>) => {
    setSteps(prev =>
      prev.map(step =>
        step.id === id ? { ...step, ...updates } : step
      )
    );
  };

  const fetchContents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/contents`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setContents(data);
      }
    } catch (error) {
      console.error('Failed to fetch contents:', error);
    }
  };

  // ===== Step 1: 이미지 선택 =====
  const handleSelectContent = (content: Content) => {
    setSelectedContent(content);
    setProgress(20);

    updateStep('select-image', {
      status: 'completed',
      content: (
        <div className="flex items-center gap-4">
          <div className="relative w-20 h-20 flex-shrink-0">
            <Image
              src={content.thumbnail_url || content.image_url}
              alt={content.product_name || ''}
              fill
              className="object-cover rounded-lg"
            />
          </div>
          <div>
            <p className="font-semibold text-gray-900">
              {content.product_name || '이름 없음'}
            </p>
            {content.category && (
              <p className="text-sm text-gray-500">{content.category}</p>
            )}
          </div>
        </div>
      ),
    });

    setTimeout(() => {
      addStep({
        id: 'select-style',
        title: '2️⃣ AI 스타일 선택',
        status: 'processing',
        content: null,
        timestamp: new Date(),
      });
    }, 300);
  };

  // ===== Step 2: 스타일 선택 =====
  const handleSelectStyle = (style: string) => {
    setSelectedStyle(style);
    setProgress(40);

    const selectedStyleData = AVAILABLE_STYLES.find(s => s.value === style);

    updateStep('select-style', {
      status: 'completed',
      content: (
        <div className="flex items-center gap-3">
          <span className="text-3xl">{selectedStyleData?.emoji}</span>
          <div>
            <p className="font-semibold text-gray-900">{selectedStyleData?.label}</p>
            <p className="text-sm text-gray-500">{selectedStyleData?.description}</p>
          </div>
        </div>
      ),
    });

    setTimeout(() => {
      addStep({
        id: 'generate',
        title: '3️⃣ AI 광고 생성',
        status: 'processing',
        content: null,
        timestamp: new Date(),
      });
    }, 300);
  };

  // ===== Step 3: 파이프라인 실행 =====
  const handleGenerate = async () => {
    if (!selectedContent || !selectedStyle) return;

    setProgress(50);

    updateStep('generate', {
      status: 'processing',
      content: (
        <div className="flex flex-col items-center py-8">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
          <p className="text-gray-600">AI 파이프라인이 광고를 생성하고 있습니다...</p>
          <p className="text-sm text-gray-500 mt-2">평균 2-3분 소요됩니다</p>
        </div>
      ),
    });

    try {
      const response = await fetch(`${API_URL}/api/v1/pipeline/run`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content_id: selectedContent.content_id,
          style: selectedStyle,
          user_prompt: userPrompt || undefined,
          ad_inputs: {
            discount: adInputs.discount || null,
            period: adInputs.period || null,
            brand: adInputs.brand || null,
            keywords: adInputs.keywords ? adInputs.keywords.split(',').map(k => k.trim()) : [],
            must_include: adInputs.mustInclude || null,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '파이프라인 실행 실패');
      }

      const data = await response.json();
      const { job_id } = data;

      // WebSocket 연결
      connectWebSocket(job_id);

    } catch (err: any) {
      console.error('Pipeline error:', err);
      updateStep('generate', {
        status: 'error',
        content: (
          <div className="text-red-600 text-center py-4">
            <p className="font-semibold">{err.message || '파이프라인 실행에 실패했습니다.'}</p>
          </div>
        ),
      });
    }
  };

  // ===== WebSocket 연결 =====
  const connectWebSocket = (jobId: string) => {
    const baseUrl = API_URL.replace(/\/$/, '');
    const wsUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
    const ws = new WebSocket(`${wsUrl}/api/v1/ws/pipeline/${jobId}`);
  
    ws.onopen = () => console.log('🔌 WebSocket 연결됨');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type !== 'ping') {
        handleWebSocketUpdate(data);
      }
    };
    ws.onerror = (error) => console.error('❌ WebSocket 에러:', error);
    ws.onclose = () => console.log('🔌 WebSocket 종료');

    setWsConnection(ws);
  };

  // ===== WebSocket 업데이트 처리 =====
  const handleWebSocketUpdate = (data: any) => {
    const { status, current_step, steps: pipelineSteps, final_image_url, error } = data;

    // 진행률 업데이트
    const progressValue = (current_step / 7) * 60 + 40;
    setProgress(Math.min(progressValue, 100));

    // 에러 처리
    if (status === 'failed') {
      updateStep('generate', {
        status: 'error',
        content: (
          <div className="text-red-600 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="font-semibold">❌ 오류 발생</p>
            <p className="text-sm mt-2">{error}</p>
          </div>
        ),
      });
      return;
    }

    // VTON 완료
    if (pipelineSteps?.virtual_fitting?.status === 'success') {
      const resultUrl = pipelineSteps.virtual_fitting.result_url;
      
      updateStep('generate', {
        status: 'completed',
        content: (
          <div className="space-y-4">
            <div className="relative w-full aspect-square max-w-2xl mx-auto">
              <Image
                src={resultUrl}
                alt="Generated Model"
                fill
                className="object-contain rounded-lg shadow-xl"
              />
            </div>
            <div className="text-center text-sm text-gray-600">
              <p>✅ AI 모델 착용 완료</p>
              <p className="text-xs text-gray-500 mt-1">배경 생성 중...</p>
            </div>
          </div>
        ),
      });
    }

    // 배경 생성 완료
    if (pipelineSteps?.generate_background?.status === 'success') {
      const bgUrl = pipelineSteps.generate_background.result_url;
      
      updateStep('generate', {
        status: 'completed',
        content: (
          <div className="space-y-4">
            <div className="relative w-full aspect-square max-w-2xl mx-auto">
              <Image
                src={bgUrl}
                alt="Background Generated"
                fill
                className="object-contain rounded-lg shadow-xl"
              />
            </div>
            <div className="text-center text-sm text-gray-600">
              <p>✅ 배경 생성 완료</p>
              <p className="text-xs text-gray-500 mt-1">광고 카피 생성 중...</p>
            </div>
          </div>
        ),
      });
    }

    // 최종 완료
    if (status === 'success' && final_image_url) {
      setFinalImageUrl(final_image_url);
      setProgress(100);
      
      addStep({
        id: 'final-result',
        title: '✅ 광고 생성 완료',
        status: 'completed',
        content: (
          <div className="space-y-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-bold text-xl text-green-900">광고 생성 완료!</h4>
                  <p className="text-green-700 text-sm">이미지가 준비되었습니다</p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3 text-gray-900">
                📸 최종 광고 이미지 (1080×1080px)
              </h4>
              <div className="border-4 border-gray-200 rounded-lg overflow-hidden shadow-xl">
                <Image
                  src={final_image_url}
                  alt="Final Ad"
                  width={1080}
                  height={1080}
                  className="w-full"
                />
              </div>
            </div>

            <div className="space-y-3">
              {/* 메인 액션 */}
              <a
                href={final_image_url}
                download
                className="w-full py-4 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg font-bold hover:from-green-700 hover:to-green-800 transition flex items-center justify-center gap-2 shadow-lg"
              >
                <span>✅</span>
                <span>승인하고 다운로드</span>
              </a>
              
              {/* 보조 액션 */}
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={handleRetry}
                  disabled={isRetrying}
                  className="py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span>🔄</span>
                  <span>{isRetrying ? '생성 중...' : '재시도'}</span>
                </button>
                
                <Link
                  href="/history"
                  className="py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition flex items-center justify-center gap-2"
                >
                  <span>📜</span>
                  <span>히스토리</span>
                </Link>
                
                <button
                  onClick={handleReset}
                  className="py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition flex items-center justify-center gap-2"
                >
                  <span>🎨</span>
                  <span>새로 만들기</span>
                </button>
              </div>
            </div>

            {/* 재시도 안내 */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mt-4">
              <h5 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
                <span>💡</span> 재시도 기능
              </h5>
              <div className="text-sm text-purple-800 space-y-1">
                <p>• 동일한 옷과 광고 정보로 AI가 다시 생성합니다</p>
                <p>• 가상 피팅, 배경, 카피가 모두 새롭게 만들어집니다</p>
                <p>• 결과가 마음에 안 들 때 여러 번 시도해보세요</p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h5 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <span>ℹ️</span> 이미지 정보
              </h5>
              <div className="text-sm text-blue-800 space-y-1">
                <p>• 해상도: 1080×1080px (Instagram 최적화)</p>
                <p>• 형식: PNG (고품질)</p>
              </div>
            </div>
          </div>
        ),
        timestamp: new Date(),
      });

      // WebSocket 종료
      if (wsConnection) {
        wsConnection.close();
        setWsConnection(null);
      }
    }
  };

  // ===== 재시도 =====
  const handleRetry = async () => {
    if (!selectedContent) return;
    
    setIsRetrying(true);
    
    // 기존 스텝 초기화
    setSteps([]);
    setProgress(0);
    setFinalImageUrl('');
    
    // 재시도 메시지
    addStep({
      id: 'retry',
      title: '🔄 재시도 중...',
      status: 'processing',
      content: (
        <div className="flex flex-col items-center py-8">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
          <p className="text-gray-600">동일한 설정으로 AI가 다시 생성하고 있습니다...</p>
          <p className="text-sm text-gray-500 mt-2">VTON, 배경, 카피가 모두 새롭게 생성됩니다</p>
        </div>
      ),
      timestamp: new Date(),
    });
    
    // 동일한 설정으로 다시 API 호출
    try {
      const response = await fetch(`${API_URL}/api/v1/pipeline/run`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content_id: selectedContent.content_id,
          style: selectedStyle,
          user_prompt: userPrompt || undefined,
          ad_inputs: {
            discount: adInputs.discount || null,
            period: adInputs.period || null,
            brand: adInputs.brand || null,
            keywords: adInputs.keywords ? adInputs.keywords.split(',').map(k => k.trim()) : [],
            must_include: adInputs.mustInclude || null,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('재시도 실패');
      }

      const data = await response.json();
      const { job_id } = data;

      // WebSocket 연결
      connectWebSocket(job_id);

    } catch (err: any) {
      console.error('Retry error:', err);
      updateStep('retry', {
        status: 'error',
        content: (
          <div className="text-red-600 text-center py-4">
            <p className="font-semibold">재시도에 실패했습니다.</p>
            <p className="text-sm mt-2">{err.message}</p>
          </div>
        ),
      });
    } finally {
      setIsRetrying(false);
    }
  };

  // ===== 리셋 =====
  const handleReset = () => {
    if (wsConnection) {
      wsConnection.close();
      setWsConnection(null);
    }
    
    setSteps([]);
    setProgress(0);
    setSelectedContent(null);
    setSelectedStyle('');
    setUserPrompt('');
    setFinalImageUrl('');
    
    addStep({
      id: 'select-image',
      title: '1️⃣ 이미지 선택',
      status: 'processing',
      content: null,
      timestamp: new Date(),
    });
  };

  // ===== 렌더링 =====
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* 진행바 */}
      <div className="sticky top-0 z-50 bg-white border-b shadow-sm">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4 mb-2">
            <h1 className="text-xl font-bold text-gray-900">AI 광고 생성</h1>
            <div className="flex-1"></div>
            <span className="text-sm font-medium text-gray-700">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* 스텝 영역 */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
          {steps.map((step, idx) => (
            <StepCard
              key={step.id}
              step={step}
              isLast={idx === steps.length - 1}
              onSelectImage={step.id === 'select-image' && step.status === 'processing' ? (
                <GallerySelector
                  contents={contents}
                  selectedContent={selectedContent}
                  onSelect={handleSelectContent}
                />
              ) : null}
              onSelectStyle={step.id === 'select-style' && step.status === 'processing' ? (
                <>
                  <AdInputForm
                    inputs={adInputs}
                    onChange={setAdInputs}
                  />
                  <StyleSelector
                    styles={AVAILABLE_STYLES}
                    selectedStyle={selectedStyle}
                    userPrompt={userPrompt}
                    onSelectStyle={handleSelectStyle}
                    onPromptChange={setUserPrompt}
                  />
                </>
              ) : null}
              onGenerate={step.id === 'generate' && step.status === 'processing' ? (
                <GenerateButton
                  onGenerate={handleGenerate}
                  disabled={!selectedContent || !selectedStyle}
                />
              ) : null}
            />
          ))}
        </div>
      </div>
    </div>
  );
}