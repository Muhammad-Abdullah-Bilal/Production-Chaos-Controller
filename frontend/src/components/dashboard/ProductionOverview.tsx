import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProductionSchedule } from "@/lib/types";
import { Clock, MapPin, Users, Video } from "lucide-react";

interface ProductionOverviewProps {
  schedule: ProductionSchedule | null;
}

export function ProductionOverview({ schedule }: ProductionOverviewProps) {
  if (!schedule) {
    return (
      <Card className="h-full flex items-center justify-center min-h-[280px]">
        <div className="text-center text-slate-500">
          <p className="text-sm">Connecting to &quot;The Last Signal&quot; backend engine...</p>
        </div>
      </Card>
    );
  }

  const currentDay = schedule.shooting_days[0];
  const todayScenes = schedule.scenes.filter((s) => currentDay?.scene_ids.includes(s.scene_id));

  return (
    <Card className="flex flex-col justify-between">
      <div>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle>Today&apos;s Call Sheet: Day {currentDay?.day_number || 1}</CardTitle>
              <CardDescription>
                Call Time: {currentDay?.call_time || "06:00"} | Wrap: {currentDay?.wrap_time || "18:00"}
              </CardDescription>
            </div>
            <Badge variant="info">Day 1 of 10</Badge>
          </div>
        </CardHeader>

        <div className="space-y-3 pt-1">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Scheduled Scenes for Day 1
          </div>
          <div className="space-y-2">
            {todayScenes.length === 0 ? (
              <p className="text-sm text-slate-400">No scenes scheduled for today.</p>
            ) : (
              todayScenes.map((scene) => (
                <div
                  key={scene.scene_id}
                  className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-indigo-400">
                        SCENE {scene.scene_number}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        ({scene.indoor_outdoor})
                      </span>
                      <span className="text-sm font-medium text-white">{scene.title}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-slate-500" />
                        {scene.duration} hrs
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3 text-slate-500" />
                        {scene.actor_ids.length} Actors, {scene.crew_ids.length} Crew
                      </span>
                    </div>
                  </div>
                  <Badge variant="default" className="text-[10px]">
                    {scene.status}
                  </Badge>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="pt-4 mt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <MapPin className="h-3.5 w-3.5 text-indigo-400" />
          Primary Location: Station Command Bunker
        </span>
        <span className="flex items-center gap-1.5">
          <Video className="h-3.5 w-3.5 text-slate-400" />
          {schedule.equipment.length} Camera &amp; Crane Units
        </span>
      </div>
    </Card>
  );
}
