import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { HealthStatus } from "@/lib/types";
import { Server, Cpu, Database, ExternalLink, RefreshCw } from "lucide-react";

interface SystemHealthBannerProps {
  health: HealthStatus | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export function SystemHealthBanner({ health, isLoading, onRefresh }: SystemHealthBannerProps) {
  const isHealthy = health?.status === "healthy";

  return (
    <Card className="border-indigo-900/30 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* API Backend Info */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Server className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white">
                {health?.service || "Production Chaos Controller API"}
              </span>
              <Badge variant={isHealthy ? "success" : "danger"} className="font-mono text-[10px]">
                {isHealthy ? "BACKEND ONLINE" : "OFFLINE / DISCONNECTED"}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              FastAPI Engine (Port 8000) • Python 3.12 (uv) • REST API
            </p>
          </div>
        </div>

        {/* Subsystem Readiness Indicators */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          {/* Gemini / ADK Subsystem */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/70 border border-slate-800">
            <Cpu className="h-4 w-4 text-indigo-400" />
            <div>
              <span className="text-slate-400 block text-[10px]">AI AGENT ENGINE</span>
              <span className="font-medium text-white">
                Gemini Tools ({health?.integrations?.agent_orchestrator?.registered_tools_count ?? 4} Registered)
              </span>
            </div>
          </div>

          {/* ClickHouse Subsystem */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/70 border border-slate-800">
            <Database className="h-4 w-4 text-amber-400" />
            <div>
              <span className="text-slate-400 block text-[10px]">PARTNER INTEGRATION</span>
              <span className="font-medium text-white">
                ClickHouse MCP ({health?.integrations?.clickhouse?.status ?? "Ready"})
              </span>
            </div>
          </div>

          {/* Docs & Refresh */}
          <div className="flex items-center gap-2">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700 transition-colors"
            >
              API Docs
              <ExternalLink className="h-3 w-3" />
            </a>
            <button
              onClick={onRefresh}
              disabled={isLoading}
              title="Refresh health status"
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
}
