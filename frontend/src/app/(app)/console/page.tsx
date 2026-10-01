import ConsoleClient from "./ConsoleClient";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<{ run?: string }>;
}

export default async function Page({ searchParams }: PageProps) {
  const params = await searchParams;
  return <ConsoleClient initialRunId={params.run ?? null} />;
}
