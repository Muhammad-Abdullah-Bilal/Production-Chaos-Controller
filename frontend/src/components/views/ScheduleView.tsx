"use client";

import { ShootingDay, ProductionSchedule } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import { Calendar, Clock, MapPin, DollarSign, CloudRain } from "lucide-react";

interface Props {
  shootingDays: ShootingDay[];
  schedule: ProductionSchedule | null;
}

export function ScheduleView({ shootingDays, schedule }: Props) {
  const sceneMap = new Map(schedule?.scenes.map((s) => [s.scene_id, s]) || []);
  const locationMap = new Map(schedule?.locations.map((l) => [l.location_id, l]) || []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          10-Day Principal Photography Timeline
        </h2>
        <Badge variant="info">Projected Wrap: Oct 10, 2026</Badge>
      </div>

      <div className="space-y-4">
        {shootingDays.map((day) => {
          const loc = locationMap.get(day.location_id);
          return (
            <Card key={day.day_number} className="p-5 space-y-4">
              {/* Day Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                  <div className="px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 font-bold font-mono text-sm">
                    DAY {day.day_number}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-base">{day.notes || `Shoot Day ${day.day_number}`}</h3>
                    <span className="text-xs text-slate-400 font-mono">{day.date}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-300 bg-slate-950 px-2.5 py-1 rounded border border-slate-800 font-mono">
                    <Clock className="h-3.5 w-3.5 text-indigo-400" />
                    {day.call_time} — {day.wrap_time}
                  </div>
                  <div className="flex items-center gap-1.5 text-emerald-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800 font-mono">
                    <DollarSign className="h-3.5 w-3.5 text-emerald-400" />
                    Est: {formatCurrency(day.estimated_daily_cost)}
                  </div>
                </div>
              </div>

              {/* Location Badge */}
              <div className="flex items-center justify-between text-xs text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                <span className="flex items-center gap-1.5">
                  <MapPin className="h-4 w-4 text-indigo-400" />
                  <span className="font-semibold text-white">{loc?.name || day.location_id}</span>
                  <span className="text-slate-500">({loc?.address})</span>
                </span>
                <div className="flex items-center gap-1.5">
                  <Badge variant={loc?.indoor_outdoor === "Outdoor" ? "warning" : "default"}>
                    {loc?.indoor_outdoor}
                  </Badge>
                  {loc?.weather_vulnerable && (
                    <Badge variant="danger" className="gap-1">
                      <CloudRain className="h-3 w-3" />
                      Weather Risk
                    </Badge>
                  )}
                </div>
              </div>

              {/* Assigned Scenes Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {day.scene_ids.map((sceneId) => {
                  const scene = sceneMap.get(sceneId);
                  if (!scene) return null;
                  return (
                    <div
                      key={sceneId}
                      className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-indigo-300">
                          SCENE {scene.scene_number}
                        </span>
                        <Badge
                          variant={scene.priority === "High" ? "danger" : "default"}
                          className="text-[10px]"
                        >
                          {scene.priority} Priority
                        </Badge>
                      </div>
                      <h4 className="font-semibold text-white text-xs">{scene.title}</h4>
                      <p className="text-[11px] text-slate-400 line-clamp-1">{scene.description}</p>
                      <div className="flex items-center justify-between pt-1 text-[10px] text-slate-500 font-mono">
                        <span>Duration: {scene.duration} hrs</span>
                        <span>Est: {formatCurrency(scene.estimated_cost)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
