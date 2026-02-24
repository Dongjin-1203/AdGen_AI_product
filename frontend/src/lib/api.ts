import axios from 'axios';
import { User, SignupRequest, Token, Content, History } from '@/types';

// 백엔드 환경변수 지정
export const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

console.log('🔍 API_URL:', API_URL);

export const api = axios.create({
  baseURL: API_URL,
  timeout: 180000,  // ⭐ 180초 (3분) 추가!
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  // 브라우저 환경에서만 localStorage 접근
  if (typeof window !== 'undefined') {
    const storage = localStorage.getItem('auth-storage');
    if (storage) {
      try {
        const { state } = JSON.parse(storage);
        if (state?.token) {
          config.headers.Authorization = `Bearer ${state.token}`;
          console.log('🔐 API 요청에 토큰 포함됨');
        } else {
          console.warn('⚠️ 토큰이 없습니다');
        }
      } catch (e) {
        console.error('❌ localStorage 파싱 실패:', e);
      }
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('❌ 인증 실패 (401)');
      // 로그인 페이지로 리다이렉트
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (data: SignupRequest) => api.post<User>('/api/v1/signup', data),
  login: (data: FormData) => api.post<Token>('/api/v1/login', data),
  getMe: () => api.get<User>('/api/v1/me'),
};

export const contentAPI = {
  upload: (formData: FormData) => api.post<Content>('/api/v1/contents/upload', formData),
  getAll: () => api.get<Content[]>('/api/v1/contents'),
  getOne: (id: string) => api.get<Content>(`/api/v1/contents/${id}`),
  update: (id: string, data: any) => api.patch(`/api/v1/contents/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/contents/${id}`),
};

export const historyAPI = {
  // 사용자별 히스토리 조회
  getByUserId: (userId: string) => api.get<History[]>(`/api/v1/history/${userId}`),
  
  // 히스토리 삭제
  delete: (historyId: string) => api.delete(`/api/v1/history/${historyId}`),
};