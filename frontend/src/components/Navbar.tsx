'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';

export default function Navbar() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/dashboard" className="text-2xl font-bold text-blue-600 hover:text-blue-700 transition">
            AdGen AI
          </Link>
          
          <div className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              대시보드
            </Link>
            <Link
              href="/upload"
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              업로드
            </Link>
            <Link
              href="/gallery"
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              갤러리
            </Link>
            <Link
              href="/history"
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              VTON 히스토리
            </Link>
            <Link
              href="/ad-history"
              className="text-gray-700 hover:text-blue-600 font-medium transition"
            >
              📋 광고 히스토리
            </Link>
            
            {user && (
              <div className="flex items-center gap-4 pl-4 border-l border-gray-300">
                <span className="text-gray-600">{user.name}님</span>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}