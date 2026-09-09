"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Calendar,
  Film,
  Users,
  AlertTriangle,
  GitMerge,
  BarChart3,
  Clapperboard,
  Database,
  Cpu,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Production Schedule", href: "/schedule", icon: Calendar },
  { label: "Scenes", href: "/scenes", icon: Film },
  { label: "Resources", href: "/resources", icon: Users },
  { label: "Disruptions", href: "/disruptions", icon: AlertTriangle },
  { label: "Recovery Plans", href: "/recovery", icon: GitMerge },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Studio Branding */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
          <div className="h-9 w-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <Clapperboard className="h-5 w-5" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-wide text-white block">
              CHAOS CONTROLLER
            </span>
            <span className="text-[10px] uppercase font-mono tracking-wider text-indigo-400 block">
              Film Ops Agent
            </span>
          </div>
        </div>

        {/* Navigation items */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                  isActive
                    ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                )}
              >
                <Icon className={cn("h-4 w-4", isActive ? "text-indigo-400" : "text-slate-500")} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Integration Badges */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 space-y-2">
        <div className="flex items-center justify-between text-[11px] text-slate-400 px-2 py-1 rounded bg-slate-900/80 border border-slate-800">
          <span className="flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-indigo-400" />
            Gemini / ADK
          </span>
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-400 px-2 py-1 rounded bg-slate-900/80 border border-slate-800">
          <span className="flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5 text-amber-400" />
            ClickHouse MCP
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Ready</span>
        </div>
      </div>
    </aside>
  );
}
