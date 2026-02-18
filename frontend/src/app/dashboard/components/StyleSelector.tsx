import { StyleOption } from '../types';

interface StyleSelectorProps {
  styles: readonly StyleOption[];
  selectedStyle: string;
  userPrompt: string;
  onSelectStyle: (style: string) => void;
  onPromptChange: (prompt: string) => void;
}

export default function StyleSelector({
  styles,
  selectedStyle,
  userPrompt,
  onSelectStyle,
  onPromptChange,
}: StyleSelectorProps) {
  return (
    <div className="space-y-6">
      {/* 스타일 선택 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {styles.map((style) => (
          <button
            key={style.value}
            type="button"
            onClick={() => onSelectStyle(style.value)}
            className={`p-6 rounded-xl border-2 transition ${
              selectedStyle === style.value
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-blue-300 bg-white'
            }`}
          >
            <div className="text-5xl mb-3">{style.emoji}</div>
            <h3 className="font-bold text-lg mb-2">{style.label}</h3>
            <p className="text-sm text-gray-600">{style.description}</p>
          </button>
        ))}
      </div>

      {/* 추가 프롬프트 */}
      <div>
        <label htmlFor="user-prompt" className="block mb-2 text-sm font-medium text-gray-700">
          추가 요청사항 (선택)
        </label>
        <textarea
          id="user-prompt"
          value={userPrompt}
          onChange={(e) => onPromptChange(e.target.value)}
          className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
          rows={3}
          placeholder="예: 밝고 화사한 느낌으로, 고급스러운 분위기로..."
        />
        <p className="mt-2 text-xs text-gray-500">
          💡 원하는 분위기나 배경 요소를 자유롭게 입력하세요
        </p>
      </div>
    </div>
  );
}