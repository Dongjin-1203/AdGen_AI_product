import Image from 'next/image';
import Link from 'next/link';
import { Content } from '../types';

interface GallerySelectorProps {
  contents: Content[];
  selectedContent: Content | null;
  onSelect: (content: Content) => void;
}

export default function GallerySelector({ contents, selectedContent, onSelect }: GallerySelectorProps) {
  if (contents.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">아직 업로드된 이미지가 없습니다</p>
        <Link
          href="/upload"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          이미지 업로드하기
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {contents.map((content) => (
        <button
          key={content.content_id}
          type="button"
          onClick={() => onSelect(content)}
          className={`relative aspect-square rounded-lg overflow-hidden border-4 transition ${
            selectedContent?.content_id === content.content_id
              ? 'border-blue-600 ring-2 ring-blue-300'
              : 'border-transparent hover:border-blue-300'
          }`}
        >
          <Image
            src={content.thumbnail_url || content.image_url}
            alt={content.product_name || '상품 이미지'}
            fill
            className="object-cover"
          />
          {content.product_name && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-2 truncate">
              {content.product_name}
            </div>
          )}
        </button>
      ))}
    </div>
  );
}