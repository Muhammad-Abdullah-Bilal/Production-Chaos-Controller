"use client";

import { Equipment, ProductionSchedule } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import { Camera, AlertCircle, ShieldAlert, DollarSign, Film } from "lucide-react";

interface Props {
  equipment: Equipment[];
  schedule: ProductionSchedule | null;
}

export function EquipmentView({ equipment, schedule }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Equipment Catalog &amp; Technical Assets ({equipment.length})
        </h2>
        <Badge variant="info">2 Critical Bottleneck Units</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {equipment.map((eq) => {
          const assignedScenes = schedule?.scenes.filter((s) => s.equipment_ids.includes(eq.equipment_id)) || [];

          return (
            <Card key={eq.equipment_id} className="p-5 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="font-bold text-white text-base flex items-center gap-2">
                      <Camera className="h-4 w-4 text-purple-400" />
                      {eq.name}
                    </h3>
                    <span className="text-xs text-slate-400 block">Category: {eq.category}</span>
                  </div>
                  {eq.is_critical ? (
                    <Badge variant="danger" className="gap-1 text-[10px]">
                      <AlertCircle className="h-3 w-3" />
                      CRITICAL ASSET
                    </Badge>
                  ) : (
                    <Badge variant="default" className="text-[10px]">
                      STANDARD
                    </Badge>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 pt-1 border-t border-slate-800">
                  <span className="font-mono text-emerald-400 font-semibold">
                    {formatCurrency(eq.daily_rate)} / day
                  </span>
                  <span className="font-mono text-indigo-300">
                    Required for {assignedScenes.length} Scenes
                  </span>
                </div>
              </div>

              {/* Mapped Scenes */}
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5 text-xs">
                <span className="text-slate-400 font-medium block">Assigned Scenes:</span>
                <div className="flex flex-wrap gap-1">
                  {assignedScenes.map((s) => (
                    <span
                      key={s.scene_id}
                      className="px-1.5 py-0.5 rounded bg-purple-950/60 border border-purple-800/60 text-purple-300 font-mono text-[10px]"
                    >
                      Scene {s.scene_number}
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
