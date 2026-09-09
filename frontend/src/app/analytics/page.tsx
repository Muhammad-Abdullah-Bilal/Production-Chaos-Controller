"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { BarChart3, Database, Sparkles, RefreshCw, Cpu, CheckCircle2, ShieldAlert } from "lucide-react";

export default function AnalyticsPage() {
  const [clickhouseStatus, setClickhouseStatus] = useState<any>(null);
  const [mcpManifest, setMcpManifest] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeQuery, setActiveQuery] = useState<string>("total_disruption_cost_summary");
  const [queryResult, setQueryResult] = useState<any>(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    Promise.all([
      api.getClickHouseStatus().catch(() => null),
      api.getClickHouseMcpManifest().catch(() => null),
      api.runClickHouseQuery("total_disruption_cost_summary").catch(() => null),
    ])
      .then(([status, mcp, initialQueryResult]) => {
        setClickhouseStatus(status);
        setMcpManifest(mcp);
        setQueryResult(initialQueryResult);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleQuery = async (queryName: string, params?: Record<string, any>) => {
    setActiveQuery(queryName);
    setIsQuerying(true);
    try {
      const res = await api.runClickHouseQuery(queryName, params);
      setQueryResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await api.syncClickHouse();
      const updatedStatus = await api.getClickHouseStatus();
      setClickhouseStatus(updatedStatus);
      alert("ClickHouse production warehouse successfully synced with latest events!");
    } catch (err) {
      alert("ClickHouse sync triggered.");
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-amber-400" />
          Production Analytics &amp; ClickHouse Data Warehouse
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          High-throughput analytical queries, disruption cost forecasting, resource vulnerability rankings, and official ClickHouse MCP integration.
        </p>
      </div>

      {/* ClickHouse Status & MCP Connection Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-slate-900 border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Database className="h-4 w-4 text-amber-400" /> ClickHouse Status
            </span>
            <Badge
              variant={clickhouseStatus?.data_source === "clickhouse" ? "success" : "warning"}
              className="text-[10px] font-mono"
            >
              {clickhouseStatus?.data_source === "clickhouse" ? "ONLINE CLUSTER" : "LOCAL CACHE"}
            </Badge>
          </div>
          <p className="text-sm font-bold text-white font-mono">
            {clickhouseStatus?.host || "localhost"}:{clickhouseStatus?.port || 8123}
          </p>
          <div className="text-[11px] text-slate-400 flex justify-between items-center border-t border-slate-800 pt-2">
            <span>Database: {clickhouseStatus?.database || "agentic_cinema"}</span>
            <Button size="sm" variant="ghost" onClick={handleSync} isLoading={isSyncing} className="h-6 text-[10px]">
              <RefreshCw className="h-3 w-3 mr-1" /> Sync Data
            </Button>
          </div>
        </Card>

        <Card className="p-4 bg-slate-900 border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Cpu className="h-4 w-4 text-indigo-400" /> ClickHouse MCP Protocol
            </span>
            <Badge variant="success" className="text-[10px] font-mono bg-indigo-950 text-indigo-300">
              ACTIVE MCP
            </Badge>
          </div>
          <p className="text-sm font-bold text-white">
            {mcpManifest?.mcp_version ? `ClickHouse MCP v${mcpManifest.mcp_version}` : "Antigravity Official MCP"}
          </p>
          <div className="text-[11px] text-slate-400 flex justify-between items-center border-t border-slate-800 pt-2">
            <span>Deterministic Tools Exposed: {mcpManifest?.tools?.length || 6}</span>
            <span className="text-emerald-400 font-mono text-[10px]">Connected</span>
          </div>
        </Card>

        <Card className="p-4 bg-slate-900 border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-purple-400" /> Analytics Query Engine
            </span>
            <Badge variant="info" className="text-[10px] font-mono">
              REAL-TIME
            </Badge>
          </div>
          <p className="text-sm font-bold text-white">6 Analytical Workloads</p>
          <div className="text-[11px] text-slate-400 border-t border-slate-800 pt-2">
            Low-latency scene move cost optimization &amp; resource risk scores.
          </div>
        </Card>
      </div>

      {/* Query Selector & Results */}
      <Card className="p-5 bg-slate-900/90 border-slate-800 space-y-4">
        <CardHeader className="px-0 pt-0 pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-amber-400" />
            ClickHouse Analytics Query Runner
          </CardTitle>
          <CardDescription className="text-xs">
            Execute analytical queries on the production schedule, actor scene dependencies, and disruption history.
          </CardDescription>
        </CardHeader>

        {/* 6 ClickHouse Query Buttons */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
          <button
            onClick={() => handleQuery("scenes_by_actor", { actor_id: "act_01" })}
            className={`p-2.5 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              activeQuery === "scenes_by_actor"
                ? "bg-indigo-600/30 border-indigo-500 text-white font-bold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            🎬 Actor Dependencies
          </button>
          <button
            onClick={() => handleQuery("scenes_by_equipment", { equipment_id: "eq_01" })}
            className={`p-2.5 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              activeQuery === "scenes_by_equipment"
                ? "bg-purple-600/30 border-purple-500 text-white font-bold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            🎥 Equipment Usage
          </button>
          <button
            onClick={() => handleQuery("top_frequent_locations", { limit: 5 })}
            className={`p-2.5 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              activeQuery === "top_frequent_locations"
                ? "bg-emerald-600/30 border-emerald-500 text-white font-bold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            📍 Location Freq
          </button>
          <button
            onClick={() => handleQuery("high_risk_disruption_resources")}
            className={`p-2.5 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              activeQuery === "high_risk_disruption_resources"
                ? "bg-rose-600/30 border-rose-500 text-white font-bold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            ⚠️ High Risk Resources
          </button>
          <button
            onClick={() => handleQuery("total_disruption_cost_summary")}
            className={`p-2.5 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              activeQuery === "total_disruption_cost_summary"
                ? "bg-amber-600/30 border-amber-500 text-white font-bold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            💰 Disruption Costs
          </button>
          <button
            onClick={() => handleQuery("lowest_impact_movable_scenes")}
            className={`p-2.5 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              activeQuery === "lowest_impact_movable_scenes"
                ? "bg-blue-600/30 border-blue-500 text-white font-bold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            ⚡ Lowest Impact Movable
          </button>
        </div>

        {/* Results Viewer */}
        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-indigo-400 uppercase">
              EXECUTED QUERY: {activeQuery}
            </span>
            <Badge
              variant={queryResult?.data_source === "clickhouse" ? "success" : "warning"}
              className="text-[10px] font-mono"
            >
              {queryResult?.data_source === "clickhouse" ? "📊 CLICKHOUSE CLUSTER RESULT" : "📁 LOCAL FALLBACK CACHE"}
            </Badge>
          </div>

          {isQuerying ? (
            <div className="p-8 text-center text-xs text-slate-500 font-mono">Running ClickHouse analytical query...</div>
          ) : queryResult ? (
            <pre className="text-xs text-slate-200 font-mono overflow-x-auto p-3 bg-slate-900/80 rounded-lg max-h-96">
              {JSON.stringify(queryResult, null, 2)}
            </pre>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500 font-mono">No query results available.</div>
          )}
        </div>
      </Card>
    </div>
  );
}
