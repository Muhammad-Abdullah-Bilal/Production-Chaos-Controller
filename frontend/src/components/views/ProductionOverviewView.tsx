"use client";

import { ProductionSchedule } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import {
  Film,
  UserCheck,
  Users,
  MapPin,
  Camera,
  Calendar,
  DollarSign,
  CloudRain,
  ShieldAlert,
} from "lucide-react";

interface Props {
  schedule: ProductionSchedule | null;
}

export function ProductionOverviewView({ schedule }: Props) {
  if (!schedule) {
    return (
      <Card className="p-8 text-center text-slate-400">
        Loading &quot;The Last Signal&quot; production overview...
      </Card>
    );
  }

  const outdoorScenes = schedule.scenes.filter((s) => s.indoor_outdoor === "Outdoor");
  const weatherSensitiveScenes = schedule.scenes.filter((s) => s.weather_sensitive);
  const totalSceneCost = schedule.scenes.reduce((acc, s) => acc + s.estimated_cost, 0);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-xl bg-gradient-to-r from-indigo-950 via-slate-900 to-slate-950 border border-indigo-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Film className="h-6 w-6 text-indigo-400" />
            <h1 className="text-2xl font-bold text-white tracking-tight">{schedule.project_title}</h1>
            <Badge variant="info">FEATURE FILM</Badge>
          </div>
          <p className="text-xs text-slate-400">
            Director: <span className="text-white font-medium">{schedule.director}</span> • Line Producer:{" "}
            <span className="text-white font-medium">{schedule.producer}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-2 bg-slate-950/80 rounded-lg border border-slate-800 text-right">
            <span className="text-[10px] text-slate-500 uppercase block">Total Budget</span>
            <span className="text-base font-bold text-emerald-400">{formatCurrency(schedule.total_budget)}</span>
          </div>
          <div className="px-3 py-2 bg-slate-950/80 rounded-lg border border-slate-800 text-right">
            <span className="text-[10px] text-slate-500 uppercase block">Burn Rate</span>
            <span className="text-base font-bold text-indigo-300">{formatCurrency(schedule.daily_burn_rate)} / day</span>
          </div>
        </div>
      </div>

      {/* Production Stats Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <Card className="p-3.5 text-center">
          <Film className="h-4 w-4 text-indigo-400 mx-auto mb-1" />
          <span className="text-xl font-bold text-white block">{schedule.scenes.length}</span>
          <span className="text-[11px] text-slate-400">Total Scenes</span>
        </Card>
        <Card className="p-3.5 text-center">
          <UserCheck className="h-4 w-4 text-emerald-400 mx-auto mb-1" />
          <span className="text-xl font-bold text-white block">{schedule.actors.length}</span>
          <span className="text-[11px] text-slate-400">Cast Members</span>
        </Card>
        <Card className="p-3.5 text-center">
          <Users className="h-4 w-4 text-blue-400 mx-auto mb-1" />
          <span className="text-xl font-bold text-white block">{schedule.crew.length}</span>
          <span className="text-[11px] text-slate-400">Crew Depts</span>
        </Card>
        <Card className="p-3.5 text-center">
          <MapPin className="h-4 w-4 text-amber-400 mx-auto mb-1" />
          <span className="text-xl font-bold text-white block">{schedule.locations.length}</span>
          <span className="text-[11px] text-slate-400">Locations</span>
        </Card>
        <Card className="p-3.5 text-center">
          <Camera className="h-4 w-4 text-purple-400 mx-auto mb-1" />
          <span className="text-xl font-bold text-white block">{schedule.equipment.length}</span>
          <span className="text-[11px] text-slate-400">Eq Packages</span>
        </Card>
        <Card className="p-3.5 text-center">
          <Calendar className="h-4 w-4 text-rose-400 mx-auto mb-1" />
          <span className="text-xl font-bold text-white block">{schedule.shooting_days.length}</span>
          <span className="text-[11px] text-slate-400">Shoot Days</span>
        </Card>
      </div>

      {/* Production Risk & Breakdown Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="font-semibold text-white text-sm flex items-center gap-2">
              <CloudRain className="h-4 w-4 text-amber-400" />
              Weather Vulnerability &amp; Location Exposure
            </span>
            <Badge variant="warning">{weatherSensitiveScenes.length} Sensitive Scenes</Badge>
          </div>
          <div className="space-y-3 text-xs text-slate-300">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex justify-between font-medium text-white">
                <span>Alpine Ridge Summit (EXT)</span>
                <span className="text-amber-400 font-mono">6 Scenes</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                High altitude platform. High risk of wind shear &amp; blizzard disruptions.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex justify-between font-medium text-white">
                <span>Glacier Ridge Pass (EXT)</span>
                <span className="text-rose-400 font-mono">3 Scenes</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Helicopter drop zone. Strict weather clearance required for flight safety.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex justify-between font-medium text-white">
                <span>Stage Cover Sets (INT Soundstages)</span>
                <span className="text-emerald-400 font-mono">11 Scenes</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Command Bunker &amp; Quantum Vault sets. Available as backup cover sets during weather holds.
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="font-semibold text-white text-sm flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-emerald-400" />
              Budget Breakdown &amp; Resource Valuation
            </span>
            <Badge variant="success">Sum: {formatCurrency(totalSceneCost)}</Badge>
          </div>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-300">High Priority Climax Scenes (6 Scenes)</span>
              <span className="font-mono text-white font-semibold">$385,000</span>
            </div>
            <div className="flex justify-between items-center p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-300">Lead Cast Daily Allocations (Mercer &amp; Vance)</span>
              <span className="font-mono text-white font-semibold">$26,500 / day</span>
            </div>
            <div className="flex justify-between items-center p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-300">Specialty Crane &amp; Aerial Units (Technocrane + Heli)</span>
              <span className="font-mono text-white font-semibold">$12,800 / day</span>
            </div>
            <div className="flex justify-between items-center p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-slate-300">Soundstage Rental &amp; Cryo Lighting</span>
              <span className="font-mono text-white font-semibold">$13,500 / day</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
