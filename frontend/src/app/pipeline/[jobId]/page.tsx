'use client';

import { useParams } from 'next/navigation';
import PipelineMonitor from '@/components/pipeline/PipelineMonitor';

export default function PipelinePage() {
  const params = useParams();
  const jobId = params.jobId as string;

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <PipelineMonitor jobId={jobId} apiBaseUrl={apiBaseUrl} />
      </div>
    </main>
  );
}