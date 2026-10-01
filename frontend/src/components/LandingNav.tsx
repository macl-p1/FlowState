"use client";

import Link from "next/link";
import { Workflow, Menu, X } from "lucide-react";
import { useState } from "react";

const navLinks = [
  { href: "#how-it-works", label: "How it works" },
  { href: "#templates", label: "Templates" },
  { href: "/dashboard", label: "Sign in" },
];

export default function LandingNav() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-base/80 backdrop-blur-sm">
      <div className="mx-auto max-w-6xl px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-text flex items-center justify-center">
            <Workflow className="w-4 h-4 text-base" strokeWidth={2.5} />
          </div>
          <span className="text-text font-semibold text-base tracking-tight">
            FlowState
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-7">
          {navLinks.map((link) =>
            link.href.startsWith("#") ? (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-text-muted hover:text-text transition-colors duration-200"
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm text-text-muted hover:text-text transition-colors duration-200"
              >
                {link.label}
              </Link>
            )
          )}
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden p-1.5 text-text-muted hover:text-text"
          onClick={() => setOpen(!open)}
        >
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden border-t border-border bg-base px-6 py-4 flex flex-col gap-3">
          {navLinks.map((link) =>
            link.href.startsWith("#") ? (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-text-muted hover:text-text transition-colors"
                onClick={() => setOpen(false)}
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm text-text-muted hover:text-text transition-colors"
                onClick={() => setOpen(false)}
              >
                {link.label}
              </Link>
            )
          )}
        </div>
      )}
    </nav>
  );
}
