import { Suspense } from "react";
import BuilderClient from "./BuilderClient";
import { Loader2 } from "lucide-react";

function BuilderLoading() {
  return (
    <div className="flex h-screen items-center justify-center bg-base">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-6 h-6 text-signal animate-spin" />
        <span className="text-xs text-text-muted">Loading builder…</span>
      </div>
    </div>
  );
}

interface BuilderPageProps {
  searchParams: Promise<{ prompt?: string; name?: string }>;
}

export default async function BuilderPage({ searchParams }: BuilderPageProps) {
  const params = await searchParams;
  return (
    <Suspense fallback={<BuilderLoading />}>
      <BuilderClient initialPrompt={params.prompt} initialName={params.name} />
    </Suspense>
  );
}
