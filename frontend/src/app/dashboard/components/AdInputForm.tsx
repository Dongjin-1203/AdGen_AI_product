"use client";

import React from 'react';

export interface AdInputs {
  discount: string;
  period: string;
  brand: string;
  keywords: string;
  mustInclude: string;
}

interface AdInputFormProps {
  inputs: AdInputs;
  onChange: (inputs: AdInputs) => void;
}

export default function AdInputForm({ inputs, onChange }: AdInputFormProps) {
  const handleChange = (field: keyof AdInputs, value: string) => {
    onChange({
      ...inputs,
      [field]: value,
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">📝</span>
        <h2 className="text-xl font-bold text-gray-900">광고 정보 입력</h2>
      </div>
      
      <p className="text-sm text-gray-600 mb-6">
        AI가 자동으로 광고를 생성하지만, 아래 정보를 입력하면 더 정확한 광고를 만들 수 있어요.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 할인율 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            💰 할인율
          </label>
          <input
            type="text"
            value={inputs.discount}
            onChange={(e) => handleChange('discount', e.target.value)}
            placeholder="예: 40% OFF, 50% 할인"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* 기간 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📅 할인 기간
          </label>
          <input
            type="text"
            value={inputs.period}
            onChange={(e) => handleChange('period', e.target.value)}
            placeholder="예: 03.20 - 03.27"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* 브랜드명 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🏷️ 브랜드/이벤트명
          </label>
          <input
            type="text"
            value={inputs.brand}
            onChange={(e) => handleChange('brand', e.target.value)}
            placeholder="예: SPRING SALE, NEW ARRIVAL"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* 키워드 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🔑 키워드 (쉼표로 구분)
          </label>
          <input
            type="text"
            value={inputs.keywords}
            onChange={(e) => handleChange('keywords', e.target.value)}
            placeholder="예: 시원함, 여름, 리조트"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* 필수 포함 문구 (전체 너비) */}
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ✨ 반드시 포함할 문구 (선택)
        </label>
        <textarea
          value={inputs.mustInclude}
          onChange={(e) => handleChange('mustInclude', e.target.value)}
          placeholder="예: 이번 시즌 최대 할인, 한정 수량"
          rows={2}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
      </div>

      {/* 도움말 */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-800">
          💡 <strong>팁:</strong> 입력하지 않아도 AI가 자동으로 생성합니다. 
          특정 문구를 꼭 넣고 싶을 때만 입력하세요!
        </p>
      </div>
    </div>
  );
}