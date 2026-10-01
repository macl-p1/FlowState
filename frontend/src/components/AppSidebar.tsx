"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Workflow,
  Terminal,
  Puzzle,
  RefreshCw,
  BarChart3,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, mobileLabel: "Dash" },
  { href: "/builder", label: "Workflows", icon: Workflow, mobileLabel: "Flows" },
  { href: "/console", label: "Console", icon: Terminal, mobileLabel: "Run" },
  { href: "/tools", label: "Tools", icon: Puzzle, mobileLabel: "Tools" },
  { href: "/history", label: "History", icon: RefreshCw, mobileLabel: "Logs" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, mobileLabel: "Stats" },
];

export default function AppSidebar() {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-60 flex-col border-r border-border bg-surface/50 shrink-0">
        <div className="p-4">
          <Link
            href="/"
            className="flex items-center gap-2.5 mb-6 px-1 hover:opacity-80 transition-opacity"
          >
            <div className="w-6 h-6 rounded-md bg-text flex items-center justify-center">
              <Workflow className="w-3.5 h-3.5 text-base" strokeWidth={2.5} />
            </div>
            <span className="text-text font-semibold text-sm tracking-tight">
              FlowState
            </span>
          </Link>

          <nav className="flex flex-col gap-0.5">
            {navItems.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" &&
                  pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm transition-colors ${
                    isActive
                      ? "bg-surface-2 text-text"
                      : "text-text-muted hover:text-text hover:bg-surface-2"
                  }`}
                >
                  <item.icon className="w-4 h-4 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="mt-auto p-4 border-t border-border">
          <div className="flex items-center gap-2.5 px-2.5 py-2 text-text-muted text-sm">
            <div className="w-6 h-6 rounded-full bg-surface-2 flex items-center justify-center">
              <span className="text-xs font-medium">GA</span>
            </div>
            <span className="truncate">gaura@acme.co</span>
          </div>
        </div>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-base/90 backdrop-blur-sm">
        <div className="flex items-center justify-around py-2">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" &&
                pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center gap-0.5 py-1.5 px-2 rounded-md transition-colors min-w-[56px] ${
                  isActive
                    ? "text-text bg-surface-2"
                    : "text-text-muted hover:text-text"
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="text-[10px]">{item.mobileLabel}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
