import { StepData } from '../types';

interface StepCardProps {
  step: StepData;
  isLast: boolean;
  onSelectImage?: React.ReactNode;
  onSelectStyle?: React.ReactNode;
  onGenerate?: React.ReactNode;
}

export default function StepCard({
  step,
  isLast,
  onSelectImage,
  onSelectStyle,
  onGenerate,
}: StepCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 animate-slideUp">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-4">
        {step.status === 'completed' && (
          <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
        {step.status === 'processing' && (
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
        {step.status === 'error' && (
          <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )}
        {step.status === 'pending' && (
          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
            <div className="w-3 h-3 bg-white rounded-full"></div>
          </div>
        )}

        <h3 className="font-bold text-lg text-gray-900">{step.title}</h3>
      </div>

      {/* 컨텐츠 */}
      {step.content && (
        <div className="mb-4">
          {step.content}
        </div>
      )}

      {/* 액션 UI */}
      {onSelectImage && <div className="mt-4">{onSelectImage}</div>}
      {onSelectStyle && <div className="mt-4">{onSelectStyle}</div>}
      {onGenerate && <div className="mt-4">{onGenerate}</div>}

      {/* 연결선 (마지막 아님) */}
      {!isLast && (
        <div className="flex justify-center mt-6">
          <div className="w-0.5 h-8 bg-gray-300"></div>
        </div>
      )}
    </div>
  );
}