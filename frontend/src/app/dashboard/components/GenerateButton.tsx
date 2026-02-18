interface GenerateButtonProps {
  onGenerate: () => void;
  disabled: boolean;
}

export default function GenerateButton({ onGenerate, disabled }: GenerateButtonProps) {
  return (
    <button
      type="button"
      onClick={onGenerate}
      disabled={disabled}
      className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl text-lg font-bold hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition shadow-lg"
    >
      {disabled ? '이미지와 스타일을 선택하세요' : '🚀 AI 광고 생성 시작'}
    </button>
  );
}