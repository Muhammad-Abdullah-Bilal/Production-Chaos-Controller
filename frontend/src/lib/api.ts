import {
  HealthStatus,
  ProductionSchedule,
  Scene,
  Actor,
  CrewMember,
  Location,
  Equipment,
  ShootingDay,
  DisruptionEvent,
  RecoveryPlan,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store",
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API error ${res.status}: ${errorText || res.statusText}`);
    }

    return (await res.json()) as T;
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unexpected network error occurred.");
  }
}

export const api = {
  getHealth: (): Promise<HealthStatus> => fetchJson<HealthStatus>("/api/v1/health"),
  getProduction: (): Promise<ProductionSchedule> => fetchJson<ProductionSchedule>("/api/production"),
  getScenes: (params?: { location_id?: string; indoor_outdoor?: string; priority?: string }): Promise<Scene[]> => {
    const query = new URLSearchParams();
    if (params?.location_id) query.append("location_id", params.location_id);
    if (params?.indoor_outdoor) query.append("indoor_outdoor", params.indoor_outdoor);
    if (params?.priority) query.append("priority", params.priority);
    const queryString = query.toString() ? `?${query.toString()}` : "";
    return fetchJson<Scene[]>(`/api/scenes${queryString}`);
  },
  getActors: (): Promise<Actor[]> => fetchJson<Actor[]>("/api/actors"),
  getCrew: (): Promise<CrewMember[]> => fetchJson<CrewMember[]>("/api/crew"),
  getLocations: (): Promise<Location[]> => fetchJson<Location[]>("/api/locations"),
  getEquipment: (): Promise<Equipment[]> => fetchJson<Equipment[]>("/api/equipment"),
  getSchedule: (): Promise<ShootingDay[]> => fetchJson<ShootingDay[]>("/api/schedule"),
  
  // Disruption Scenario APIs
  triggerActorDisruption: (payload: { actor_id: string; shoot_day: number; reason: string }): Promise<any> =>
    fetchJson<any>("/api/disruptions/actor-unavailable", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  triggerEquipmentDisruption: (payload: { equipment_id: string; shoot_day: number; reason: string }): Promise<any> =>
    fetchJson<any>("/api/disruptions/equipment-failure", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  triggerLocationDisruption: (payload: { location_id: string; shoot_day: number; reason: string }): Promise<any> =>
    fetchJson<any>("/api/disruptions/location-unavailable", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  triggerWeatherDisruption: (payload: { weather_type: string; severity: string; shoot_day: number; reason: string }): Promise<any> =>
    fetchJson<any>("/api/disruptions/bad-weather", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  triggerCrewDisruption: (payload: { crew_id: string; shoot_day: number; reason: string }): Promise<any> =>
    fetchJson<any>("/api/disruptions/crew-unavailable", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  triggerLogisticsDisruption: (payload: { vehicle_id: string; shoot_day: number; delay_hours: number; reason: string }): Promise<any> =>
    fetchJson<any>("/api/disruptions/logistics-delay", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  analyzeDisruption: (payload: { disruption_type: string; resource_id: string; shoot_day: number; reason?: string }): Promise<any> =>
    fetchJson<any>("/api/v1/disruptions/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  triggerMultiDisruptionAnalysis: (payload: {
    disruptions: Array<{
      disruption_type: string;
      resource_id: string;
      shoot_day: number;
      reason?: string;
      weather_type?: string;
      severity?: string;
    }>;
  }): Promise<any> =>
    fetchJson<any>("/api/v1/disruptions/multi-analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),




  // Generic Disruption & Recovery APIs
  getDisruptions: (): Promise<DisruptionEvent[]> => fetchJson<DisruptionEvent[]>("/api/v1/disruptions"),
  createDisruption: (payload: Partial<DisruptionEvent>): Promise<DisruptionEvent> =>
    fetchJson<DisruptionEvent>("/api/v1/disruptions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getRecoveryPlans: (disruptionId: string): Promise<RecoveryPlan[]> =>
    fetchJson<RecoveryPlan[]>(`/api/v1/disruptions/${disruptionId}/plans`),
  approveRecoveryPlan: (
    planId: string,
    payload: { approved_by: string; notes?: string; approved: boolean }
  ): Promise<RecoveryPlan> =>
    fetchJson<RecoveryPlan>(`/api/v1/disruptions/plans/${planId}/approve`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // ClickHouse Production Analytics & MCP APIs
  getClickHouseStatus: (): Promise<{ status: string; data_source: string; host: string; port: number; database: string; message: string }> =>
    fetchJson<{ status: string; data_source: string; host: string; port: number; database: string; message: string }>("/api/v1/analytics/clickhouse/status"),
  syncClickHouse: (): Promise<any> =>
    fetchJson<any>("/api/v1/analytics/clickhouse/sync", { method: "POST" }),
  runClickHouseQuery: (queryName: string, params?: Record<string, any>): Promise<any> =>
    fetchJson<any>("/api/v1/analytics/clickhouse/query", {
      method: "POST",
      body: JSON.stringify({ query_name: queryName, params: params || {} }),
    }),
  getClickHouseMcpManifest: (): Promise<any> =>
    fetchJson<any>("/api/v1/mcp/clickhouse"),
};
