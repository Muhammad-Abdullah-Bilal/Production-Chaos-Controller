export type IndoorOutdoor = "Indoor" | "Outdoor";
export type PriorityLevel = "High" | "Medium" | "Low";
export type SceneStatus = "Scheduled" | "In Progress" | "Completed" | "Moveable" | "Hard Fixed";

export interface Actor {
  actor_id: string;
  name: string;
  character_name: string;
  is_lead: boolean;
  daily_rate: number;
  contact_info?: string | null;
  availability_notes?: string | null;
}

export interface CrewMember {
  crew_id: string;
  name: string;
  department: string;
  role: string;
  daily_rate: number;
}

export interface Location {
  location_id: string;
  name: string;
  address: string;
  indoor_outdoor: IndoorOutdoor;
  daily_rate: number;
  permit_required: boolean;
  weather_vulnerable: boolean;
  notes?: string | null;
}

export interface Equipment {
  equipment_id: string;
  name: string;
  category: string;
  daily_rate: number;
  is_critical: boolean;
}

export interface Scene {
  scene_id: string;
  scene_number: string;
  title: string;
  description: string;
  shooting_date: string;
  start_time: string;
  duration: number;
  location_id: string;
  actor_ids: string[];
  crew_ids: string[];
  equipment_ids: string[];
  estimated_cost: number;
  priority: PriorityLevel;
  indoor_outdoor: IndoorOutdoor;
  weather_sensitive: boolean;
  status: SceneStatus;
}

export interface ShootingDay {
  day_number: number;
  date: string;
  call_time: string;
  wrap_time: string;
  location_id: string;
  scene_ids: string[];
  estimated_daily_cost: number;
  notes?: string | null;
}

export interface ProductionSchedule {
  id: string;
  project_title: string;
  director: string;
  producer: string;
  total_budget: number;
  daily_burn_rate: number;
  start_date: string;
  total_days: number;
  scenes: Scene[];
  actors: Actor[];
  crew: CrewMember[];
  locations: Location[];
  equipment: Equipment[];
  shooting_days: ShootingDay[];
}

export type DisruptionType =
  | "actor_unavailable"
  | "equipment_failure"
  | "location_unavailable"
  | "bad_weather"
  | "crew_unavailable"
  | "transportation_logistics";

export type SeverityLevel = "low" | "medium" | "high" | "critical";

export interface DisruptionEvent {
  id: string;
  title: string;
  description: string;
  disruption_type: DisruptionType;
  severity: SeverityLevel;
  reported_by: string;
  reported_at: string;
  shoot_day_affected: number;
  affected_resource_ids: string[];
  affected_scene_ids: string[];
  is_active: boolean;
}

export type PlanStatus = "draft" | "proposed" | "approved" | "rejected" | "applied";

export interface ScheduleChange {
  scene_id: string;
  scene_number: string;
  action: string;
  original_day: number;
  target_day: number;
  reason: string;
  resource_substitutions: Record<string, string>;
}

export interface ImpactAssessment {
  schedule_variance_days: number;
  cost_variance_usd: number;
  affected_actor_count: number;
  affected_crew_count: number;
  rescheduled_scene_count: number;
  risk_score: number;
  key_risks: string[];
}

export interface RecoveryPlan {
  id: string;
  disruption_id: string;
  title: string;
  summary: string;
  rationale: string;
  is_recommended: boolean;
  status: PlanStatus;
  changes: ScheduleChange[];
  impact: ImpactAssessment;
  created_at: string;
  human_approved_by?: string | null;
  human_approved_at?: string | null;
  approval_notes?: string | null;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  environment: string;
  timestamp: string;
  integrations?: {
    clickhouse?: {
      status: string;
      mcp_enabled: boolean;
      host: string;
      port: number;
      message: string;
    };
    agent_orchestrator?: {
      ready: boolean;
      configured: boolean;
      registered_tools_count: number;
    };
    database?: {
      active_schedules: number;
      recorded_disruptions: number;
    };
  };
}
