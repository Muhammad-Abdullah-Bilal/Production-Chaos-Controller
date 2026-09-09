"use client";

import { Actor, ProductionSchedule } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import { UserCheck, Star, Film, Mail, DollarSign } from "lucide-react";

interface Props {
  actors: Actor[];
  schedule: ProductionSchedule | null;
}

export function ActorsView({ actors, schedule }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Cast Directory &amp; Role Assignments ({actors.length})
        </h2>
        <Badge variant="info">2 Lead Cast • 6 Supporting Cast</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {actors.map((actor) => {
          const assignedScenes = schedule?.scenes.filter((s) => s.actor_ids.includes(actor.actor_id)) || [];

          return (
            <Card key={actor.actor_id} className="p-4 space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <div className="space-y-0.5">
                    <h3 className="font-bold text-white text-base leading-snug">{actor.name}</h3>
                    <span className="text-xs text-indigo-300 font-medium block">{actor.character_name}</span>
                  </div>
                  {actor.is_lead ? (
                    <Badge variant="success" className="gap-1 text-[10px]">
                      <Star className="h-3 w-3 fill-emerald-400 text-emerald-400" />
                      LEAD
                    </Badge>
                  ) : (
                    <Badge variant="default" className="text-[10px]">
                      SUPPORTING
                    </Badge>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800/80">
                  <span className="flex items-center gap-1 font-mono text-emerald-400">
                    <DollarSign className="h-3.5 w-3.5" />
                    {formatCurrency(actor.daily_rate)} / day
                  </span>
                  <span className="flex items-center gap-1 font-mono text-slate-300">
                    <Film className="h-3.5 w-3.5 text-indigo-400" />
                    {assignedScenes.length} Scenes
                  </span>
                </div>
              </div>

              {/* Assigned scenes list */}
              <div className="p-2.5 rounded bg-slate-950/80 border border-slate-800 text-[11px] space-y-1">
                <span className="text-slate-400 font-medium block">Assigned Scene Numbers:</span>
                <div className="flex flex-wrap gap-1">
                  {assignedScenes.map((s) => (
                    <span
                      key={s.scene_id}
                      className="px-1.5 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/60 font-mono text-[10px] text-indigo-300"
                    >
                      {s.scene_number}
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
