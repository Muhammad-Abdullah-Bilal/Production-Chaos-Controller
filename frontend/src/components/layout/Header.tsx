"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { HealthStatus } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Activity, ShieldCheck, Film } from "lucide-react";

export function Header() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [clickhouseStatus, setClickhouseStatus] = useState<string>("fallback");

  useEffect(() => {
    let isMounted = true;
    const checkBackend = async () => {
      try {
        const data = await api.getHealth();
        if (isMounted) {
          setHealth(data);
          setIsConnected(true);
        }
      } catch (err) {
        if (isMounted) {
          setIsConnected(false);
        }
      }

      try {
        const ch = await api.getClickHouseStatus();
        if (isMounted && ch) {
          setClickhouseStatus(ch.data_source || "fallback");
        }
      } catch {
        if (isMounted) {
          setClickhouseStatus("fallback");
        }
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Current Production */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <Film className="h-4 w-4 text-indigo-400" />
          <span className="font-semibold text-white">Project Nebula</span>
          <span className="text-slate-600">/</span>
          <span className="text-slate-400">Principal Photography</span>
        </div>
        <Badge variant="info" className="font-mono text-[10px]">
          DAY 1 OF 28
        </Badge>
      </div>

      {/* Status & Producer Profile */}
      <div className="flex items-center gap-4">
        {/* ClickHouse Data Source Indicator Badge */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-mono">Data Source:</span>
          {clickhouseStatus === "clickhouse" ? (
            <Badge variant="success" className="gap-1.5 font-mono text-[11px] bg-emerald-950/80 text-emerald-300 border-emerald-500/40">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              📊 ClickHouse (Active)
            </Badge>
          ) : (
            <Badge variant="warning" className="gap-1.5 font-mono text-[11px] bg-amber-950/80 text-amber-300 border-amber-500/40">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
              📁 Local Memory (Fallback)
            </Badge>
          )}
        </div>

        {/* Backend API Health Indicator */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-mono">Backend API:</span>
          {isConnected ? (
            <Badge variant="success" className="gap-1.5 font-mono text-[11px]">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ONLINE (FastAPI)
            </Badge>
          ) : (
            <Badge variant="danger" className="gap-1.5 font-mono text-[11px]">
              <span className="h-1.5 w-1.5 rounded-full bg-rose-400" />
              OFFLINE (Port 8000)
            </Badge>
          )}
        </div>

        {/* User / Producer Avatar */}
        <div className="flex items-center gap-2.5 pl-4 border-l border-slate-800">
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-xs font-bold text-white shadow-sm">
            LP
          </div>
          <div className="text-left">
            <span className="text-xs font-medium text-white block leading-tight">
              Marcus Webb
            </span>
            <span className="text-[10px] text-slate-400 block leading-tight">
              Line Producer
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
