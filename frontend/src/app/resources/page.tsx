"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Actor, Equipment, Location, CrewMember } from "@/lib/types";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";
import { Users, Camera, MapPin, UserCheck, CheckCircle2 } from "lucide-react";

type ResourceTab = "actors" | "equipment" | "locations" | "crew";

export default function ResourcesPage() {
  const [activeTab, setActiveTab] = useState<ResourceTab>("actors");
  const [actors, setActors] = useState<Actor[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [crew, setCrew] = useState<CrewMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getActors().catch(() => []),
      api.getEquipment().catch(() => []),
      api.getLocations().catch(() => []),
      api.getCrew().catch(() => []),
    ])
      .then(([act, eq, locs, crw]) => {
        setActors(act);
        setEquipment(eq);
        setLocations(locs);
        setCrew(crw);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Users className="h-5 w-5 text-purple-400" />
          Production Resources &amp; Assets Directory
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Master registry of actors, critical filming equipment, approved stage/location venues, and crew roles.
        </p>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-2 p-1 bg-slate-900 border border-slate-800 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab("actors")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            activeTab === "actors"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <UserCheck className="h-4 w-4" />
          Actors ({actors.length})
        </button>
        <button
          onClick={() => setActiveTab("equipment")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            activeTab === "equipment"
              ? "bg-purple-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Camera className="h-4 w-4" />
          Equipment ({equipment.length})
        </button>
        <button
          onClick={() => setActiveTab("locations")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            activeTab === "locations"
              ? "bg-emerald-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <MapPin className="h-4 w-4" />
          Locations ({locations.length})
        </button>
        <button
          onClick={() => setActiveTab("crew")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            activeTab === "crew"
              ? "bg-blue-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Users className="h-4 w-4" />
          Crew ({crew.length})
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-500 text-xs font-mono">Loading resource database...</div>
      ) : activeTab === "actors" ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {actors.map((actor) => (
            <Card key={actor.actor_id} className="p-4 bg-slate-900/90 border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{actor.name}</h3>
                  <p className="text-xs text-indigo-400 font-medium">Role: {actor.character_name}</p>
                </div>
                {actor.is_lead ? (
                  <Badge variant="warning" className="text-[9px]">★ Lead Cast</Badge>
                ) : (
                  <Badge variant="outline" className="text-[9px]">Supporting</Badge>
                )}
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-xs space-y-1">
                <div className="flex justify-between text-slate-400">
                  <span>Day Rate:</span>
                  <span className="text-emerald-400 font-mono font-bold">{formatCurrency(actor.daily_rate)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Status:</span>
                  <span className="text-slate-200 font-medium flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-emerald-400" /> Active Schedule
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : activeTab === "equipment" ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {equipment.map((eq) => (
            <Card key={eq.equipment_id} className="p-4 bg-slate-900/90 border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{eq.name}</h3>
                  <p className="text-xs text-purple-400 font-medium">Category: {eq.category}</p>
                </div>
                {eq.is_critical ? (
                  <Badge variant="danger" className="text-[9px]">⚠️ Critical Asset</Badge>
                ) : (
                  <Badge variant="outline" className="text-[9px]">Standard</Badge>
                )}
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-xs space-y-1">
                <div className="flex justify-between text-slate-400">
                  <span>Daily Rental:</span>
                  <span className="text-emerald-400 font-mono font-bold">{formatCurrency(eq.daily_rate)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Operated By:</span>
                  <span className="text-slate-200 font-mono text-[11px]">{(eq as any).required_crew_role || "Camera Crew"}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : activeTab === "locations" ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {locations.map((loc) => (
            <Card key={loc.location_id} className="p-4 bg-slate-900/90 border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{loc.name}</h3>
                  <p className="text-xs text-emerald-400 font-medium">Setting: {loc.indoor_outdoor}</p>
                </div>
                {loc.weather_vulnerable ? (
                  <Badge variant="warning" className="text-[9px]">⛈️ Weather Sensitive</Badge>
                ) : (
                  <Badge variant="success" className="text-[9px]">🛡️ All-Weather</Badge>
                )}
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-xs space-y-1">
                <div className="flex justify-between text-slate-400">
                  <span>Location Fee:</span>
                  <span className="text-emerald-400 font-mono font-bold">{formatCurrency(loc.daily_rate)}/day</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Max Crew Capacity:</span>
                  <span className="text-slate-200 font-mono">{(loc as any).max_crew_capacity || 40} People</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {crew.map((c) => (
            <Card key={c.crew_id} className="p-4 bg-slate-900/90 border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{c.name}</h3>
                  <p className="text-xs text-blue-400 font-medium">{c.role}</p>
                </div>
                <Badge variant="outline" className="text-[9px] uppercase font-mono">{c.department}</Badge>
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-xs space-y-1">
                <div className="flex justify-between text-slate-400">
                  <span>Daily Rate:</span>
                  <span className="text-emerald-400 font-mono font-bold">{formatCurrency(c.daily_rate)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Department:</span>
                  <span className="text-slate-200 font-medium">{c.department}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
