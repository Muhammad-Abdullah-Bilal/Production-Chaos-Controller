"use client";

import { useState } from "react";
import { Scene, ProductionSchedule } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import { Film, Clock, CloudRain, ShieldAlert, Filter, Search, DollarSign } from "lucide-react";

interface Props {
  scenes: Scene[];
  schedule: ProductionSchedule | null;
}

export function SceneListView({ scenes, schedule }: Props) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterIndoor, setFilterIndoor] = useState<string>("ALL");
  const [filterPriority, setFilterPriority] = useState<string>("ALL");

  const actorMap = new Map(schedule?.actors.map((a) => [a.actor_id, a.name]) || []);
  const locationMap = new Map(schedule?.locations.map((l) => [l.location_id, l.name]) || []);
  const eqMap = new Map(schedule?.equipment.map((e) => [e.equipment_id, e.name]) || []);

  const filteredScenes = scenes.filter((scene) => {
    const matchesSearch =
      scene.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scene.scene_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scene.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesIndoor =
      filterIndoor === "ALL" || scene.indoor_outdoor === filterIndoor;

    const matchesPriority =
      filterPriority === "ALL" || scene.priority === filterPriority;

    return matchesSearch && matchesIndoor && matchesPriority;
  });

  return (
    <div className="space-y-4">
      {/* Search & Filter Toolbar */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div className="relative w-full sm:w-72">
          <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search scene title, number, script..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-slate-400 flex items-center gap-1">
            <Filter className="h-3.5 w-3.5 text-indigo-400" /> Filter:
          </span>
          <select
            value={filterIndoor}
            onChange={(e) => setFilterIndoor(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Environments</option>
            <option value="Indoor">Indoor Only</option>
            <option value="Outdoor">Outdoor Only</option>
          </select>
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Priorities</option>
            <option value="High">High Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="Low">Low Priority</option>
          </select>
        </div>
      </div>

      {/* Scene Counter */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Showing {filteredScenes.length} of {scenes.length} Scenes</span>
      </div>

      {/* Scenes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredScenes.map((scene) => {
          const locName = locationMap.get(scene.location_id) || scene.location_id;
          return (
            <Card key={scene.scene_id} className="p-4 space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="info" className="font-mono text-xs">
                      SCENE {scene.scene_number}
                    </Badge>
                    <span className="font-bold text-white text-sm">{scene.title}</span>
                  </div>
                  <Badge
                    variant={
                      scene.priority === "High"
                        ? "danger"
                        : scene.priority === "Medium"
                        ? "warning"
                        : "default"
                    }
                    className="text-[10px]"
                  >
                    {scene.priority} Priority
                  </Badge>
                </div>

                <p className="text-xs text-slate-300 line-clamp-2">{scene.description}</p>

                {/* Badges bar */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px]">
                  <Badge variant={scene.indoor_outdoor === "Outdoor" ? "warning" : "default"}>
                    {scene.indoor_outdoor.toUpperCase()}
                  </Badge>

                  {scene.weather_sensitive && (
                    <Badge variant="danger" className="gap-1">
                      <CloudRain className="h-3 w-3" />
                      WEATHER SENSITIVE
                    </Badge>
                  )}

                  <span className="text-slate-400 font-mono ml-auto">
                    {scene.duration} hrs • {formatCurrency(scene.estimated_cost)}
                  </span>
                </div>
              </div>

              {/* Cast & Resource Tags */}
              <div className="p-2.5 rounded bg-slate-950/80 border border-slate-800/80 text-[11px] space-y-1.5 mt-2">
                <div className="text-slate-400">
                  <span className="font-medium text-slate-500">Location: </span>
                  <span className="text-indigo-300 font-medium">{locName}</span>
                </div>
                <div className="flex flex-wrap gap-1 text-[10px]">
                  <span className="text-slate-500 font-medium">Cast: </span>
                  {scene.actor_ids.map((aId) => (
                    <span key={aId} className="px-1.5 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/60 text-indigo-300">
                      {actorMap.get(aId) || aId}
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
