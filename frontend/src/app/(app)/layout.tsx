import AppSidebar from "@/components/AppSidebar";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AppSidebar />
      <main className="flex-1 overflow-auto pb-14 md:pb-0">{children}</main>
    </>
  );
}
