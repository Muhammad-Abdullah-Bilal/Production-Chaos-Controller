"use client";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ArrowRight, Calendar, ArrowLeftRight, CheckCircle2, Clock } from "lucide-react";

interface ScheduleChange {
  scene_id: string;
  scene_number: string;
  action: string;
  original_day: number;
  target_day: number;
  reason: string;
}

interface Props {
  shootDay: number;
  affectedScenes: any[];
  proposedChanges: ScheduleChange[];
  selectedOptionTitle: string;
}

export function ScheduleComparison({
  shootDay,
  affectedScenes,
  proposedChanges,
  selectedOptionTitle,
}: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <ArrowLeftRight className="h-4 w-4 text-indigo-400" />
          Side-by-Side Schedule Comparison
        </h3>
        <Badge variant="info">Strategy: {selectedOptionTitle}</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Panel: Original Schedule */}
        <Card className="p-4 border-slate-800 bg-slate-950/80 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-semibold text-rose-300 text-xs flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              Original Schedule (Day {shootDay})
            </span>
            <Badge variant="danger" className="text-[10px]">
              {affectedScenes.length} Conflicted Scene(s)
            </Badge>
          </div>

          <div className="space-y-2">
            {affectedScenes.map((sc) => (
              <div
                key={sc.scene_id}
                className="p-3 rounded-lg bg-rose-950/20 border border-rose-800/40 space-y-1 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-rose-300">
                    SCENE {sc.scene_number}
                  </span>
                  <Badge variant="danger" className="text-[10px]">
                    ACTOR BLOCKED
                  </Badge>
                </div>
                <div className="font-medium text-white">{sc.title}</div>
                <div className="text-[11px] text-slate-400 font-mono">
                  {sc.indoor_outdoor} • {sc.duration} hrs • Cost: ${sc.estimated_cost?.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Right Panel: Proposed Recovered Schedule */}
        <Card className="p-4 border-indigo-900/40 bg-indigo-950/20 space-y-3">
          <div className="flex items-center justify-between border-b border-indigo-800/40 pb-2">
            <span className="font-semibold text-emerald-300 text-xs flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              Proposed Recovered Schedule
            </span>
            <Badge variant="success" className="text-[10px]">
              AI RECOVERY ACTIVE
            </Badge>
          </div>

          <div className="space-y-2">
            {proposedChanges.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No modifications needed.</p>
            ) : (
              proposedChanges.map((change, idx) => {
                const isAdvanced = change.action.includes("ADVANCED");
                return (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border text-xs space-y-1 ${
                      isAdvanced
                        ? "bg-emerald-950/30 border-emerald-800/50"
                        : "bg-amber-950/30 border-amber-800/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-white">
                        SCENE {change.scene_number}
                      </span>
                      <Badge variant={isAdvanced ? "success" : "warning"} className="text-[10px]">
                        {change.action}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2 font-mono text-[11px] text-indigo-300">
                      <span>Day {change.original_day}</span>
                      <ArrowRight className="h-3 w-3 text-slate-400" />
                      <span className="font-bold text-white">Day {change.target_day}</span>
                    </div>

                    <p className="text-[11px] text-slate-300">{change.reason}</p>
                  </div>
                );
              })
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
