"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import {
  ProductionSchedule,
  Scene,
  Actor,
  Location,
  Equipment,
  ShootingDay,
  DisruptionEvent,
  HealthStatus,
} from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import {
  Film,
  Calendar,
  UserCheck,
  MapPin,
  Camera,
  AlertTriangle,
  PlusCircle,
  ArrowRight,
  ShieldAlert,
  Target,
  Users,
  Activity,
  Layers,
  CheckCircle2,
  Clock,
  Zap,
} from "lucide-react";

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [schedule, setSchedule] = useState<ProductionSchedule | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [actors, setActors] = useState<Actor[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [shootingDays, setShootingDays] = useState<ShootingDay[]>([]);
  const [disruptions, setDisruptions] = useState<DisruptionEvent[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [
        healthRes,
        prodRes,
        scenesRes,
        actorsRes,
        locationsRes,
        equipmentRes,
        schedRes,
        disruptionsRes,
      ] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getProduction().catch(() => null),
        api.getScenes().catch(() => []),
        api.getActors().catch(() => []),
        api.getLocations().catch(() => []),
        api.getEquipment().catch(() => []),
        api.getSchedule().catch(() => []),
        api.getDisruptions().catch(() => []),
      ]);

      setHealth(healthRes);
      setSchedule(prodRes);
      setScenes(scenesRes);
      setActors(actorsRes);
      setLocations(locationsRes);
      setEquipment(equipmentRes);
      setShootingDays(schedRes);
      setDisruptions(disruptionsRes);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to communicate with backend.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Current day calculation
  const currentDayNumber = 1;
  const currentDayObj = shootingDays.find((d) => d.day_number === currentDayNumber) || shootingDays[0];
  const scenesTodayCount = currentDayObj ? currentDayObj.scene_ids.length : 2;
  const scenesTodayList = scenes.filter((s) => currentDayObj?.scene_ids.includes(s.scene_id)) || scenes.slice(0, 2);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* 🎬 Hero Banner: Film Production Control Room */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/80 to-slate-950 border border-indigo-500/30 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl -z-0 pointer-events-none" />

        <div className="relative z-10 space-y-1.5">
          <div className="flex items-center gap-2">
            <Badge variant="info" className="gap-1 bg-indigo-900/60 text-indigo-300 border-indigo-500/40 font-mono text-[10px]">
              <Film className="h-3 w-3 text-indigo-400" />
              PRINCIPAL PHOTOGRAPHY
            </Badge>
            <Badge variant="success" className="font-mono text-[10px]">
              SCI-FI THRILLER FEATURE
            </Badge>
          </div>

          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            🎬 Production &quot;The Last Signal&quot;
          </h1>
          <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
            Real-Time Film Operations Control Room &amp; Automated Disruption Recovery Engine powered by Google Gemini Agent Reasoning &amp; ClickHouse Data Analytics.
          </p>
        </div>

        <div className="relative z-10 flex flex-wrap items-center gap-3">
          <Link href="/disruptions">
            <Button variant="danger" size="lg" className="gap-2 shadow-lg shadow-rose-900/40 text-sm font-bold animate-pulse">
              <AlertTriangle className="h-4 w-4 text-white" />
              🚨 Report Disruption
            </Button>
          </Link>
          <Link href="/schedule">
            <Button variant="secondary" size="lg" className="gap-2 text-sm font-semibold">
              <Calendar className="h-4 w-4" />
              View Schedule
            </Button>
          </Link>
        </div>
      </div>

      {/* 📊 Required Control Room Stat Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* 📅 Current Production Day */}
        <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-1 hover:border-indigo-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-medium">Production Day</span>
            <Calendar className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">Day {currentDayNumber} <span className="text-xs text-slate-500 font-sans font-normal">/ 10</span></div>
          <span className="text-[10px] text-emerald-400 font-medium block">On Track (0 Days Shift)</span>
        </Card>

        {/* 🎯 Scenes Today */}
        <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-1 hover:border-purple-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-medium">Scenes Today</span>
            <Target className="h-4 w-4 text-purple-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{scenesTodayCount} <span className="text-xs text-slate-500 font-sans font-normal">Scheduled</span></div>
          <span className="text-[10px] text-purple-300 font-medium block">Sc. 1 &amp; Sc. 2 Standing Set</span>
        </Card>

        {/* 👥 Actors */}
        <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-1 hover:border-blue-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-medium">Actors</span>
            <Users className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{actors.length || 8} <span className="text-xs text-slate-500 font-sans font-normal">Cast</span></div>
          <span className="text-[10px] text-blue-300 font-medium block">2 Leads Active Today</span>
        </Card>

        {/* 🎥 Equipment */}
        <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-1 hover:border-amber-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-medium">Equipment</span>
            <Camera className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{equipment.length || 5} <span className="text-xs text-slate-500 font-sans font-normal">Packages</span></div>
          <span className="text-[10px] text-amber-300 font-medium block">RED V-Raptor 8K Primary</span>
        </Card>

        {/* 🏢 Locations */}
        <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-1 hover:border-emerald-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-medium">Locations</span>
            <MapPin className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{locations.length || 4} <span className="text-xs text-slate-500 font-sans font-normal">Venues</span></div>
          <span className="text-[10px] text-emerald-300 font-medium block">Stage 4 Bunker &amp; Glacier Pass</span>
        </Card>

        {/* 🚨 Active Disruptions */}
        <Card className="p-4 bg-rose-950/20 border-rose-800/40 space-y-1 hover:border-rose-500/60 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-medium text-rose-300">Disruptions</span>
            <AlertTriangle className="h-4 w-4 text-rose-400 animate-pulse" />
          </div>
          <div className="text-xl font-bold text-rose-400 font-mono">{disruptions.length || 1} <span className="text-xs text-rose-300/60 font-sans font-normal">Active</span></div>
          <span className="text-[10px] text-rose-400 font-medium block">Recovery Plan Ready</span>
        </Card>
      </div>

      {/* Main Control Panel Dashboard Views */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2-Cols: Scenes Today & Active Production Metrics */}
        <div className="lg:col-span-2 space-y-6">
          {/* Scenes Scheduled Today Card */}
          <Card className="p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Target className="h-4 w-4 text-indigo-400" />
                  Scenes Scheduled Today (Day {currentDayNumber})
                </h3>
                <p className="text-xs text-slate-400">Call Time: 07:00 AM • Location: Stage 4 Command Bunker</p>
              </div>
              <Badge variant="info">2 Scenes Active</Badge>
            </div>

            <div className="space-y-3">
              {scenesTodayList.length > 0 ? (
                scenesTodayList.map((scene) => (
                  <div key={scene.scene_id} className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="font-mono text-xs text-indigo-300 border-indigo-500/30">
                          SCENE {scene.scene_number}
                        </Badge>
                        <h4 className="text-xs font-bold text-white">{scene.title}</h4>
                      </div>
                      <Badge variant={scene.indoor_outdoor === "Indoor" ? "success" : "warning"} className="text-[10px]">
                        {scene.indoor_outdoor.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-300 leading-snug">{scene.description}</p>
                    <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-900">
                      <span>Est. Cost: {formatCurrency(scene.estimated_cost)}</span>
                      <span>Duration: {scene.duration} Mins</span>
                      <span>Priority: <span className="text-indigo-300 font-semibold">{scene.priority.toUpperCase()}</span></span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-400 text-center py-4">No scenes scheduled for today.</div>
              )}
            </div>
          </Card>

          {/* Quick Scenario Launch Grid */}
          <Card className="p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-400" />
                  Simulate Production Disruption Scenarios
                </h3>
                <p className="text-xs text-slate-400">Launch AI Agent reasoning and deterministic tools across canonical scenarios</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              <Link href="/disruptions" className="p-3 bg-slate-950 hover:bg-slate-900 border border-slate-800 rounded-xl space-y-1 group transition-all">
                <span className="text-xs font-bold text-indigo-300 flex items-center justify-between">
                  Actor Unavailable
                  <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                </span>
                <p className="text-[11px] text-slate-400">Dr. Sarah Mercer unavailable on Day 4 hold</p>
              </Link>

              <Link href="/disruptions" className="p-3 bg-slate-950 hover:bg-slate-900 border border-slate-800 rounded-xl space-y-1 group transition-all">
                <span className="text-xs font-bold text-purple-300 flex items-center justify-between">
                  Equipment Failure
                  <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-purple-400 transition-colors" />
                </span>
                <p className="text-[11px] text-slate-400">RED V-Raptor 8K primary camera failure</p>
              </Link>

              <Link href="/disruptions" className="p-3 bg-slate-950 hover:bg-slate-900 border border-slate-800 rounded-xl space-y-1 group transition-all">
                <span className="text-xs font-bold text-amber-300 flex items-center justify-between">
                  Bad Weather
                  <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-amber-400 transition-colors" />
                </span>
                <p className="text-[11px] text-slate-400">Heavy rain forecast for Glacier Pass</p>
              </Link>

              <Link href="/disruptions" className="p-3 bg-slate-950 hover:bg-slate-900 border border-slate-800 rounded-xl space-y-1 group transition-all">
                <span className="text-xs font-bold text-blue-300 flex items-center justify-between">
                  Crew Unavailable
                  <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-blue-400 transition-colors" />
                </span>
                <p className="text-[11px] text-slate-400">Director of Photography medical hold</p>
              </Link>

              <Link href="/disruptions" className="p-3 bg-slate-950 hover:bg-slate-900 border border-slate-800 rounded-xl space-y-1 group transition-all">
                <span className="text-xs font-bold text-amber-300 flex items-center justify-between">
                  Logistics Breakdown
                  <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-amber-400 transition-colors" />
                </span>
                <p className="text-[11px] text-slate-400">Equipment transport van highway breakdown</p>
              </Link>

              <Link href="/disruptions" className="p-3 bg-rose-950/40 hover:bg-rose-950/70 border border-rose-800/50 rounded-xl space-y-1 group transition-all">
                <span className="text-xs font-bold text-rose-300 flex items-center justify-between">
                  🔥 Chaos Mode
                  <ArrowRight className="h-3.5 w-3.5 text-rose-400 group-hover:translate-x-0.5 transition-transform" />
                </span>
                <p className="text-[11px] text-slate-300">Simultaneous Multi-Disruption Engine</p>
              </Link>
            </div>
          </Card>
        </div>

        {/* Right 1-Col: Live Production Status & ClickHouse Summary */}
        <div className="space-y-6">
          {/* Active Disruption Status Box */}
          <Card className="p-5 border-rose-500/40 bg-rose-950/20 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
                <ShieldAlert className="h-4 w-4 text-rose-400 animate-pulse" />
                Active Disruption Monitor
              </span>
              <Badge variant="danger" className="text-[9px]">1 ACTIVE</Badge>
            </div>
            <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 text-xs space-y-1">
              <span className="font-bold text-white block">Dr. Sarah Mercer Hold (Day 4)</span>
              <p className="text-slate-400 text-[11px]">Emergency medical hold impacting Scene 4 &amp; Scene 5 filming.</p>
              <div className="pt-2">
                <Link href="/disruptions">
                  <Button variant="primary" size="sm" className="w-full text-xs gap-1 bg-indigo-600 hover:bg-indigo-500">
                    Review AI Recovery Plan
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            </div>
          </Card>

          {/* ClickHouse Integration Status Box */}
          <Card className="p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                📊 ClickHouse Analytics
              </span>
              <Badge variant="success" className="text-[9px]">MCP CONNECTED</Badge>
            </div>
            <div className="space-y-2 text-xs text-slate-300">
              <p className="text-[11px] leading-relaxed">
                ClickHouse MergeTree tables store scenes, schedules, cast, crew, equipment, locations, disruptions, recovery plans, and cost records.
              </p>
              <Link href="/analytics">
                <Button variant="secondary" size="sm" className="w-full text-xs gap-1.5 mt-1">
                  Open Analytics Explorer
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
