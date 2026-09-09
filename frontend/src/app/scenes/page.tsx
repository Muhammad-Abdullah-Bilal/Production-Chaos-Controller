"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Scene, Location } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Film, MapPin, CloudRain, Filter, Search } from "lucide-react";

export default function ScenesPage() {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterIndoorOutdoor, setFilterIndoorOutdoor] = useState<string>("ALL");
  const [filterWeather, setFilterWeather] = useState<string>("ALL");

  useEffect(() => {
    Promise.all([
      api.getScenes().catch(() => []),
      api.getLocations().catch(() => []),
    ])
      .then(([sc, locs]) => {
        setScenes(sc);
        setLocations(locs);
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredScenes = scenes.filter((scene) => {
    const matchesSearch =
      scene.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scene.scene_number.toString().includes(searchTerm) ||
      scene.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType =
      filterIndoorOutdoor === "ALL" ||
      (filterIndoorOutdoor === "Indoor" && scene.indoor_outdoor === "Indoor") ||
      (filterIndoorOutdoor === "Outdoor" && scene.indoor_outdoor === "Outdoor");

    const matchesWeather =
      filterWeather === "ALL" ||
      (filterWeather === "SENSITIVE" && scene.weather_sensitive) ||
      (filterWeather === "STABLE" && !scene.weather_sensitive);

    return matchesSearch && matchesType && matchesWeather;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Film className="h-5 w-5 text-indigo-400" />
          Production Scenes &amp; Dependency Breakdown
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Catalog of all production script scenes, required locations, cast assignments, equipment specs, and weather sensitivity.
        </p>
      </div>

      {/* Filters Bar */}
      <Card className="p-4 bg-slate-900 border-slate-800">
        <div className="flex flex-wrap items-center gap-4 justify-between">
          <div className="flex items-center gap-2 flex-1 min-w-[240px]">
            <Search className="h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search scene title, number, or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 text-xs text-slate-400">
              <Filter className="h-3.5 w-3.5" />
              <span>Setting:</span>
            </div>
            <select
              value={filterIndoorOutdoor}
              onChange={(e) => setFilterIndoorOutdoor(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Settings</option>
              <option value="Indoor">Indoor (Soundstage/Set)</option>
              <option value="Outdoor">Outdoor (Exterior)</option>
            </select>

            <select
              value={filterWeather}
              onChange={(e) => setFilterWeather(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Weather Profiling</option>
              <option value="SENSITIVE">⛈️ Weather Sensitive</option>
              <option value="STABLE">🛡️ Weather Resistant</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Scenes Grid */}
      {loading ? (
        <div className="p-12 text-center text-slate-500 text-xs font-mono">Loading production scenes...</div>
      ) : filteredScenes.length === 0 ? (
        <Card className="p-8 text-center text-slate-500 border-dashed">
          No matching scenes found for current filters.
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredScenes.map((scene) => {
            const locName = locations.find((l) => l.location_id === scene.location_id)?.name || scene.location_id;
            return (
              <Card key={scene.scene_id} className="p-4 bg-slate-900/90 border-slate-800 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-mono text-xs font-bold border border-indigo-500/30">
                        SCENE {scene.scene_number}
                      </span>
                      <Badge variant={scene.indoor_outdoor === "Indoor" ? "default" : "outline"}>
                        {scene.indoor_outdoor.toUpperCase()}
                      </Badge>
                      {scene.weather_sensitive && (
                        <Badge variant="warning" className="text-[9px] gap-1">
                          <CloudRain className="h-3 w-3" /> Weather Sensitive
                        </Badge>
                      )}
                    </div>
                    <h3 className="text-sm font-bold text-white tracking-tight pt-0.5">{scene.title}</h3>
                  </div>
                  <Badge variant="outline" className="font-mono text-[10px]">
                    Est. {scene.duration} Hrs
                  </Badge>
                </div>

                <p className="text-xs text-slate-300 leading-snug">{scene.description}</p>

                <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs">
                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">Filming Location</span>
                    <div className="flex items-center gap-1 text-slate-300 font-medium">
                      <MapPin className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span className="truncate">{locName}</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase font-mono block">Required Weather</span>
                    <span className="text-slate-300 font-mono text-[11px] capitalize">
                      {(scene as any).required_weather || "Clear / Any"}
                    </span>
                  </div>
                </div>

                {/* Cast & Equipment Dependencies */}
                <div className="pt-2 border-t border-slate-800/80 space-y-2 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block mb-1">Required Cast:</span>
                    <div className="flex flex-wrap gap-1">
                      {scene.actor_ids.map((actorId: string) => (
                        <Badge key={actorId} variant="outline" className="text-[10px] bg-slate-950">
                          👤 {actorId}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-mono block mb-1">Required Equipment:</span>
                    <div className="flex flex-wrap gap-1">
                      {scene.equipment_ids.map((eqId: string) => (
                        <Badge key={eqId} variant="outline" className="text-[10px] bg-slate-950 border-slate-800">
                          🎥 {eqId}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
