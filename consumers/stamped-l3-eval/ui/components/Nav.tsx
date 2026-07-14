"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/corpus", label: "Corpus" },
  { href: "/detectors", label: "Detectors" },
  { href: "/compare", label: "Compare" },
  { href: "/live", label: "Live" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <nav className="nav" aria-label="Lab">
      <p className="brand">Stamped · L3 Lab</p>
      {LINKS.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          aria-current={pathname.startsWith(l.href) ? "page" : undefined}
        >
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
