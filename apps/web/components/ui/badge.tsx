import type { ReactNode } from "react";

import { cn } from "../../lib/utils";

export default function Badge({
  children,
  variant = "default"
}: {
  children: ReactNode;
  variant?: "default" | "outline";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
        variant === "default"
          ? "bg-ink text-white"
          : "border border-slate/40 text-slate"
      )}
    >
      {children}
    </span>
  );
}
