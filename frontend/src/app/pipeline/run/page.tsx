'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { pipelineAPI } from '@/lib/api';

export default function PipelineRunPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    content_id: '',
    style: 'resort' as 'resort' | 'retro' | 'romantic',
    model_index: undefined as number | undefined,
    user_prompt: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await pipelineAPI.run({
        content_id: formData.content_id,
        style: formData.style,
        model_index: formData.model_index,
        user_prompt: formData.user_prompt || undefined,
      });

      const { job_id } = response.data;
      
      // 모니터링 페이지로 이동
      router.push(`/pipeline/${job_id}`);
    } catch (err: any) {
      console.error('파이프라인 실행 실패:', err);
      setError(err.response?.data?.detail || '파이프라인 실행에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">
            파이프라인 실행
          </h1>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Content ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content ID *
              </label>
              <input
                type="text"
                required
                value={formData.content_id}
                onChange={(e) => setFormData({ ...formData, content_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="업로드한 상품 이미지 ID"
              />
            </div>

            {/* Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                스타일 *
              </label>
              <select
                value={formData.style}
                onChange={(e) => setFormData({ ...formData, style: e.target.value as any })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="resort">Resort (리조트)</option>
                <option value="retro">Retro (레트로)</option>
                <option value="romantic">Romantic (로맨틱)</option>
              </select>
            </div>

            {/* Model Index */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                모델 인덱스 (선택사항)
              </label>
              <input
                type="number"
                min="0"
                value={formData.model_index || ''}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  model_index: e.target.value ? parseInt(e.target.value) : undefined 
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="비워두면 랜덤 선택"
              />
            </div>

            {/* User Prompt */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                추가 요청사항 (선택사항)
              </label>
              <textarea
                value={formData.user_prompt}
                onChange={(e) => setFormData({ ...formData, user_prompt: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder="예: 밝고 화사한 느낌으로"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {loading ? '실행 중...' : '파이프라인 실행'}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}