"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ProductionSchedule, Actor, Equipment, Location, CrewMember } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ScheduleComparison } from "@/components/disruption/ScheduleComparison";
import { formatCurrency } from "@/lib/utils";
import {
  AlertTriangle,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Edit3,
  UserCheck,
  Camera,
  MapPin,
  Building,
  CloudRain,
  Sun,
  Calendar,
  Users,
  Truck,
  Flame,
  Plus,
  Trash2,
  Layers,
  AlertCircle,
} from "lucide-react";

type ScenarioMode = "actor" | "equipment" | "location" | "weather" | "crew" | "logistics" | "chaos";

export default function DisruptionsPage() {
  const [scenarioMode, setScenarioMode] = useState<ScenarioMode>("actor");
  const [schedule, setSchedule] = useState<ProductionSchedule | null>(null);
  const [actors, setActors] = useState<Actor[]>([]);
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  const [locationsList, setLocationsList] = useState<Location[]>([]);
  const [crewList, setCrewList] = useState<CrewMember[]>([]);
  const [loading, setLoading] = useState(true);

  // Actor Form selections
  const [selectedActorId, setSelectedActorId] = useState<string>("act_01");
  const [actorShootDay, setActorShootDay] = useState<number>(4);
  const [actorReason, setActorReason] = useState<string>(
    "Dr. Sarah Mercer contractually unavailable on Day 4 due to emergency medical hold."
  );

  // Equipment Form selections
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string>("eq_01");
  const [equipmentShootDay, setEquipmentShootDay] = useState<number>(5);
  const [equipmentReason, setEquipmentReason] = useState<string>(
    "RED V-Raptor 8K primary camera package sensor shutter failure on Day 5."
  );

  // Location Form selections
  const [selectedLocationId, setSelectedLocationId] = useState<string>("loc_03");
  const [locationShootDay, setLocationShootDay] = useState<number>(6);
  const [locationReason, setLocationReason] = useState<string>(
    "City Hospital / Sub-Zero Quantum Vault location unavailable on Day 6 due to emergency lockdown & coolant maintenance."
  );

  // Weather Form selections
  const [weatherType, setWeatherType] = useState<string>("Heavy Rain");
  const [weatherSeverity, setWeatherSeverity] = useState<string>("High");
  const [weatherShootDay, setWeatherShootDay] = useState<number>(7);
  const [weatherReason, setWeatherReason] = useState<string>(
    "Heavy torrential rain and high wind forecast for Day 7 halting outdoor helicopter extraction at Glacier Pass."
  );

  // Crew Form selections
  const [selectedCrewId, setSelectedCrewId] = useState<string>("crw_02");
  const [crewShootDay, setCrewShootDay] = useState<number>(5);
  const [crewReason, setCrewReason] = useState<string>(
    "Director of Photography Claire Delacroix suddenly unavailable on Day 5 due to emergency medical hold."
  );

  // Logistics Form selections
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>("veh_01");
  const [logisticsShootDay, setLogisticsShootDay] = useState<number>(8);
  const [logisticsDelayHours, setLogisticsDelayHours] = useState<number>(2);
  const [logisticsReason, setLogisticsReason] = useState<string>(
    "Equipment transport vehicle broken down on mountain pass highway route."
  );

  // Chaos Mode Multi-Disruption Stack
  const [chaosDisruptions, setChaosDisruptions] = useState<
    Array<{
      disruption_type: string;
      resource_id: string;
      shoot_day: number;
      reason: string;
      weather_type?: string;
      severity?: string;
    }>
  >([
    {
      disruption_type: "actor_unavailable",
      resource_id: "act_01",
      shoot_day: 6,
      reason: "Dr. Sarah Mercer contractually unavailable on Day 6 due to emergency medical hold.",
    },
    {
      disruption_type: "equipment_failure",
      resource_id: "eq_01",
      shoot_day: 6,
      reason: "RED V-Raptor 8K primary camera package sensor shutter failure on Day 6.",
    },
    {
      disruption_type: "bad_weather",
      resource_id: "loc_04",
      shoot_day: 6,
      reason: "Severe torrential rain forecast halting outdoor filming at Glacier Pass on Day 6.",
      weather_type: "Heavy Rain",
      severity: "High",
    },
  ]);

  // AI Agent Analysis Result
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [selectedOptionIndex, setSelectedOptionIndex] = useState<number>(0);

  // ClickHouse Production Analytics Query Explorer
  const [selectedAnalyticsQuery, setSelectedAnalyticsQuery] = useState<string>("high_risk_disruption_resources");
  const [analyticsResult, setAnalyticsResult] = useState<any | null>(null);
  const [isQueryingAnalytics, setIsQueryingAnalytics] = useState<boolean>(false);

  const handleRunAnalyticsQuery = async (queryName: string, params?: Record<string, any>) => {
    setSelectedAnalyticsQuery(queryName);
    setIsQueryingAnalytics(true);
    try {
      const res = await api.runClickHouseQuery(queryName, params);
      setAnalyticsResult(res);
    } catch (err) {
      console.error("ClickHouse analytics query error:", err);
    } finally {
      setIsQueryingAnalytics(false);
    }
  };

  // Producer Approval State
  const [producerNotes, setProducerNotes] = useState<string>("");
  const [approvalStatus, setApprovalStatus] = useState<string | null>(null);
  const [isModifying, setIsModifying] = useState<boolean>(false);

  useEffect(() => {
    Promise.all([
      api.getProduction().catch(() => null),
      api.getActors().catch(() => []),
      api.getEquipment().catch(() => []),
      api.getLocations().catch(() => []),
      api.getCrew().catch(() => []),
    ])
      .then(([prod, act, eq, locs, crw]) => {
        setSchedule(prod);
        setActors(act);
        setEquipmentList(eq);
        setLocationsList(locs);
        setCrewList(crw);
        if (act.length > 0) setSelectedActorId(act[0].actor_id);
        if (eq.length > 0) setSelectedEquipmentId(eq[0].equipment_id);
        if (locs.length > 0) setSelectedLocationId(locs[2]?.location_id || locs[0].location_id);
        if (crw.length > 0) setSelectedCrewId(crw[1]?.crew_id || crw[0].crew_id);
      })
      .finally(() => setLoading(false));
  }, []);

  const ANALYSIS_STEPS = [
    "Analyzing production...",
    "Finding dependencies...",
    "Checking resources...",
    "Generating recovery plans...",
    "Evaluating impact...",
  ];
  const [analysisStepIndex, setAnalysisStepIndex] = useState<number>(0);

  const handleRunAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setAnalysisStepIndex(0);
    setApprovalStatus(null);

    const stepInterval = setInterval(() => {
      setAnalysisStepIndex((prev) => (prev < 4 ? prev + 1 : 4));
    }, 400);

    try {
      let res;
      if (scenarioMode === "actor") {
        res = await api.triggerActorDisruption({
          actor_id: selectedActorId,
          shoot_day: Number(actorShootDay),
          reason: actorReason,
        });
      } else if (scenarioMode === "equipment") {
        res = await api.triggerEquipmentDisruption({
          equipment_id: selectedEquipmentId,
          shoot_day: Number(equipmentShootDay),
          reason: equipmentReason,
        });
      } else if (scenarioMode === "location") {
        res = await api.triggerLocationDisruption({
          location_id: selectedLocationId,
          shoot_day: Number(locationShootDay),
          reason: locationReason,
        });
      } else if (scenarioMode === "weather") {
        res = await api.triggerWeatherDisruption({
          weather_type: weatherType,
          severity: weatherSeverity,
          shoot_day: Number(weatherShootDay),
          reason: weatherReason,
        });
      } else if (scenarioMode === "crew") {
        res = await api.triggerCrewDisruption({
          crew_id: selectedCrewId,
          shoot_day: Number(crewShootDay),
          reason: crewReason,
        });
      } else if (scenarioMode === "chaos") {
        res = await api.triggerMultiDisruptionAnalysis({
          disruptions: chaosDisruptions,
        });
      } else {
        res = await api.triggerLogisticsDisruption({
          vehicle_id: selectedVehicleId,
          shoot_day: Number(logisticsShootDay),
          delay_hours: Number(logisticsDelayHours),
          reason: logisticsReason,
        });
      }
      setAnalysisResult(res);
      setSelectedOptionIndex(0);
    } catch (err) {
      alert("Failed to analyze disruption. Make sure backend is running.");
    } finally {
      clearInterval(stepInterval);
      setIsAnalyzing(false);
    }
  };

  const handleApprove = () => setApprovalStatus("APPROVED");
  const handleReject = () => setApprovalStatus("REJECTED");

  const selectedPlan = analysisResult?.recovery_options?.[selectedOptionIndex] || analysisResult?.recommended_plan;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-400" />
          Production Chaos Controller — Disruption Simulator
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Select a disruption scenario to invoke deterministic tools and Gemini agent recovery reasoning over ClickHouse datasets.
        </p>
      </div>

      {/* 📊 ClickHouse Production Analytics Explorer */}
      <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-white flex items-center gap-1.5">
              📊 ClickHouse Production Analytics Engine
            </span>
            <Badge variant="success" className="text-[10px] font-mono bg-emerald-950 text-emerald-300 border-emerald-500/40">
              OFFICIAL CLICKHOUSE MCP INTEGRATED
            </Badge>
          </div>
          <span className="text-xs text-slate-400 italic">
            Query high-throughput production metrics, resource risk scores, and disruption cost statistics.
          </span>
        </div>

        {/* 6 Canonical Analytics Query Buttons */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
          <button
            onClick={() => handleRunAnalyticsQuery("scenes_by_actor", { actor_id: selectedActorId })}
            className={`p-2 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              selectedAnalyticsQuery === "scenes_by_actor"
                ? "bg-indigo-600/30 border-indigo-500 text-white font-semibold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            🎬 Actor Scenes
          </button>
          <button
            onClick={() => handleRunAnalyticsQuery("scenes_by_equipment", { equipment_id: selectedEquipmentId })}
            className={`p-2 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              selectedAnalyticsQuery === "scenes_by_equipment"
                ? "bg-purple-600/30 border-purple-500 text-white font-semibold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            🎥 Equipment Usage
          </button>
          <button
            onClick={() => handleRunAnalyticsQuery("top_frequent_locations", { limit: 5 })}
            className={`p-2 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              selectedAnalyticsQuery === "top_frequent_locations"
                ? "bg-emerald-600/30 border-emerald-500 text-white font-semibold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            📍 Location Freq
          </button>
          <button
            onClick={() => handleRunAnalyticsQuery("high_risk_disruption_resources")}
            className={`p-2 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              selectedAnalyticsQuery === "high_risk_disruption_resources"
                ? "bg-rose-600/30 border-rose-500 text-white font-semibold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            ⚠️ High Risk Resources
          </button>
          <button
            onClick={() => handleRunAnalyticsQuery("total_disruption_cost_summary")}
            className={`p-2 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              selectedAnalyticsQuery === "total_disruption_cost_summary"
                ? "bg-amber-600/30 border-amber-500 text-white font-semibold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            💰 Disruption Costs
          </button>
          <button
            onClick={() => handleRunAnalyticsQuery("lowest_impact_movable_scenes")}
            className={`p-2 rounded-lg text-left transition-all text-xs border cursor-pointer ${
              selectedAnalyticsQuery === "lowest_impact_movable_scenes"
                ? "bg-blue-600/30 border-blue-500 text-white font-semibold"
                : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            ⚡ Lowest Impact Movable
          </button>
        </div>

        {/* Analytics Query Results Viewer */}
        {analyticsResult && (
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
            <div className="flex items-center justify-between font-mono text-[11px] border-b border-slate-800 pb-1.5">
              <span className="text-indigo-400 font-bold uppercase">
                QUERY: {analyticsResult.query}
              </span>
              <Badge variant={analyticsResult.data_source === "clickhouse" ? "success" : "warning"} className="text-[9px] font-mono">
                {analyticsResult.data_source === "clickhouse" ? "📊 CLICKHOUSE CLUSTER" : "📁 LOCAL FALLBACK CACHE"}
              </Badge>
            </div>
            <pre className="text-[11px] text-slate-300 font-mono overflow-x-auto p-2 bg-slate-900/60 rounded max-h-40">
              {JSON.stringify(analyticsResult, null, 2)}
            </pre>
          </div>
        )}
      </Card>

      {/* Scenario Mode Switcher */}
      <div className="flex flex-wrap items-center gap-3 p-1.5 bg-slate-900 border border-slate-800 rounded-xl w-fit">
        <button
          onClick={() => {
            setScenarioMode("actor");
            setAnalysisResult(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            scenarioMode === "actor"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <UserCheck className="h-4 w-4" />
          Scenario 1: Actor Unavailable
        </button>
        <button
          onClick={() => {
            setScenarioMode("equipment");
            setAnalysisResult(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            scenarioMode === "equipment"
              ? "bg-purple-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Camera className="h-4 w-4" />
          Scenario 2: Equipment Failure
        </button>
        <button
          onClick={() => {
            setScenarioMode("weather");
            setAnalysisResult(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            scenarioMode === "weather"
              ? "bg-amber-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <CloudRain className="h-4 w-4" />
          Scenario 4: Bad Weather
        </button>
        <button
          onClick={() => {
            setScenarioMode("crew");
            setAnalysisResult(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            scenarioMode === "crew"
              ? "bg-blue-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Users className="h-4 w-4" />
          Scenario 5: Crew Unavailable
        </button>
        <button
          onClick={() => {
            setScenarioMode("logistics");
            setAnalysisResult(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            scenarioMode === "logistics"
              ? "bg-amber-600 text-white shadow-sm"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Truck className="h-4 w-4" />
          Scenario 6: Transport / Logistics
        </button>
        <button
          onClick={() => {
            setScenarioMode("chaos");
            setAnalysisResult(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
            scenarioMode === "chaos"
              ? "bg-rose-600 text-white shadow-sm ring-2 ring-rose-500/50"
              : "text-rose-400 hover:text-white hover:bg-rose-950/40 border border-rose-900/40"
          }`}
        >
          <Flame className="h-4 w-4 text-rose-400 animate-pulse" />
          🚨 CHAOS MODE (Multi-Disruption)
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Panel */}
        <Card className="lg:col-span-1 p-5 space-y-4">
          <CardHeader className="px-0 pt-0 pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              {scenarioMode === "actor" ? (
                <UserCheck className="h-4 w-4 text-indigo-400" />
              ) : scenarioMode === "equipment" ? (
                <Camera className="h-4 w-4 text-purple-400" />
              ) : scenarioMode === "location" ? (
                <MapPin className="h-4 w-4 text-emerald-400" />
              ) : scenarioMode === "weather" ? (
                <CloudRain className="h-4 w-4 text-amber-400" />
              ) : scenarioMode === "crew" ? (
                <Users className="h-4 w-4 text-blue-400" />
              ) : scenarioMode === "chaos" ? (
                <Flame className="h-4 w-4 text-rose-400 animate-pulse" />
              ) : (
                <Truck className="h-4 w-4 text-amber-400" />
              )}
              {scenarioMode === "actor"
                ? "Actor Disruption Settings"
                : scenarioMode === "equipment"
                ? "Equipment Failure Settings"
                : scenarioMode === "location"
                ? "Location Disruption Settings"
                : scenarioMode === "weather"
                ? "Weather Forecast Settings"
                : scenarioMode === "crew"
                ? "Crew Disruption Settings"
                : scenarioMode === "chaos"
                ? "🔥 Chaos Mode Multi-Disruption Builder"
                : "Logistics Breakdown Settings"}
            </CardTitle>
            <CardDescription className="text-xs">
              {scenarioMode === "actor"
                ? "Simulate lead or supporting cast unavailability"
                : scenarioMode === "equipment"
                ? "Simulate primary camera, crane, or prop failure"
                : scenarioMode === "location"
                ? "Simulate hospital, soundstage, or outdoor location closure"
                : scenarioMode === "weather"
                ? "Simulate rain, blizzard, or storm disrupting outdoor sets"
                : scenarioMode === "crew"
                ? "Simulate Director of Photography, Gaffer, or key crew absence"
                : scenarioMode === "chaos"
                ? "Simulate simultaneous disruptions occurring together (e.g. Lead Actor + Camera Failure + Heavy Rain)"
                : "Simulate equipment transport van or crew vehicle breakdown"}
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleRunAnalysis} className="space-y-4 text-xs">
            {scenarioMode === "actor" ? (
              <>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Select Unavailable Actor</label>
                  <select
                    value={selectedActorId}
                    onChange={(e) => setSelectedActorId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-indigo-500"
                  >
                    {actors.map((a) => (
                      <option key={a.actor_id} value={a.actor_id}>
                        {a.name} ({a.character_name}) {a.is_lead ? "★ Lead" : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Impacted Shoot Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={actorShootDay}
                    onChange={(e) => setActorShootDay(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Disruption Reason</label>
                  <textarea
                    rows={3}
                    required
                    value={actorReason}
                    onChange={(e) => setActorReason(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </>
            ) : scenarioMode === "equipment" ? (
              <>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Select Failed Equipment</label>
                  <select
                    value={selectedEquipmentId}
                    onChange={(e) => setSelectedEquipmentId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-purple-500"
                  >
                    {equipmentList.map((e) => (
                      <option key={e.equipment_id} value={e.equipment_id}>
                        {e.name} ({e.category}) {e.is_critical ? "⚠️ Critical Asset" : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Failure Shoot Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={equipmentShootDay}
                    onChange={(e) => setEquipmentShootDay(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-purple-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Failure Description</label>
                  <textarea
                    rows={3}
                    required
                    value={equipmentReason}
                    onChange={(e) => setEquipmentReason(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
              </>
            ) : scenarioMode === "location" ? (
              <>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Select Unavailable Location</label>
                  <select
                    value={selectedLocationId}
                    onChange={(e) => setSelectedLocationId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-emerald-500"
                  >
                    {locationsList.map((l) => (
                      <option key={l.location_id} value={l.location_id}>
                        {l.name} ({l.indoor_outdoor}) {l.weather_vulnerable ? "⛈️ Weather Sensitive" : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Unavailable Shoot Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={locationShootDay}
                    onChange={(e) => setLocationShootDay(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Unavailability Reason</label>
                  <textarea
                    rows={3}
                    required
                    value={locationReason}
                    onChange={(e) => setLocationReason(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </>
            ) : scenarioMode === "weather" ? (
              <>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Forecasted Weather Condition</label>
                  <select
                    value={weatherType}
                    onChange={(e) => setWeatherType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="Heavy Rain">🌧️ Heavy Rain / Downpour</option>
                    <option value="Blizzard & Snow">❄️ Blizzard & Heavy Snow</option>
                    <option value="High Winds">💨 High Winds & Gale Force</option>
                    <option value="Dense Fog">🌫️ Dense Zero-Visibility Fog</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Weather Severity</label>
                  <select
                    value={weatherSeverity}
                    onChange={(e) => setWeatherSeverity(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="High">🔴 High (Full Outdoor Shutdown)</option>
                    <option value="Medium">🟡 Medium (Partial Delay)</option>
                    <option value="Low">🟢 Low (Minor Caution)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Forecast Shoot Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={weatherShootDay}
                    onChange={(e) => setWeatherShootDay(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Weather Forecast Description</label>
                  <textarea
                    rows={3}
                    required
                    value={weatherReason}
                    onChange={(e) => setWeatherReason(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              </>
            ) : scenarioMode === "crew" ? (
              <>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Select Unavailable Crew Member</label>
                  <select
                    value={selectedCrewId}
                    onChange={(e) => setSelectedCrewId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                  >
                    {crewList.map((c) => (
                      <option key={c.crew_id} value={c.crew_id}>
                        {c.name} — {c.role} ({c.department})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Unavailable Shoot Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={crewShootDay}
                    onChange={(e) => setCrewShootDay(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Unavailability Reason</label>
                  <textarea
                    rows={3}
                    required
                    value={crewReason}
                    onChange={(e) => setCrewReason(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </>
            ) : scenarioMode === "chaos" ? (
              <div className="space-y-3">
                <div className="p-3 bg-rose-950/30 border border-rose-800/50 rounded-lg text-xs space-y-1">
                  <span className="font-bold text-rose-300 flex items-center gap-1.5">
                    <Flame className="h-4 w-4 text-rose-400 animate-pulse" />
                    Simultaneous Multi-Disruption Stack ({chaosDisruptions.length})
                  </span>
                  <p className="text-[11px] text-slate-400">
                    The Production Manager Agent will analyze all disruptions simultaneously, build a combined dependency graph, and resolve recovery plan collisions.
                  </p>
                </div>

                <div className="space-y-2">
                  {chaosDisruptions.map((dis, idx) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 font-bold text-white text-xs">
                          {dis.disruption_type === "actor_unavailable" ? (
                            <UserCheck className="h-3.5 w-3.5 text-indigo-400" />
                          ) : dis.disruption_type === "equipment_failure" ? (
                            <Camera className="h-3.5 w-3.5 text-purple-400" />
                          ) : dis.disruption_type === "location_unavailable" ? (
                            <MapPin className="h-3.5 w-3.5 text-emerald-400" />
                          ) : dis.disruption_type === "bad_weather" ? (
                            <CloudRain className="h-3.5 w-3.5 text-amber-400" />
                          ) : dis.disruption_type === "crew_unavailable" ? (
                            <Users className="h-3.5 w-3.5 text-blue-400" />
                          ) : (
                            <Truck className="h-3.5 w-3.5 text-amber-400" />
                          )}
                          <span className="capitalize">{dis.disruption_type.replace('_', ' ')}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-[9px] font-mono border-rose-500/30 text-rose-300">
                            DAY {dis.shoot_day}
                          </Badge>
                          {chaosDisruptions.length > 1 && (
                            <button
                              type="button"
                              onClick={() => {
                                const nextStack = [...chaosDisruptions];
                                nextStack.splice(idx, 1);
                                setChaosDisruptions(nextStack);
                              }}
                              className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-snug">{dis.reason}</p>
                    </div>
                  ))}
                </div>

                <div className="pt-2 flex items-center justify-between text-xs">
                  <button
                    type="button"
                    onClick={() => {
                      setChaosDisruptions([
                        {
                          disruption_type: "actor_unavailable",
                          resource_id: "act_01",
                          shoot_day: 6,
                          reason: "Dr. Sarah Mercer contractually unavailable on Day 6 due to emergency medical hold.",
                        },
                        {
                          disruption_type: "equipment_failure",
                          resource_id: "eq_01",
                          shoot_day: 6,
                          reason: "RED V-Raptor 8K primary camera package sensor shutter failure on Day 6.",
                        },
                        {
                          disruption_type: "bad_weather",
                          resource_id: "loc_04",
                          shoot_day: 6,
                          reason: "Severe torrential rain forecast halting outdoor filming at Glacier Pass on Day 6.",
                          weather_type: "Heavy Rain",
                          severity: "High",
                        },
                      ]);
                    }}
                    className="text-[11px] text-indigo-400 hover:underline flex items-center gap-1 font-medium"
                  >
                    <Layers className="h-3 w-3" /> Reset 3-Disruption Stack
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Select Broken Transport Vehicle</label>
                  <select
                    value={selectedVehicleId}
                    onChange={(e) => setSelectedVehicleId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="veh_01">🚐 Camera &amp; Grip Transport Van #1 (Location B Route)</option>
                    <option value="veh_02">🚚 Heavy Lighting &amp; Generator Truck #2</option>
                    <option value="veh_03">🚌 Cast &amp; Stunt Crew Transport Bus</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Impacted Shoot Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={logisticsShootDay}
                    onChange={(e) => setLogisticsShootDay(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Estimated Delay (Hours)</label>
                  <input
                    type="number"
                    min="1"
                    max="8"
                    value={logisticsDelayHours}
                    onChange={(e) => setLogisticsDelayHours(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Breakdown Reason</label>
                  <textarea
                    rows={3}
                    required
                    value={logisticsReason}
                    onChange={(e) => setLogisticsReason(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              </>
            )}

            <Button
              type="submit"
              isLoading={isAnalyzing}
              className={`w-full gap-2 ${
                scenarioMode === "chaos" ? "bg-rose-600 hover:bg-rose-500 border-rose-500/40" : ""
              }`}
            >
              {scenarioMode === "chaos" ? (
                <>
                  <Flame className="h-4 w-4 text-white" />
                  Analyze Multi-Disruption (Chaos Mode)
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Analyze Disruption &amp; Generate Recovery Plans
                </>
              )}
            </Button>
          </form>
        </Card>

        {/* AI Agent Output Panel */}
        <div className="lg:col-span-2 space-y-4">
          {isAnalyzing ? (
            <Card className="p-8 text-center bg-slate-900/90 border-slate-800 space-y-4">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="w-12 h-12 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
                  <Sparkles className="w-5 h-5 text-indigo-400 absolute inset-0 m-auto animate-pulse" />
                </div>
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-bold text-white tracking-wide">
                  {ANALYSIS_STEPS[analysisStepIndex]}
                </h3>
                <p className="text-xs text-slate-400">
                  Invoking Production Manager Agent &amp; ClickHouse deterministic intelligence tools...
                </p>
              </div>
              <div className="max-w-md mx-auto space-y-2 pt-2">
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                  <div
                    className="bg-indigo-500 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${((analysisStepIndex + 1) / ANALYSIS_STEPS.length) * 100}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                  <span>Step {analysisStepIndex + 1} of {ANALYSIS_STEPS.length}</span>
                  <span>{Math.round(((analysisStepIndex + 1) / ANALYSIS_STEPS.length) * 100)}%</span>
                </div>
              </div>
            </Card>
          ) : !analysisResult ? (
            <Card className="p-8 text-center text-slate-500 border-dashed space-y-2">
              <ShieldAlert className="h-8 w-8 text-slate-600 mx-auto" />
              <p className="text-sm font-semibold text-white">No Disruption Scenario Active</p>
              <p className="text-xs text-slate-400">
                Configure the scenario settings on the left and click &quot;Analyze Disruption&quot;.
              </p>
            </Card>
          ) : (
            <div className="space-y-5">
              {/* 🚨 Disruption Problem Alert Card */}
              <Card className="p-5 border-rose-500/40 bg-rose-950/20 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-rose-400 animate-pulse" />
                    <h2 className="text-base font-bold text-white tracking-tight">
                      🚨 {analysisResult.problem || `DISRUPTION: ${analysisResult.disruption?.actor_name}`}
                    </h2>
                  </div>
                  <Badge variant="danger" className="font-mono text-[10px]">
                    {analysisResult.active_disruption_count
                      ? `${analysisResult.active_disruption_count} ACTIVE DISRUPTIONS`
                      : `DAY ${analysisResult.disruption?.shoot_day || 6} AFFECTED`}
                  </Badge>
                </div>

                <p className="text-xs text-slate-300">
                  {analysisResult.disruption?.reason || "Multiple simultaneous disruptions logged on shoot day."}
                </p>

                {/* Detected Recovery Conflicts Alert Box (Chaos Mode) */}
                {analysisResult.detected_conflicts && analysisResult.detected_conflicts.length > 0 && (
                  <div className="p-3 bg-amber-950/40 rounded-lg border border-amber-500/50 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-amber-300 font-bold flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                        <AlertTriangle className="h-4 w-4 text-amber-400 animate-pulse" />
                        Independent Recovery Plan Conflicts Detected ({analysisResult.detected_conflicts.length})
                      </span>
                      <Badge variant="warning" className="text-[9px] font-mono">
                        COMBINED ENGINE RESOLUTION
                      </Badge>
                    </div>
                    <div className="space-y-1.5">
                      {analysisResult.detected_conflicts.map((c: any, idx: number) => (
                        <div key={idx} className="p-2.5 bg-slate-950/90 rounded border border-amber-900/60 text-[11px] space-y-1">
                          <div className="flex items-center justify-between font-semibold">
                            <span className="text-amber-200">⚡ {c.type?.toUpperCase()}</span>
                            <Badge variant="danger" className="text-[8px] font-mono">{c.severity || "HIGH"}</Badge>
                          </div>
                          <p className="text-slate-300 text-[11px] leading-snug">{c.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Affected Breakdown (Scenes, Dates, Crew, Locations) */}
                {analysisResult.affected ? (
                  <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-semibold block text-[11px]">Affected Scenes:</span>
                      <div className="space-y-0.5 font-medium text-white">
                        {analysisResult.affected.scenes?.map((s: string, idx: number) => (
                          <div key={idx}>{s}</div>
                        ))}
                      </div>
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-semibold block text-[11px]">Impacted Dates:</span>
                      <div className="space-y-0.5 font-medium text-amber-300">
                        {analysisResult.affected.dates?.map((d: string, idx: number) => (
                          <div key={idx}>{d}</div>
                        ))}
                      </div>
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-semibold block text-[11px]">Affected Crew / Cast:</span>
                      <div className="space-y-0.5 font-medium text-indigo-300">
                        {analysisResult.affected.crew?.map((c: string, idx: number) => (
                          <div key={idx}>{c}</div>
                        )) || (
                          analysisResult.affected.actors?.map((a: string, idx: number) => (
                            <div key={idx}>{a}</div>
                          ))
                        )}
                      </div>
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-semibold block text-[11px]">Filming Location:</span>
                      <div className="space-y-0.5 font-medium text-purple-300">
                        {analysisResult.affected.locations ? (
                          analysisResult.affected.locations.map((l: string, idx: number) => (
                            <div key={idx}>{l}</div>
                          ))
                        ) : (
                          <div>{analysisResult.affected.original_location || "Original Location"}</div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-semibold block text-[11px]">Stalled Scenes ({analysisResult.affected_scenes?.length || 0}):</span>
                      {analysisResult.affected_scenes?.map((s: any) => (
                        <div key={s.scene_id} className="text-white font-medium">
                          Scene {s.scene_number}: {s.title}
                        </div>
                      ))}
                    </div>
                    <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-semibold block text-[11px]">Affected Resources:</span>
                      <div className="flex flex-wrap gap-1">
                        {analysisResult.affected_resources?.map((res: string, i: number) => (
                          <Badge key={i} variant="outline" className="text-[10px]">
                            {res}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Alternative Approved Locations list (Scenario 3) */}
                {analysisResult.alternative_locations && analysisResult.alternative_locations.length > 0 && (
                  <div className="p-3 bg-emerald-950/30 rounded-lg border border-emerald-900/50 text-xs space-y-1">
                    <span className="text-emerald-300 font-semibold flex items-center gap-1.5">
                      <Building className="h-3.5 w-3.5 text-emerald-400" />
                      Approved Alternative Locations ({analysisResult.alternative_locations.length}):
                    </span>
                    <div className="flex flex-wrap gap-2 pt-1">
                      {analysisResult.alternative_locations.map((alt: any, idx: number) => (
                        <Badge key={idx} variant="success" className="text-[10px] gap-1">
                          📍 {alt.name} ({alt.indoor_outdoor}) — {formatCurrency(alt.daily_rate)}/day
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Alternative Indoor Scenes & Alternative Dates (Scenario 4 Bad Weather) */}
                {analysisResult.alternative_indoor_scenes && analysisResult.alternative_indoor_scenes.length > 0 && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 text-xs">
                    <div className="p-3 bg-amber-950/30 rounded-lg border border-amber-900/50 space-y-1">
                      <span className="text-amber-300 font-semibold flex items-center gap-1.5">
                        <Building className="h-3.5 w-3.5 text-amber-400" />
                        Alternative Indoor Cover Scenes ({analysisResult.alternative_indoor_scenes.length}):
                      </span>
                      <div className="space-y-1 pt-1">
                        {analysisResult.alternative_indoor_scenes.slice(0, 3).map((cs: any) => (
                          <div key={cs.scene_id} className="text-slate-200 text-[11px] font-medium flex items-center justify-between border-b border-amber-900/30 pb-0.5">
                            <span>Scene {cs.scene_number}: {cs.title}</span>
                            <Badge variant="outline" className="text-[9px]">Stage 4 Bunker</Badge>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-3 bg-indigo-950/30 rounded-lg border border-indigo-900/50 space-y-1">
                      <span className="text-indigo-300 font-semibold flex items-center gap-1.5">
                        <Calendar className="h-3.5 w-3.5 text-indigo-400" />
                        Alternative Outdoor Shooting Dates ({analysisResult.alternative_dates?.length || 0}):
                      </span>
                      <div className="space-y-1 pt-1">
                        {analysisResult.alternative_dates?.slice(0, 3).map((d: any, idx: number) => (
                          <div key={idx} className="text-slate-200 text-[11px] font-medium flex items-center justify-between border-b border-indigo-900/30 pb-0.5">
                            <span>Day {d.shoot_day} ({d.date})</span>
                            <span className="text-emerald-400 font-mono text-[10px]">{d.forecast}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Qualified Replacement Crew Candidates (Scenario 5 Crew Unavailable) */}
                {analysisResult.qualified_replacements && analysisResult.qualified_replacements.length > 0 && (
                  <div className="p-3 bg-blue-950/30 rounded-lg border border-blue-900/50 text-xs space-y-1">
                    <span className="text-blue-300 font-semibold flex items-center gap-1.5">
                      <Users className="h-3.5 w-3.5 text-blue-400" />
                      Qualified Replacement Crew Candidates ({analysisResult.qualified_replacements.length}):
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                      {analysisResult.qualified_replacements.map((rep: any, idx: number) => (
                        <div key={idx} className="p-2 bg-slate-950/80 rounded border border-slate-800 space-y-0.5">
                          <div className="flex items-center justify-between text-white font-semibold">
                            <span>{rep.name}</span>
                            <span className="text-emerald-400 font-mono text-[10px]">{formatCurrency(rep.daily_rate)}/day</span>
                          </div>
                          <div className="text-[10px] text-slate-400">{rep.role} ({rep.department})</div>
                          <div className="text-[9px] text-blue-400">{rep.source}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Dispatch Feasibility Info (Scenario 6 Logistics) */}
                {analysisResult.dispatch_feasibility && (
                  <div className="p-3 bg-amber-950/30 rounded-lg border border-amber-900/50 text-xs space-y-1">
                    <span className="text-amber-300 font-semibold flex items-center gap-1.5">
                      <Truck className="h-3.5 w-3.5 text-amber-400" />
                      Emergency Transport Dispatch Feasibility:
                    </span>
                    <div className="grid grid-cols-2 gap-2 pt-1">
                      <div className="p-2 bg-slate-950/80 rounded border border-slate-800 text-[11px]">
                        <span className="text-slate-400 block">Backup Hot-Shot Courier:</span>
                        <span className="text-emerald-400 font-medium">Available ({analysisResult.dispatch_feasibility.backup_transport_eta_hours}-Hr ETA Delay)</span>
                      </div>
                      <div className="p-2 bg-slate-950/80 rounded border border-slate-800 text-[11px]">
                        <span className="text-slate-400 block">Base Camp Cover Set:</span>
                        <span className="text-indigo-300 font-medium">Stage 4 Soundstage Pre-rigged</span>
                      </div>
                    </div>
                  </div>
                )}
              </Card>

              {/* 🛠️ Deterministic Tool Execution Trace Card */}
              {analysisResult.tool_execution_trace && analysisResult.tool_execution_trace.length > 0 && (
                <Card className="p-4 bg-slate-900/90 border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-indigo-400 flex items-center gap-1.5 uppercase tracking-wider">
                      <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
                      Production Manager Agent Tool Execution Trace ({analysisResult.tool_execution_trace.length} Steps)
                    </span>
                    <Badge variant="outline" className="text-[9px] font-mono border-indigo-500/30 text-indigo-300">
                      DETERMINISTIC AGENT TOOL LOG
                    </Badge>
                  </div>
                  <div className="space-y-1.5 pt-1">
                    {analysisResult.tool_execution_trace.map((step: any, idx: number) => (
                      <div key={idx} className="p-2 bg-slate-950 rounded border border-slate-800 flex items-start justify-between text-xs">
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2">
                            <span className="px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 font-mono text-[10px] font-bold">
                              STEP {step.step}
                            </span>
                            <span className="text-white font-mono font-semibold text-[11px]">
                              {step.tool}()
                            </span>
                            <span className="text-slate-500 text-[10px] italic">({step.phase})</span>
                          </div>
                          <p className="text-slate-300 text-[11px] pl-1">{step.summary}</p>
                        </div>
                        <Badge variant="success" className="text-[8px] font-mono">EXECUTED</Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {/* Recovery Options Selector */}
              <div className="space-y-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">
                  AI Candidate Recovery Solutions ({analysisResult.recovery_options.length})
                </span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {analysisResult.recovery_options.map((opt: any, idx: number) => {
                    const isSelected = selectedOptionIndex === idx;
                    return (
                      <button
                        key={opt.option_id}
                        onClick={() => setSelectedOptionIndex(idx)}
                        className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                          isSelected
                            ? "bg-indigo-600/20 border-indigo-500 shadow-md"
                            : "bg-slate-900 border-slate-800 hover:bg-slate-800/60"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-white">{opt.strategy}</span>
                          {opt.is_recommended && (
                            <Badge variant="success" className="text-[9px]">
                              RECOMMENDED
                            </Badge>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 line-clamp-2">{opt.title}</p>
                        <div className="mt-2 flex items-center justify-between text-[10px] font-mono border-t border-slate-800/60 pt-1.5">
                          <span className="text-emerald-400">{formatCurrency(opt.cost_variance_usd)}</span>
                          <span className="text-indigo-300">{opt.schedule_variance_days} Days Shift</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Impact Metrics & AI Rationale */}
              {selectedPlan && (
                <Card className="p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white">{selectedPlan.title}</h3>
                      <p className="text-xs text-slate-400">{selectedPlan.summary}</p>
                    </div>
                    <Badge variant="info">AI Confidence: {(analysisResult.confidence * 100).toFixed(0)}%</Badge>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block">Estimated Delay</span>
                      <span className="text-sm font-bold text-white">
                        {selectedPlan.schedule_variance_days > 0
                          ? `+${selectedPlan.schedule_variance_days} Days Shift`
                          : "0 Days Shift (No Delay)"}
                      </span>
                    </div>
                    <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block">Additional Cost</span>
                      <span className="text-sm font-bold text-emerald-400">
                        {formatCurrency(selectedPlan.cost_variance_usd)}
                      </span>
                    </div>
                    <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block">Resources Affected</span>
                      <span className="text-sm font-bold text-indigo-300">
                        {selectedPlan.affected_resource_count ?? analysisResult.affected?.crew?.length ?? 12}
                      </span>
                    </div>
                    <div className="p-2.5 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 uppercase block">Scenes Moved</span>
                      <span className="text-sm font-bold text-purple-300">
                        {selectedPlan.scenes_moved_count ?? analysisResult.affected_scenes?.length ?? 2}
                      </span>
                    </div>
                  </div>

                  {/* Why / Rationale */}
                  <div className="p-3.5 rounded-lg bg-indigo-950/30 border border-indigo-900/50 text-xs space-y-1">
                    <span className="font-semibold text-indigo-300 flex items-center gap-1.5">
                      <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
                      Why This Plan Was Selected:
                    </span>
                    <p className="text-slate-300 leading-relaxed">{analysisResult.reasoning}</p>
                  </div>

                  {/* Side-by-Side Schedule Comparison */}
                  <ScheduleComparison
                    shootDay={analysisResult.disruption?.shoot_day || 6}
                    affectedScenes={analysisResult.affected_scenes}
                    proposedChanges={selectedPlan.proposed_changes || []}
                    selectedOptionTitle={selectedPlan.strategy}
                  />

                  {/* Producer Sign-off Controls */}
                  <div className="pt-3 border-t border-slate-800 space-y-3">
                    {approvalStatus && (
                      <div
                        className={`p-3 rounded-lg text-xs font-semibold text-center border ${
                          approvalStatus === "APPROVED"
                            ? "bg-emerald-950/60 border-emerald-800 text-emerald-300"
                            : "bg-rose-950/60 border-rose-800 text-rose-300"
                        }`}
                      >
                        {approvalStatus === "APPROVED"
                          ? "✓ RECOVERY PLAN APPROVED BY PRODUCER. Schedule changes committed."
                          : "✕ RECOVERY PLAN REJECTED. Retaining original call sheets."}
                      </div>
                    )}

                    {isModifying && (
                      <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                        <label className="block text-xs font-medium text-slate-300">
                          Producer Modification Notes:
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. Approved provided camera courier arrives before 11:30 AM..."
                          value={producerNotes}
                          onChange={(e) => setProducerNotes(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-xs text-white"
                        />
                      </div>
                    )}

                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setIsModifying(!isModifying)}
                        className="text-xs gap-1.5"
                      >
                        <Edit3 className="h-3.5 w-3.5" />
                        {isModifying ? "Cancel Modification" : "Modify Plan"}
                      </Button>

                      <div className="flex items-center gap-2">
                        <Button
                          type="button"
                          variant="danger"
                          size="md"
                          onClick={handleReject}
                          className="gap-1.5"
                        >
                          <XCircle className="h-4 w-4" />
                          Reject
                        </Button>
                        <Button
                          type="button"
                          variant="primary"
                          size="md"
                          onClick={handleApprove}
                          className="gap-1.5 bg-emerald-600 hover:bg-emerald-500 border-emerald-500/30"
                        >
                          <CheckCircle2 className="h-4 w-4" />
                          Approve Recovery Plan
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
