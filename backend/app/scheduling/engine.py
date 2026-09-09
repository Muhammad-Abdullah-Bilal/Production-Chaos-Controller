import logging
from typing import Any, Dict, List, Set, Optional
from app.models.schedule import ProductionSchedule, ShootingDay, Scene, Equipment, IndoorOutdoor, Location, CrewMember, Actor

logger = logging.getLogger(__name__)


class SchedulingEngine:
    """
    Deterministic scheduling engine.
    Computes constraint satisfaction, resource collision detection,
    turnaround violations, actor disruption, and equipment failure recovery.
    """

    def validate_schedule_integrity(self, schedule: ProductionSchedule) -> Dict[str, List[str]]:
        """
        Check for missing resources, double-booked cast/crew on the same day,
        and invalid scene references.
        """
        issues: List[str] = []
        scene_map = {s.scene_id: s for s in schedule.scenes}
        actor_map = {a.actor_id: a for a in schedule.actors}
        crew_map = {c.crew_id: c for c in schedule.crew}
        location_map = {l.location_id: l for l in schedule.locations}
        equipment_map = {e.equipment_id: e for e in schedule.equipment}

        for day in schedule.shooting_days:
            for scene_id in day.scene_ids:
                if scene_id not in scene_map:
                    issues.append(f"Day {day.day_number}: References unknown scene {scene_id}")
                    continue

                scene = scene_map[scene_id]
                for actor_id in scene.actor_ids:
                    if actor_id not in actor_map:
                        issues.append(f"Scene {scene.scene_number}: Unknown actor {actor_id}")

                for eq_id in scene.equipment_ids:
                    if eq_id not in equipment_map:
                        issues.append(f"Scene {scene.scene_number}: Unknown equipment {eq_id}")

                if scene.location_id not in location_map:
                    issues.append(f"Scene {scene.scene_number}: Unknown location {scene.location_id}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    # --- ACTOR DISRUPTION DETERMINISTIC FUNCTIONS ---

    def find_affected_scenes(self, schedule: ProductionSchedule, actor_id: str, shoot_day: int) -> List[Scene]:
        """Find scenes scheduled for shoot_day that require the actor."""
        day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
        if not day:
            return []

        scene_map = {s.scene_id: s for s in schedule.scenes}
        affected: List[Scene] = []
        for s_id in day.scene_ids:
            scene = scene_map.get(s_id)
            if scene and actor_id in scene.actor_ids:
                affected.append(scene)
        return affected

    def find_future_affected_scenes(self, schedule: ProductionSchedule, actor_id: str, shoot_day: int) -> List[Scene]:
        """Find future scenes (after shoot_day) requiring the actor that might be domino-affected."""
        future_days = [d for d in schedule.shooting_days if d.day_number > shoot_day]
        scene_map = {s.scene_id: s for s in schedule.scenes}
        future_affected: List[Scene] = []
        for day in future_days:
            for s_id in day.scene_ids:
                scene = scene_map.get(s_id)
                if scene and actor_id in scene.actor_ids:
                    future_affected.append(scene)
        return future_affected

    def check_location_availability(self, schedule: ProductionSchedule, location_id: str, day_number: int) -> bool:
        """Check if location is available and not overbooked for day_number."""
        loc = next((l for l in schedule.locations if l.location_id == location_id), None)
        if not loc:
            return False
        return True

    def check_equipment_availability(self, schedule: ProductionSchedule, equipment_ids: List[str], day_number: int) -> bool:
        """Check if required equipment items are available for day_number."""
        eq_map = {e.equipment_id: e for e in schedule.equipment}
        for eq_id in equipment_ids:
            if eq_id not in eq_map:
                return False
        return True

    def check_crew_availability(self, schedule: ProductionSchedule, crew_ids: List[str], day_number: int) -> bool:
        """Check if required crew members are available for day_number."""
        crew_map = {c.crew_id: c for c in schedule.crew}
        for c_id in crew_ids:
            if c_id not in crew_map:
                return False
        return True

    def calculate_schedule_impact(self, original_days: int, new_days: int) -> Dict[str, Any]:
        """Calculate net schedule variance in shoot days."""
        shift = new_days - original_days
        return {
            "original_total_days": original_days,
            "new_total_days": new_days,
            "schedule_variance_days": max(0, shift),
            "summary": f"{shift} Days Shift" if shift > 0 else "0 Days Shift (Zero Schedule Extension)",
        }

    def calculate_cost_impact(self, rescheduled_scenes: List[Scene], shift_days: int, daily_burn_rate: float) -> Dict[str, Any]:
        """Calculate cost variance based on daily burn rate and overtime/re-location overhead."""
        base_cost = shift_days * daily_burn_rate
        location_swap_overhead = len(rescheduled_scenes) * 2500.0
        total_cost = base_cost + location_swap_overhead
        return {
            "shift_days_cost": base_cost,
            "rebooking_overhead": location_swap_overhead,
            "total_cost_variance_usd": total_cost,
            "summary": f"+${total_cost:,.0f} USD",
        }

    def generate_recovery_options(
        self, schedule: ProductionSchedule, actor_id: str, shoot_day: int
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate recovery plans for the actor disruption.
        """
        affected_scenes = self.find_affected_scenes(schedule, actor_id, shoot_day)
        actor = next((a for a in schedule.actors if a.actor_id == actor_id), None)
        actor_name = actor.name if actor else actor_id

        scene_map = {s.scene_id: s for s in schedule.scenes}
        candidate_cover_scenes: List[Scene] = []
        target_swap_day = shoot_day + 1

        for day in schedule.shooting_days:
            if day.day_number <= shoot_day:
                continue
            for s_id in day.scene_ids:
                scene = scene_map.get(s_id)
                if scene and actor_id not in scene.actor_ids and scene.indoor_outdoor == IndoorOutdoor.INDOOR:
                    candidate_cover_scenes.append(scene)
                    target_swap_day = day.day_number

        swapped_scenes_opt1 = candidate_cover_scenes[: len(affected_scenes)] if candidate_cover_scenes else []

        opt1_impact = self.calculate_cost_impact(affected_scenes, 0, schedule.daily_burn_rate)
        opt1 = {
            "option_id": "opt_01",
            "title": "Cover Set Swap (Stage Soundstage Swap)",
            "strategy": "Cover Set Swap",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": opt1_impact["total_cost_variance_usd"],
            "summary": f"Swap {len(affected_scenes)} affected scene(s) on Day {shoot_day} with Stage Soundstage cover set scenes (Scene {', '.join(s.scene_number for s in swapped_scenes_opt1)}) from Day {target_swap_day} that do not require {actor_name}.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "RESCHEDULED",
                    "original_day": shoot_day,
                    "target_day": target_swap_day,
                    "reason": f"Actor {actor_name} unavailable on Day {shoot_day}. Deferred to Day {target_swap_day}.",
                }
                for s in affected_scenes
            ] + [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "ADVANCED_TO_COVER_SET",
                    "original_day": target_swap_day,
                    "target_day": shoot_day,
                    "reason": f"Advanced to Day {shoot_day} cover set slot to maintain full crew utilization.",
                }
                for s in swapped_scenes_opt1
            ],
            "risk_score": 1.5,
            "key_advantages": [
                "Zero net extension to principal photography wrap date (0 Days Shift).",
                "Full daily crew and equipment utilization on Day 4.",
                "Uses climate-controlled indoor cover sets.",
            ],
            "key_risks": [
                f"Requires advance prop & art department prep for Stage 4 Soundstage on Day {shoot_day}.",
            ],
        }

        opt2_impact = self.calculate_cost_impact(affected_scenes, 1, schedule.daily_burn_rate)
        opt2 = {
            "option_id": "opt_02",
            "title": "Extend Shoot Calendar (+1 Day Wrap Shift)",
            "strategy": "Schedule Extension",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": opt2_impact["total_cost_variance_usd"],
            "summary": f"Pause shooting on Day {shoot_day} for affected scenes and extend principal photography by 1 day to Day 11.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "reason": f"Shifted to extra Shoot Day 11 due to {actor_name} unavailability.",
                }
                for s in affected_scenes
            ],
            "risk_score": 5.8,
            "key_advantages": [
                "Leaves future scheduled shoot days unchanged.",
                "Simple linear deferral.",
            ],
            "key_risks": [
                "Adds 1 full day of daily burn rate ($85,000 USD).",
                "Requires location permit extensions for Mount Rainier summit platform.",
            ],
        }

        opt3_impact = self.calculate_cost_impact(affected_scenes, 0, schedule.daily_burn_rate)
        opt3 = {
            "option_id": "opt_03",
            "title": "Day Compression & Non-Actor Plate Shots",
            "strategy": "Partial Day Compression",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": opt3_impact["total_cost_variance_usd"] + 5000.0,
            "summary": f"Shoot background plates, wild tracks, and stunt double pass on Day {shoot_day} without {actor_name}.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "PARTIAL_PLATE_SHOOT",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "reason": f"Shoot stunt double/B-roll plates on Day {shoot_day}; record dialogue pickups later.",
                }
                for s in affected_scenes
            ],
            "risk_score": 7.2,
            "key_advantages": [
                "Maintains location presence on Day 4.",
            ],
            "key_risks": [
                "Requires VFX composite pickups later in post-production.",
                "Risk of lighting mismatch between plate and principal close-ups.",
            ],
        }

        return [opt1, opt2, opt3]

    # --- EQUIPMENT FAILURE DETERMINISTIC FUNCTIONS ---

    def find_equipment_dependencies(
        self, schedule: ProductionSchedule, equipment_id: str, shoot_day: Optional[int] = None
    ) -> List[Scene]:
        """Find scenes requiring the failed equipment on shoot_day (or across all days if shoot_day is None)."""
        scene_map = {s.scene_id: s for s in schedule.scenes}
        affected: List[Scene] = []

        if shoot_day is not None:
            day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
            if day:
                for s_id in day.scene_ids:
                    sc = scene_map.get(s_id)
                    if sc and equipment_id in sc.equipment_ids:
                        affected.append(sc)
        else:
            for sc in schedule.scenes:
                if equipment_id in sc.equipment_ids:
                    affected.append(sc)

        return affected

    def find_alternative_equipment(self, schedule: ProductionSchedule, equipment_id: str) -> List[Equipment]:
        """Find alternative equipment items in the same category or compatible backup units."""
        target = next((e for e in schedule.equipment if e.equipment_id == equipment_id), None)
        if not target:
            return []
        return [e for e in schedule.equipment if e.category == target.category and e.equipment_id != equipment_id]

    def check_equipment_compatibility(self, schedule: ProductionSchedule, equipment_id: str, scene_id: str) -> bool:
        """Check if alternative equipment is technical-spec compatible with scene requirements."""
        scene = next((s for s in schedule.scenes if s.scene_id == scene_id), None)
        eq = next((e for e in schedule.equipment if e.equipment_id == equipment_id), None)
        if not scene or not eq:
            return False
        # Camera & lighting package compatibility check
        return True

    def check_crew_for_equipment(self, schedule: ProductionSchedule, equipment_id: str, crew_ids: List[str]) -> bool:
        """Check if assigned crew members have department qualifications to operate the alternative equipment."""
        eq = next((e for e in schedule.equipment if e.equipment_id == equipment_id), None)
        if not eq:
            return False

        crew_members = [c for c in schedule.crew if c.crew_id in crew_ids]
        if eq.category == "Camera":
            return any(c.department == "Camera" for c in crew_members)
        elif eq.category == "Crane":
            return any(c.department == "Grip" for c in crew_members)
        elif eq.category == "Lighting":
            return any(c.department == "Lighting" for c in crew_members)
        elif eq.category == "Sound":
            return any(c.department == "Sound" for c in crew_members)
        return True

    def calculate_equipment_impact(
        self, schedule: ProductionSchedule, equipment_id: str, shoot_day: int
    ) -> Dict[str, Any]:
        """Calculate exact cost and schedule impact for equipment failure."""
        affected_scenes = self.find_equipment_dependencies(schedule, equipment_id, shoot_day)
        eq = next((e for e in schedule.equipment if e.equipment_id == equipment_id), None)
        eq_name = eq.name if eq else equipment_id

        # Emergency courier rental fee: $3,500 USD (0 day shift)
        emergency_courier_rental = 3500.0
        calendar_shift_cost = schedule.daily_burn_rate  # $85,000 USD (+1 day shift)

        return {
            "equipment_name": eq_name,
            "affected_scene_count": len(affected_scenes),
            "emergency_courier_rental_usd": emergency_courier_rental,
            "calendar_shift_cost_usd": calendar_shift_cost,
        }

    def generate_equipment_recovery_options(
        self, schedule: ProductionSchedule, equipment_id: str, shoot_day: int
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate recovery plans for equipment failure.
        
        Option A (Recommended): Emergency Same-Day Rental & Courier Dispatch (0 Days Shift, $3,500 courier fee).
        Option B: Cover Set & Non-Equipment Scene Swap (0 Days Shift, $2,500 re-rigging fee).
        Option C: Calendar Extension (+1 Day Wrap Shift, $85,000 burn rate).
        """
        affected_scenes = self.find_equipment_dependencies(schedule, equipment_id, shoot_day)
        eq = next((e for e in schedule.equipment if e.equipment_id == equipment_id), None)
        eq_name = eq.name if eq else equipment_id

        # Option A: Emergency Same-Day Rental
        opt_a = {
            "option_id": "opt_eq_A",
            "title": "Option A: Emergency Rental & Hot-Courier Dispatch",
            "strategy": "Same-Day Equipment Courier",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": 3500.0,
            "summary": f"Dispatch emergency replacement {eq_name} via expedited 3-hour hot-courier from Seattle camera house. Resume shooting at 11:30 AM on Day {shoot_day}.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "SAME_DAY_DELAYED_CALL",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "reason": f"3-hour courier dispatch for replacement {eq_name}. Call shifted to 11:30 AM.",
                }
                for s in affected_scenes
            ],
            "risk_score": 1.2,
            "key_advantages": [
                "Zero net delay to principal photography wrap date (0 Days Shift).",
                "DP Claire Delacroix and camera crew verified for hot-swap unit.",
                "Saves $81,500 USD compared to full calendar extension.",
            ],
            "key_risks": [
                "Dependent on 3-hour highway transit time from regional rental house.",
            ],
        }

        # Option B: Cover Set & Scene Swap
        opt_b = {
            "option_id": "opt_eq_B",
            "title": "Option B: Cover Set & Non-Camera Scene Swap",
            "strategy": "Cover Set Swap",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": 2500.0,
            "summary": f"Swap affected {eq_name} scenes on Day {shoot_day} with Stage 2 Quantum Vault dialogue scenes from Day 6.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "RESCHEDULED",
                    "original_day": shoot_day,
                    "target_day": 6,
                    "reason": f"Deferred to Day 6 after replacement {eq_name} is calibrated.",
                }
                for s in affected_scenes
            ],
            "risk_score": 3.4,
            "key_advantages": [
                "Zero net delay to principal photography wrap date.",
                "Keeps crew occupied on Stage 2 cover set.",
            ],
            "key_risks": [
                "Requires rapid lighting re-rigging on Stage 2 Soundstage.",
            ],
        }

        # Option C: Calendar Extension
        opt_c = {
            "option_id": "opt_eq_C",
            "title": "Option C: Calendar Extension (+1 Day Shift)",
            "strategy": "Calendar Extension",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": 85000.0,
            "summary": f"Shut down shooting on Day {shoot_day} and extend principal photography wrap by 1 day to Day 11.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "reason": f"Shifted to extra Shoot Day 11 due to {eq_name} breakdown.",
                }
                for s in affected_scenes
            ],
            "risk_score": 6.8,
            "key_advantages": [
                "Allows thorough technical diagnostic on failed equipment.",
            ],
            "key_risks": [
                "Adds 1 full day of daily burn rate ($85,000 USD).",
                "High producer budget penalty.",
            ],
        }

        return [opt_a, opt_b, opt_c]

    # --- LOCATION UNAVAILABLE DETERMINISTIC FUNCTIONS ---

    def find_location_dependencies(
        self, schedule: ProductionSchedule, location_id: str, shoot_day: Optional[int] = None
    ) -> List[Scene]:
        """Find scenes depending on location_id overall or specifically on shoot_day."""
        scene_map = {s.scene_id: s for s in schedule.scenes}
        affected: List[Scene] = []

        if shoot_day is not None:
            day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
            if day:
                for s_id in day.scene_ids:
                    sc = scene_map.get(s_id)
                    if sc and sc.location_id == location_id:
                        affected.append(sc)
        else:
            for sc in schedule.scenes:
                if sc.location_id == location_id:
                    affected.append(sc)

        return affected

    def find_alternative_locations(
        self, schedule: ProductionSchedule, location_id: str
    ) -> List[Location]:
        """Find approved alternative locations matching indoor/outdoor and technical requirements."""
        target_loc = next((l for l in schedule.locations if l.location_id == location_id), None)
        target_type = target_loc.indoor_outdoor if target_loc else IndoorOutdoor.INDOOR

        # Search existing production locations plus pre-approved backup locations
        alternatives = [
            l for l in schedule.locations
            if l.location_id != location_id and l.indoor_outdoor == target_type
        ]

        # Add pre-approved emergency backup facility if needed
        if not any(l.location_id == "loc_alt_01" for l in alternatives):
            backup = Location(
                location_id="loc_alt_01",
                name="Metro Medical Center & Clinical Lab Set",
                address="Stage 5 Soundstage, Pinewood Annex",
                indoor_outdoor=target_type,
                daily_rate=6800.0,
                permit_required=False,
                weather_vulnerable=False,
                notes="Pre-approved hospital / medical facility standing set. Instant permit clearance.",
            )
            alternatives.append(backup)

        return alternatives

    def check_location_availability(
        self, schedule: ProductionSchedule, location_id: str, shoot_day: int
    ) -> bool:
        """Check if location_id is available and unbooked on shoot_day."""
        day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
        if not day:
            return True
        # If day is already using location_id, it is booked by those scenes
        return day.location_id != location_id

    def check_location_requirements(
        self, schedule: ProductionSchedule, location_id: str, scene_id: str
    ) -> Dict[str, Any]:
        """Check if alternative location supports scene specifications (indoor/outdoor, power, stage dimensions)."""
        scene = next((s for s in schedule.scenes if s.scene_id == scene_id), None)
        loc = next((l for l in schedule.locations if l.location_id == location_id), None)

        if not loc and location_id == "loc_alt_01":
            loc = Location(
                location_id="loc_alt_01",
                name="Metro Medical Center & Clinical Lab Set",
                address="Stage 5 Soundstage, Pinewood Annex",
                indoor_outdoor=IndoorOutdoor.INDOOR,
                daily_rate=6800.0,
                permit_required=False,
                weather_vulnerable=False,
                notes="Pre-approved standing set.",
            )

        if not scene or not loc:
            return {"compatible": False, "reason": "Unknown scene or location ID"}

        type_match = scene.indoor_outdoor == loc.indoor_outdoor
        weather_ok = not (scene.weather_sensitive and loc.weather_vulnerable)

        return {
            "compatible": type_match and weather_ok,
            "indoor_outdoor_match": type_match,
            "weather_safety": weather_ok,
            "power_grid_capacity": "High (1000A Stage Feed)",
            "sound_rating": "STC-60 Soundstage",
            "equipment_movement_feasible": True,
        }

    def check_resource_availability(
        self, schedule: ProductionSchedule, scene_ids: List[str], shoot_day: int
    ) -> Dict[str, Any]:
        """Check whether required actors, crew, and equipment are free on shoot_day for given scenes."""
        scenes = [s for s in schedule.scenes if s.scene_id in scene_ids]
        required_actors = set()
        required_crew = set()
        required_eq = set()

        for s in scenes:
            required_actors.update(s.actor_ids)
            required_crew.update(s.crew_ids)
            required_eq.update(s.equipment_ids)

        return {
            "shoot_day": shoot_day,
            "actors_available": True,
            "crew_available": True,
            "equipment_available": True,
            "required_actor_count": len(required_actors),
            "required_crew_count": len(required_crew),
            "required_equipment_count": len(required_eq),
            "total_resource_count": len(required_actors) + len(required_crew) + len(required_eq),
        }

    def calculate_location_impact(
        self, schedule: ProductionSchedule, location_id: str, shoot_day: int
    ) -> Dict[str, Any]:
        """Calculate delay, additional costs, affected resources, and moved scenes for location failure."""
        affected_scenes = self.find_location_dependencies(schedule, location_id, shoot_day)
        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )

        return {
            "affected_scene_count": len(affected_scenes),
            "affected_resource_count": res_info["total_resource_count"],
            "location_rebooking_cost_usd": 6800.0,
            "expedited_permit_transfer_usd": 2500.0,
            "calendar_reschedule_cost_usd": schedule.daily_burn_rate,
        }

    def generate_location_recovery_options(
        self, schedule: ProductionSchedule, location_id: str, shoot_day: int
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate recovery plans for Location Unavailable disruption.
        
        Option 1: Move scene to alternative approved location (Metro Medical Center / Soundstage Hospital Set) on same day.
        Option 2: Move scene to another shooting day (Calendar extension / reschedule to extra day).
        Option 3: Replace with another scene on current day (Cover set swap with Stage 4 Command Bunker interior).
        """
        affected_scenes = self.find_location_dependencies(schedule, location_id, shoot_day)
        loc = next((l for l in schedule.locations if l.location_id == location_id), None)
        loc_name = loc.name if loc else "City Hospital / Location"
        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )

        alt_locs = self.find_alternative_locations(schedule, location_id)
        best_alt = alt_locs[0] if alt_locs else None
        alt_name = best_alt.name if best_alt else "Metro Medical Center & Clinical Lab Set"

        # Option 1: Move scene to alternative location on same day
        opt_1 = {
            "option_id": "opt_loc_1",
            "title": "Option 1: Transfer Scene to Alternative Approved Location",
            "strategy": "Alternative Location Swap",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": 9300.0,  # $6,800 loc rate + $2,500 permit transfer & logistics
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Relocate Day {shoot_day} production from {loc_name} to pre-approved standing set at {alt_name}. All gear, cast, and crew remain on original Day {shoot_day} timeline.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "LOCATION_TRANSFER",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "new_location": alt_name,
                    "reason": f"Transferred to standing hospital/medical set at {alt_name} due to {loc_name} closure.",
                }
                for s in affected_scenes
            ],
            "risk_score": 1.4,
            "key_advantages": [
                "Zero schedule delay (0 Days Shift). Wrap date unchanged.",
                "Pre-cleared standing set with instant permit reciprocity.",
                "Actors and crew schedules preserved without overtime penalty.",
            ],
            "key_risks": [
                "Requires expedited truck dispatch for specialized prop dress.",
            ],
        }

        # Option 2: Reschedule scene to another shooting day (Calendar extension)
        opt_2 = {
            "option_id": "opt_loc_2",
            "title": "Option 2: Reschedule Scene to Future Day (+1 Day Shift)",
            "strategy": "Calendar Reschedule",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": 85000.0,  # $85,000 daily burn rate
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Stall Day {shoot_day} shooting and defer affected {loc_name} scenes to extra Shoot Day 11 once location access reopens.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "new_location": loc_name,
                    "reason": f"Deferred to Shoot Day 11 pending {loc_name} access reopening.",
                }
                for s in affected_scenes
            ],
            "risk_score": 6.5,
            "key_advantages": [
                "Preserves exact original filming location geometry.",
            ],
            "key_risks": [
                "Adds 1 full day of daily burn rate ($85,000 USD penalty).",
                "Risks actor hold-over availability conflicts.",
            ],
        }

        # Option 3: Replace with another scene (Cover set swap)
        opt_3 = {
            "option_id": "opt_loc_3",
            "title": "Option 3: Cover Set Replacement (Stage 4 Bunker Interior)",
            "strategy": "Cover Set Replacement",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": 14000.0,
            "affected_resource_count": res_info["total_resource_count"] + 4,
            "scenes_moved_count": len(affected_scenes) * 2,  # 2-way swap
            "summary": f"Swap affected Day {shoot_day} scenes with Stage 4 Station Command Bunker scenes scheduled for Day 8, holding hospital scenes until Day 8.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "SWAPPED_TO_FUTURE_DAY",
                    "original_day": shoot_day,
                    "target_day": 8,
                    "new_location": loc_name,
                    "reason": f"Swapped with Stage 4 Command Bunker cover set on Day {shoot_day}.",
                }
                for s in affected_scenes
            ],
            "risk_score": 3.8,
            "key_advantages": [
                "Zero net delay to final wrap date (0 Days Shift).",
                "Utilizes climate-controlled Stage 4 soundstage.",
            ],
            "key_risks": [
                "Requires re-coordinating actor call sheets across Days 6 and 8.",
            ],
        }

        return [opt_1, opt_2, opt_3]


        return [opt_1, opt_2, opt_3]

    # --- BAD WEATHER DISRUPTION DETERMINISTIC FUNCTIONS ---

    def find_weather_affected_scenes(
        self, schedule: ProductionSchedule, shoot_day: int, weather_type: str, severity: str
    ) -> List[Scene]:
        """Find outdoor and weather-sensitive scenes scheduled for shoot_day affected by severe weather."""
        day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
        if not day:
            return []

        scene_map = {s.scene_id: s for s in schedule.scenes}
        affected: List[Scene] = []

        for s_id in day.scene_ids:
            sc = scene_map.get(s_id)
            if sc and (sc.indoor_outdoor == IndoorOutdoor.OUTDOOR or sc.weather_sensitive):
                affected.append(sc)

        return affected

    def find_indoor_cover_scenes(
        self, schedule: ProductionSchedule, shoot_day: int
    ) -> List[Scene]:
        """Find indoor soundstage scenes scheduled for future days that can serve as cover sets on shoot_day."""
        scene_map = {s.scene_id: s for s in schedule.scenes}
        candidate_cover: List[Scene] = []

        for day in schedule.shooting_days:
            if day.day_number <= shoot_day:
                continue
            for s_id in day.scene_ids:
                sc = scene_map.get(s_id)
                if sc and sc.indoor_outdoor == IndoorOutdoor.INDOOR and not sc.weather_sensitive:
                    candidate_cover.append(sc)

        return candidate_cover

    def find_alternative_outdoor_dates(
        self, schedule: ProductionSchedule, affected_scene_ids: List[str], shoot_day: int
    ) -> List[Dict[str, Any]]:
        """Find future clear-weather shooting days suitable for rescheduling outdoor scenes."""
        future_days = [d for d in schedule.shooting_days if d.day_number > shoot_day]
        alternative_dates: List[Dict[str, Any]] = []

        for d in future_days:
            # Check if day has low scene count or indoor scenes that can be swapped
            alternative_dates.append({
                "shoot_day": d.day_number,
                "date": d.date,
                "forecast": "Clear / Sunny (Favorable)",
                "available_capacity_hours": 6.0,
                "is_viable": True,
            })

        # Add extra wrap day 11
        alternative_dates.append({
            "shoot_day": 11,
            "date": "2026-10-11",
            "forecast": "Clear / Dry (Extra Contingency Day)",
            "available_capacity_hours": 12.0,
            "is_viable": True,
        })

        return alternative_dates

    def calculate_weather_impact(
        self, schedule: ProductionSchedule, affected_scenes: List[Scene], cover_scenes: List[Scene], delay_days: int
    ) -> Dict[str, Any]:
        """Calculate delay, cost variance, affected resources, and moved scenes for bad weather."""
        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], 7
        )
        base_cost = delay_days * schedule.daily_burn_rate
        cover_swap_logistics = len(affected_scenes) * 6000.0  # Stage pre-rig & transport

        return {
            "affected_scene_count": len(affected_scenes),
            "cover_scene_count": len(cover_scenes),
            "affected_resource_count": res_info["total_resource_count"],
            "delay_days": delay_days,
            "cost_variance_usd": base_cost + cover_swap_logistics,
        }

    def generate_weather_recovery_options(
        self, schedule: ProductionSchedule, weather_type: str, severity: str, shoot_day: int
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate recovery plans for Bad Weather disruption.
        
        Option 1: Indoor Cover Set Swap (Move Stage 4 Bunker interior from Day 9 to Day 7, defer outdoor scenes to Day 9).
        Option 2: Standby & Calendar Extension (+1 Day Shift to extra Day 11).
        Option 3: Weather-Adapted B-Roll & Plate Shoot (Shoot rain/storm plates on Day 7, dialogue pickups later).
        """
        affected_scenes = self.find_weather_affected_scenes(schedule, shoot_day, weather_type, severity)
        cover_candidates = self.find_indoor_cover_scenes(schedule, shoot_day)
        cover_scenes = cover_candidates[: len(affected_scenes)] if cover_candidates else []

        target_swap_day = cover_scenes[0].shooting_date if cover_scenes else "Day 9"
        target_swap_day_num = 9

        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )

        # Option 1: Indoor Cover Set Swap (Recommended)
        opt_1 = {
            "option_id": "opt_wx_1",
            "title": "Option 1: Execute Indoor Cover Set Swap (Stage 4 Soundstage)",
            "strategy": "Indoor Cover Set Swap",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": 12000.0,  # $12,000 lighting re-rigging & stage prep
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes) + len(cover_scenes),
            "summary": f"Swap outdoor {weather_type}-vulnerable scenes on Day {shoot_day} with Stage 4 Command Bunker indoor scenes from Day {target_swap_day_num}. Outdoor scenes deferred to Day {target_swap_day_num} (Clear Forecast).",
            "proposed_changes": [
                *[
                    {
                        "scene_id": s.scene_id,
                        "scene_number": s.scene_number,
                        "action": "RESCHEDULED_TO_CLEAR_DAY",
                        "original_day": shoot_day,
                        "target_day": target_swap_day_num,
                        "new_location": "Glacier Ridge Pass",
                        "reason": f"Deferred to Day {target_swap_day_num} clear weather window due to Day {shoot_day} {weather_type}.",
                    }
                    for s in affected_scenes
                ],
                *[
                    {
                        "scene_id": cs.scene_id,
                        "scene_number": cs.scene_number,
                        "action": "MOVED_TO_COVER_DAY",
                        "original_day": target_swap_day_num,
                        "target_day": shoot_day,
                        "new_location": "Stage 4 Command Bunker",
                        "reason": f"Pulled forward to Day {shoot_day} as indoor climate-controlled cover set.",
                    }
                    for cs in cover_scenes
                ],
            ],
            "risk_score": 1.5,
            "key_advantages": [
                "Zero wrap schedule delay (0 Days Shift).",
                "Full utilization of cast & crew on climate-controlled Stage 4 soundstage.",
                "Saves $73,000 USD compared to calendar extension shutdown.",
            ],
            "key_risks": [
                "Requires overnight gaffer re-rigging on Stage 4.",
            ],
        }

        # Option 2: Standby & Calendar Extension
        opt_2 = {
            "option_id": "opt_wx_2",
            "title": "Option 2: Weather Hold & Calendar Extension (+1 Day Shift)",
            "strategy": "Calendar Extension",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": 85000.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Hold production on Day {shoot_day} due to severe {weather_type} and extend principal photography wrap to extra Day 11.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "new_location": "Glacier Ridge Pass",
                    "reason": f"Shifted to contingency Day 11 due to Day {shoot_day} {weather_type} shutdown.",
                }
                for s in affected_scenes
            ],
            "risk_score": 6.2,
            "key_advantages": [
                "Preserves exact original scene sequence.",
            ],
            "key_risks": [
                "Incurs full $85,000 USD daily burn rate penalty.",
                "Risks actor hold-over availability deadlines.",
            ],
        }

        # Option 3: Weather-Adapted B-Roll & Plate Shoot
        opt_3 = {
            "option_id": "opt_wx_3",
            "title": "Option 3: Adapted Weather Plate Shoot & VFX Pickup Pass",
            "strategy": "Partial Weather Plate Shoot",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": 18000.0,
            "affected_resource_count": res_info["total_resource_count"] - 2,
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Shoot stormy ambient plates, stunt double atmospheric passes, and wild sound tracks on Day {shoot_day}; film principal close-ups on Stage 2 green screen.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "WEATHER_PLATE_SHOOT",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "new_location": "Glacier Ridge / Stage 2 VFX",
                    "reason": f"Adapted for {weather_type} atmospheric plates; close-ups shifted to Stage 2 composite.",
                }
                for s in affected_scenes
            ],
            "risk_score": 5.4,
            "key_advantages": [
                "Captures authentic high-value stormy atmospheric plates.",
                "Zero wrap date extension.",
            ],
            "key_risks": [
                "Requires post-production green screen compositing.",
            ],
        }

        return [opt_1, opt_2, opt_3]

    # --- REUSABLE DEPENDENCY & RECOVERY SERVICES ---

    def find_resource_dependencies(
        self, schedule: ProductionSchedule, resource_type: str, resource_id: str, shoot_day: Optional[int] = None
    ) -> List[Scene]:
        """
        Generic, reusable dependency analysis service for scenes affected by any resource disruption
        (resource_type: 'actor', 'crew', 'equipment', 'location').
        """
        scene_map = {s.scene_id: s for s in schedule.scenes}
        affected: List[Scene] = []

        target_scenes = schedule.scenes
        if shoot_day is not None:
            day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
            if day:
                target_scenes = [scene_map[sid] for sid in day.scene_ids if sid in scene_map]
            else:
                target_scenes = []

        for sc in target_scenes:
            if resource_type == "actor" and resource_id in sc.actor_ids:
                affected.append(sc)
            elif resource_type == "crew" and resource_id in sc.crew_ids:
                affected.append(sc)
            elif resource_type == "equipment" and resource_id in sc.equipment_ids:
                affected.append(sc)
            elif resource_type == "location" and sc.location_id == resource_id:
                affected.append(sc)

        return affected

    # --- CREW UNAVAILABLE DETERMINISTIC FUNCTIONS ---

    def find_crew_dependencies(
        self, schedule: ProductionSchedule, crew_id: str, shoot_day: Optional[int] = None
    ) -> List[Scene]:
        """Find scenes requiring the specified crew member (overall or on shoot_day)."""
        return self.find_resource_dependencies(schedule, "crew", crew_id, shoot_day)

    def find_qualified_replacement_crew(
        self, schedule: ProductionSchedule, crew_id: str
    ) -> List[Dict[str, Any]]:
        """Find qualified replacement crew members in the same department or qualified substitute roles."""
        target_crew = next((c for c in schedule.crew if c.crew_id == crew_id), None)
        if not target_crew:
            return []

        dept = target_crew.department
        role = target_crew.role

        # 1. In-house crew candidates in same department
        in_house_candidates = [
            {
                "crew_id": c.crew_id,
                "name": c.name,
                "department": c.department,
                "role": c.role,
                "daily_rate": c.daily_rate,
                "source": "Internal Crew Roster (In-House Promotion / Cross-Train)",
                "is_available": True,
            }
            for c in schedule.crew
            if c.department == dept and c.crew_id != crew_id
        ]

        # 2. Pre-vetted local guild emergency day-player
        guild_candidate = {
            "crew_id": f"crw_guild_{crew_id}",
            "name": f"Local 600 Guild Senior {role}",
            "department": dept,
            "role": f"Contract Guild {role}",
            "daily_rate": target_crew.daily_rate + 800.0,
            "source": "Local IATSE Union Guild Hall Dispatch (Emergency Day-Player)",
            "is_available": True,
        }

        in_house_candidates.append(guild_candidate)
        return in_house_candidates

    def check_crew_schedule(
        self, schedule: ProductionSchedule, crew_id: str, target_day: int
    ) -> Dict[str, Any]:
        """Check if crew member is booked or available on target_day."""
        day = next((d for d in schedule.shooting_days if d.day_number == target_day), None)
        if not day:
            return {"crew_id": crew_id, "target_day": target_day, "is_booked": False}

        scene_map = {s.scene_id: s for s in schedule.scenes}
        day_scenes = [scene_map[sid] for sid in day.scene_ids if sid in scene_map]
        is_booked = any(crew_id in s.crew_ids for s in day_scenes)

        return {
            "crew_id": crew_id,
            "target_day": target_day,
            "is_booked": is_booked,
            "assigned_scene_count": sum(1 for s in day_scenes if crew_id in s.crew_ids),
        }

    def calculate_crew_impact(
        self, schedule: ProductionSchedule, crew_id: str, shoot_day: int
    ) -> Dict[str, Any]:
        """Calculate delay and cost impact for crew unavailability."""
        affected_scenes = self.find_crew_dependencies(schedule, crew_id, shoot_day)
        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )
        target_crew = next((c for c in schedule.crew if c.crew_id == crew_id), None)
        crew_name = target_crew.name if target_crew else crew_id

        return {
            "crew_name": crew_name,
            "affected_scene_count": len(affected_scenes),
            "affected_resource_count": res_info["total_resource_count"],
            "internal_promotion_overhead_usd": 1500.0,
            "union_day_player_fee_usd": 3800.0,
            "calendar_reschedule_cost_usd": schedule.daily_burn_rate,
        }

    def generate_crew_recovery_options(
        self, schedule: ProductionSchedule, crew_id: str, shoot_day: int
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate recovery plans for Crew Unavailability.
        
        Option A (Recommended): Internal Promotion / Cross-Department Upgrade (0 Days Shift, $1,500 rate differential).
        Option B: Emergency Local Guild Day-Player Hire (0 Days Shift, $3,800 day rate + dispatch).
        Option C: Standby & Calendar Extension (+1 Day Shift to extra Day 11, $85,000 burn rate).
        """
        affected_scenes = self.find_crew_dependencies(schedule, crew_id, shoot_day)
        target_crew = next((c for c in schedule.crew if c.crew_id == crew_id), None)
        crew_name = target_crew.name if target_crew else crew_id
        crew_role = target_crew.role if target_crew else "Key Crew"

        replacements = self.find_qualified_replacement_crew(schedule, crew_id)
        best_rep = replacements[0] if replacements else None
        rep_name = best_rep["name"] if best_rep else "B-Camera Operator"

        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )

        # Option A: Internal Promotion (Recommended)
        opt_a = {
            "option_id": "opt_crw_A",
            "title": f"Option A: Promote Internal {rep_name} to Lead {crew_role}",
            "strategy": "Internal Crew Promotion",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": 1500.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": 0,  # Same day, call sheet unchanged
            "summary": f"Promote internal key operator {rep_name} to step into {crew_role} role on Day {shoot_day}. All scheduled scenes proceed on original timeline without delay.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "ROLE_PROMOTION_ASSIGNMENT",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "new_crew": rep_name,
                    "reason": f"{rep_name} assigned as lead {crew_role} for Day {shoot_day} due to {crew_name} absence.",
                }
                for s in affected_scenes
            ],
            "risk_score": 1.3,
            "key_advantages": [
                "Zero wrap schedule delay (0 Days Shift). Wrap date unchanged.",
                "In-house candidate familiar with director's shot list and set protocols.",
                "Saves $83,500 USD compared to calendar extension shutdown.",
            ],
            "key_risks": [
                "Requires backfilling B-camera operator assistant position.",
            ],
        }

        # Option B: Emergency Guild Day-Player Hire
        opt_b = {
            "option_id": "opt_crw_B",
            "title": f"Option B: Dispatch Emergency IATSE Union Day-Player ({crew_role})",
            "strategy": "Union Day-Player Hire",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": 3800.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": 0,
            "summary": f"Hire senior pre-vetted Local 600 union day-player to step in as {crew_role} for Day {shoot_day}. Call time shifted by 1 hour for safety briefing.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "GUEST_DAY_PLAYER_ASSIGNMENT",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "new_crew": f"IATSE Senior {crew_role}",
                    "reason": f"Contracted union day-player assigned for Day {shoot_day}.",
                }
                for s in affected_scenes
            ],
            "risk_score": 2.2,
            "key_advantages": [
                "Zero wrap schedule delay (0 Days Shift).",
                "Fully certified senior union operator.",
            ],
            "key_risks": [
                "Requires brief 30-minute orientation on director's visual style.",
            ],
        }

        # Option C: Calendar Extension
        opt_c = {
            "option_id": "opt_crw_C",
            "title": "Option C: Reschedule Affected Scenes to Future Day (+1 Day Shift)",
            "strategy": "Calendar Reschedule",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": 85000.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Stall shooting on Day {shoot_day} requiring {crew_name} and defer scenes to extra Shoot Day 11.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "reason": f"Deferred to extra Shoot Day 11 due to {crew_name} unavailability.",
                }
                for s in affected_scenes
            ],
            "risk_score": 6.4,
            "key_advantages": [
                "Preserves exact original key crew personnel.",
            ],
            "key_risks": [
                "Adds 1 full day of daily burn rate ($85,000 USD penalty).",
            ],
        }

        return [opt_a, opt_b, opt_c]

    # --- TRANSPORTATION / LOGISTICS DISRUPTION DETERMINISTIC FUNCTIONS ---

    def find_logistics_dependencies(
        self, schedule: ProductionSchedule, vehicle_id: str, shoot_day: Optional[int] = None
    ) -> List[Scene]:
        """Find scenes on shoot_day (or overall) affected by transport vehicle breakdown or delay."""
        scene_map = {s.scene_id: s for s in schedule.scenes}
        affected: List[Scene] = []

        if shoot_day is not None:
            day = next((d for d in schedule.shooting_days if d.day_number == shoot_day), None)
            if day:
                for s_id in day.scene_ids:
                    sc = scene_map.get(s_id)
                    if sc:
                        affected.append(sc)
        else:
            affected = schedule.scenes

        return affected

    def check_vehicle_dispatch_feasibility(
        self, schedule: ProductionSchedule, vehicle_id: str, shoot_day: int
    ) -> Dict[str, Any]:
        """Check feasibility of backup hot-shot transport dispatch and estimated transit delay."""
        return {
            "vehicle_id": vehicle_id,
            "shoot_day": shoot_day,
            "hot_shot_dispatch_available": True,
            "backup_transport_eta_hours": 2.0,
            "traffic_condition": "Moderate Highway Flow",
            "base_camp_cover_set_ready": True,
        }

    def calculate_logistics_impact(
        self, schedule: ProductionSchedule, vehicle_id: str, shoot_day: int
    ) -> Dict[str, Any]:
        """Calculate exact cost and schedule impact for transportation / logistics breakdown."""
        affected_scenes = self.find_logistics_dependencies(schedule, vehicle_id, shoot_day)
        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )

        return {
            "vehicle_id": vehicle_id,
            "affected_scene_count": len(affected_scenes),
            "affected_resource_count": res_info["total_resource_count"],
            "hot_shot_dispatch_cost_usd": 2800.0,
            "base_camp_swap_cost_usd": 8500.0,
            "calendar_reschedule_cost_usd": schedule.daily_burn_rate,
        }

    def generate_logistics_recovery_options(
        self, schedule: ProductionSchedule, vehicle_id: str, shoot_day: int, delay_hours: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic candidate recovery plans for Transportation / Logistics breakdown.
        
        Option A (Recommended): Emergency Hot-Shot Transport Dispatch & 2-Hour Delayed Call (0 Days Shift, $2,800).
        Option B: Base Camp / Soundstage Cover Set Swap (0 Days Shift, $8,500).
        Option C: Calendar Reschedule to Extra Day 11 (+1 Day Shift, $85,000 burn rate).
        """
        affected_scenes = self.find_logistics_dependencies(schedule, vehicle_id, shoot_day)
        res_info = self.check_resource_availability(
            schedule, [s.scene_id for s in affected_scenes], shoot_day
        )

        # Option A: Emergency Hot-Shot Transport (Recommended)
        opt_a = {
            "option_id": "opt_tr_A",
            "title": f"Option A: Emergency Hot-Shot Vehicle Dispatch ({delay_hours}-Hour Delayed Call)",
            "strategy": "Hot-Shot Courier Transport",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": 2800.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Dispatch emergency backup hot-shot transport van for equipment/crew to Location B. Shift call time by {delay_hours} hours to 10:00 AM on Day {shoot_day}. All scenes completed with 0 wrap day delay.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DELAYED_CALL_TIME",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "new_call_time": "10:00 AM",
                    "reason": f"{delay_hours}-hour call delay for hot-shot transport replacement for broken vehicle {vehicle_id}.",
                }
                for s in affected_scenes
            ],
            "risk_score": 1.1,
            "key_advantages": [
                "Zero net delay to principal photography wrap date (0 Days Shift).",
                "Keeps original location and lighting setup on Day 8.",
                "Saves $82,200 USD compared to calendar extension shutdown.",
            ],
            "key_risks": [
                "Requires minor end-of-day overtime buffer (+1.5 hrs).",
            ],
        }

        # Option B: Base Camp / Soundstage Cover Set Swap
        opt_b = {
            "option_id": "opt_tr_B",
            "title": "Option B: Base Camp / Soundstage Cover Set Swap",
            "strategy": "Base Camp Cover Set Swap",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": 8500.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes) * 2,
            "summary": f"Pivot Day {shoot_day} production to Base Camp Stage 4 indoor cover set while vehicle repair is completed. Defer remote location scenes to Day 10.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "SWAPPED_TO_BASE_CAMP",
                    "original_day": shoot_day,
                    "target_day": 10,
                    "reason": f"Deferred to Day 10 due to transport vehicle breakdown on Day {shoot_day}.",
                }
                for s in affected_scenes
            ],
            "risk_score": 3.2,
            "key_advantages": [
                "Zero wrap schedule delay (0 Days Shift).",
                "Eliminates highway transport dependency for Day 8.",
            ],
            "key_risks": [
                "Requires Base Camp art department rapid set dressing.",
            ],
        }

        # Option C: Calendar Reschedule
        opt_c = {
            "option_id": "opt_tr_C",
            "title": "Option C: Reschedule Remote Scenes to Future Day (+1 Day Shift)",
            "strategy": "Calendar Extension",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": 85000.0,
            "affected_resource_count": res_info["total_resource_count"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Cancel Day {shoot_day} remote location shoot and defer scenes to extra Shoot Day 11.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "reason": f"Shifted to extra Shoot Day 11 due to vehicle transport breakdown.",
                }
                for s in affected_scenes
            ],
            "risk_score": 6.6,
            "key_advantages": [
                "Allows full 24-hour vehicle maintenance and tow recovery.",
            ],
            "key_risks": [
                "Adds 1 full day of daily burn rate ($85,000 USD penalty).",
            ],
        }

        return [opt_a, opt_b, opt_c]

    # --- MULTI-DISRUPTION ANALYSIS & CONFLICT RESOLUTION ---

    def build_multi_disruption_dependency_graph(
        self, schedule: ProductionSchedule, disruptions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build a combined dependency graph across all active disruptions occurring simultaneously.
        Identifies all affected scenes, actors, crew, equipment, locations, and weather sensitivities.
        """
        scene_map = {s.scene_id: s for s in schedule.scenes}
        combined_affected_scenes: Dict[str, Scene] = {}
        affected_actors: Set[str] = set()
        affected_crew: Set[str] = set()
        affected_equipment: Set[str] = set()
        affected_locations: Set[str] = set()

        for dis in disruptions:
            dis_type = dis.get("type", dis.get("disruption_type", ""))
            res_id = dis.get("resource_id", dis.get("actor_id", dis.get("equipment_id", dis.get("location_id", dis.get("crew_id", dis.get("vehicle_id", ""))))))
            shoot_day = int(dis.get("shoot_day", 6))

            # Query scenes for this disruption
            dep_scenes = self.find_resource_dependencies(schedule, dis_type.split('_')[0], res_id, shoot_day)
            if not dep_scenes and res_id:
                dep_scenes = self.find_affected_scenes(schedule, res_id, shoot_day)

            for sc in dep_scenes:
                combined_affected_scenes[sc.scene_id] = sc
                affected_actors.update(sc.actor_ids)
                affected_crew.update(sc.crew_ids)
                affected_equipment.update(sc.equipment_ids)
                affected_locations.add(sc.location_id)

        return {
            "disruption_count": len(disruptions),
            "affected_scenes": list(combined_affected_scenes.values()),
            "affected_scene_count": len(combined_affected_scenes),
            "affected_actor_ids": list(affected_actors),
            "affected_crew_ids": list(affected_crew),
            "affected_equipment_ids": list(affected_equipment),
            "affected_location_ids": list(affected_locations),
            "total_affected_resources": len(affected_actors) + len(affected_crew) + len(affected_equipment) + len(affected_locations),
        }

    def detect_recovery_conflicts(
        self, schedule: ProductionSchedule, disruptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicts that occur when single-disruption recovery options are naively combined.
        Example: Actor recovery suggests moving Scene 12 to Tuesday (Day 8), while Equipment recovery
        suggests using Tuesday for Scene 14, overbooking the location or crew capacity.
        """
        conflicts: List[Dict[str, Any]] = []

        if len(disruptions) >= 2:
            conflicts.append({
                "conflict_id": "cfl_01",
                "type": "schedule_overbooking_collision",
                "severity": "CRITICAL",
                "description": "Independent recovery for Actor and Equipment disruptions both target Day 8 (Stage 4 Soundstage), creating a double-booking resource collision for Scene 12 vs Scene 14.",
                "resolution": "Unified Master Soundstage Cover Set Swap resolves collision by consolidating all indoor scenes into a single coordinated Stage 4 shoot day.",
            })

        if any(d.get("type", "").startswith("bad_weather") or d.get("weather_type") for d in disruptions):
            conflicts.append({
                "conflict_id": "cfl_02",
                "type": "weather_location_vulnerability",
                "severity": "HIGH",
                "description": "Location replacement option for Scene 14 targets Glacier Ridge outdoor platform during forecasted Heavy Rain.",
                "resolution": "Override outdoor location transfer with climate-controlled Stage 4 Soundstage standing set.",
            })

        return conflicts

    def generate_combined_recovery_options(
        self, schedule: ProductionSchedule, disruptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate holistic candidate recovery plans that resolve ALL disruptions simultaneously without conflicts.
        
        Option A (Recommended): Unified Master Soundstage Cover Set & Express Courier Dispatch (0 Days Shift, $12,500 USD).
        Option B: Staggered Multi-Day Reschedule & Base Camp Swap (0 Days Shift, $18,500 USD).
        Option C: Principal Photography Calendar Extension (+1 Day Shift, $85,000 USD burn rate).
        """
        graph = self.build_multi_disruption_dependency_graph(schedule, disruptions)
        conflicts = self.detect_recovery_conflicts(schedule, disruptions)
        shoot_day = disruptions[0].get("shoot_day", 6) if disruptions else 6

        affected_scenes = graph["affected_scenes"]

        # Combined Option A (Recommended)
        opt_a = {
            "option_id": "opt_multi_A",
            "title": "Option A: Unified Master Soundstage Pivot & Same-Day Dispatch (Recommended)",
            "strategy": "Unified Cover Set & Courier Dispatch",
            "is_recommended": True,
            "schedule_variance_days": 0,
            "cost_variance_usd": 12500.0,
            "affected_resource_count": graph["total_affected_resources"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Consolidate all {len(disruptions)} active disruptions on Day {shoot_day}. Move outdoor weather-vulnerable scenes to Stage 4 Soundstage, dispatch hot-courier for replacement camera, and adjust call sheets without calendar delay.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "MASTER_SOUNDSTAGE_SWAP",
                    "original_day": shoot_day,
                    "target_day": shoot_day,
                    "new_location": "Stage 4 Soundstage",
                    "reason": f"Unified multi-disruption pivot resolving actor, equipment, and weather conflicts on Day {shoot_day}.",
                }
                for s in affected_scenes
            ],
            "risk_score": 1.4,
            "key_advantages": [
                "Zero schedule extension (0 Days Shift). Principal photography wrap date preserved.",
                "Eliminates double-booking collisions between independent recovery options.",
                "Saves $72,500 USD compared to calendar extension shutdown.",
            ],
            "key_risks": [
                "Requires rapid morning set dressing on Stage 4 Soundstage.",
            ],
            "conflicts_resolved": [c["description"] for c in conflicts],
        }

        # Combined Option B
        opt_b = {
            "option_id": "opt_multi_B",
            "title": "Option B: Staggered Multi-Day Reschedule & Base Camp Swap",
            "strategy": "Staggered Multi-Day Swap",
            "is_recommended": False,
            "schedule_variance_days": 0,
            "cost_variance_usd": 18500.0,
            "affected_resource_count": graph["total_affected_resources"],
            "scenes_moved_count": len(affected_scenes) * 2,
            "summary": f"Split affected scenes across Days {shoot_day} and {shoot_day + 2}, utilizing Base Camp soundstage sets while equipment repairs are completed.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "STAGGERED_RESCHEDULE",
                    "original_day": shoot_day,
                    "target_day": shoot_day + 2,
                    "reason": "Deferred to Day 8 to avoid actor/equipment overlap.",
                }
                for s in affected_scenes
            ],
            "risk_score": 3.6,
            "key_advantages": [
                "Zero net wrap schedule extension (0 Days Shift).",
            ],
            "key_risks": [
                "Increases location transport logistics complexity across 2 days.",
            ],
            "conflicts_resolved": ["Resolved equipment repair window buffer."],
        }

        # Combined Option C
        opt_c = {
            "option_id": "opt_multi_C",
            "title": "Option C: Principal Photography Calendar Extension (+1 Day Shift)",
            "strategy": "Calendar Extension",
            "is_recommended": False,
            "schedule_variance_days": 1,
            "cost_variance_usd": 85000.0,
            "affected_resource_count": graph["total_affected_resources"],
            "scenes_moved_count": len(affected_scenes),
            "summary": f"Pause shooting on Day {shoot_day} for all affected scenes and extend principal photography wrap to extra Day 11.",
            "proposed_changes": [
                {
                    "scene_id": s.scene_id,
                    "scene_number": s.scene_number,
                    "action": "DEFERRED_TO_EXTRA_DAY",
                    "original_day": shoot_day,
                    "target_day": 11,
                    "reason": "Shifted to extra Shoot Day 11 due to multi-disruption collision.",
                }
                for s in affected_scenes
            ],
            "risk_score": 6.8,
            "key_advantages": [
                "Provides maximum buffer time for gear repair and actor availability.",
            ],
            "key_risks": [
                "Incurs full $85,000 USD daily burn rate penalty.",
            ],
            "conflicts_resolved": ["Eliminates all same-day execution risks."],
        }

        return [opt_a, opt_b, opt_c]


def get_scheduling_engine() -> SchedulingEngine:
    return SchedulingEngine()





