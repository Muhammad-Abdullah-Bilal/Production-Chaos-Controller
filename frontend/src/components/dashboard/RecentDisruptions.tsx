import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DisruptionEvent } from "@/lib/types";
import { AlertTriangle, ArrowRight, PlusCircle } from "lucide-react";

interface RecentDisruptionsProps {
  disruptions: DisruptionEvent[];
}

export function RecentDisruptions({ disruptions }: RecentDisruptionsProps) {
  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return <Badge variant="danger">CRITICAL</Badge>;
      case "high":
        return <Badge variant="danger">HIGH</Badge>;
      case "medium":
        return <Badge variant="warning">MEDIUM</Badge>;
      default:
        return <Badge variant="info">LOW</Badge>;
    }
  };

  return (
    <Card className="flex flex-col justify-between">
      <div>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                Live Disruption Log
              </CardTitle>
              <CardDescription>
                Unexpected production incidents requiring AI recovery intervention
              </CardDescription>
            </div>
            <Link href="/disruptions">
              <Button size="sm" variant="secondary" className="gap-1.5 text-xs">
                <PlusCircle className="h-3.5 w-3.5 text-indigo-400" />
                Report Event
              </Button>
            </Link>
          </div>
        </CardHeader>

        <div className="space-y-3 pt-1">
          {disruptions.length === 0 ? (
            <div className="py-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              <p className="text-sm font-medium text-slate-400">Zero active production disruptions</p>
              <p className="text-xs text-slate-500 mt-1">
                Actors, crew, equipment, and locations are confirmed on schedule.
              </p>
            </div>
          ) : (
            disruptions.slice(0, 3).map((d) => (
              <div
                key={d.id}
                className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex flex-col gap-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-white">{d.title}</span>
                  {getSeverityBadge(d.severity)}
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">{d.description}</p>
                <div className="flex items-center justify-between pt-2 text-xs text-slate-500 border-t border-slate-800/50">
                  <span>Day {d.shoot_day_affected} Impacted</span>
                  <span className="font-mono text-[11px] text-amber-400">
                    {d.affected_scene_ids.length} scenes stalled
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="pt-4 mt-4 border-t border-slate-800 flex justify-end">
        <Link href="/recovery">
          <Button variant="ghost" size="sm" className="text-xs text-indigo-400 hover:text-indigo-300 gap-1">
            View AI Recovery Scenarios
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </Link>
      </div>
    </Card>
  );
}
