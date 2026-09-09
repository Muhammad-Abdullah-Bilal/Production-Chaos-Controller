"use client";

import { Location, ProductionSchedule } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import { MapPin, CloudRain, ShieldCheck, DollarSign, Film } from "lucide-react";

interface Props {
  locations: Location[];
  schedule: ProductionSchedule | null;
}

export function LocationsView({ locations, schedule }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Filming Locations Directory ({locations.length})
        </h2>
        <Badge variant="info">2 Soundstages • 2 Outdoor Locations</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {locations.map((loc) => {
          const assignedScenes = schedule?.scenes.filter((s) => s.location_id === loc.location_id) || [];

          return (
            <Card key={loc.location_id} className="p-5 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="font-bold text-white text-base flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-indigo-400" />
                      {loc.name}
                    </h3>
                    <p className="text-xs text-slate-400">{loc.address}</p>
                  </div>
                  <Badge variant={loc.indoor_outdoor === "Outdoor" ? "warning" : "default"}>
                    {loc.indoor_outdoor.toUpperCase()}
                  </Badge>
                </div>

                <div className="flex items-center gap-2 flex-wrap text-[11px]">
                  <span className="font-mono text-emerald-400 font-semibold bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                    {formatCurrency(loc.daily_rate)} / day
                  </span>
                  {loc.permit_required && (
                    <Badge variant="info" className="gap-1">
                      <ShieldCheck className="h-3 w-3" />
                      PERMIT APPROVED
                    </Badge>
                  )}
                  {loc.weather_vulnerable && (
                    <Badge variant="danger" className="gap-1">
                      <CloudRain className="h-3 w-3" />
                      WEATHER RISK
                    </Badge>
                  )}
                </div>

                {loc.notes && (
                  <p className="text-xs text-slate-300 italic bg-slate-950/60 p-2.5 rounded border border-slate-800/60">
                    &quot;{loc.notes}&quot;
                  </p>
                )}
              </div>

              {/* Mapped Scenes */}
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="font-medium">Mapped Scenes ({assignedScenes.length}):</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {assignedScenes.map((s) => (
                    <span
                      key={s.scene_id}
                      className="px-2 py-0.5 rounded bg-indigo-950/70 border border-indigo-800/70 text-indigo-300 font-mono text-[11px]"
                    >
                      Scene {s.scene_number} ({s.title})
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
