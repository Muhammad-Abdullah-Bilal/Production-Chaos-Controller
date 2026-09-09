import logging
from typing import Dict, List, Optional
from app.models.schedule import (
    Actor,
    CrewMember,
    Equipment,
    IndoorOutdoor,
    Location,
    PriorityLevel,
    ProductionSchedule,
    Scene,
    SceneStatus,
    ShootingDay,
)
from app.models.disruption import DisruptionEvent
from app.models.recovery import RecoveryPlan

logger = logging.getLogger(__name__)


class InMemoryDatabase:
    """
    In-memory state repository for 'The Last Signal' production dataset.
    Exposes full relational integrity across scenes, cast, crew, locations, and equipment.
    """

    def __init__(self):
        self.schedules: Dict[str, ProductionSchedule] = {}
        self.disruptions: Dict[str, DisruptionEvent] = {}
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        self._seed_initial_data()

    def _seed_initial_data(self):
        """Seed 'The Last Signal' 20-scene sci-fi production dataset."""
        actors = [
            Actor(actor_id="act_01", name="Dr. Sarah Mercer", character_name="Dr. Sarah Mercer (Lead Astronomer)", is_lead=True, daily_rate=14000.0, contact_info="sarah.mercer@agency.com"),
            Actor(actor_id="act_02", name="Commander Ethan Vance", character_name="Commander Vance (Expedition Officer)", is_lead=True, daily_rate=12500.0, contact_info="vance.rep@hollywood.com"),
            Actor(actor_id="act_03", name="Dr. Aris Thorne", character_name="Dr. Aris Thorne (Quantum Physicist)", is_lead=False, daily_rate=8500.0, contact_info="thorne@castmgt.com"),
            Actor(actor_id="act_04", name="Maya Lin", character_name="Maya Lin (Communications Tech)", is_lead=False, daily_rate=7000.0, contact_info="maya.lin@talent.com"),
            Actor(actor_id="act_05", name="General Arthur Pendelton", character_name="General Pendelton (High Command)", is_lead=False, daily_rate=9500.0, contact_info="general.p@talent.com"),
            Actor(actor_id="act_06", name="Daniel 'Jax' Miller", character_name="Jax Miller (Helicopter Pilot)", is_lead=False, daily_rate=6000.0, contact_info="jax@flightcrew.com"),
            Actor(actor_id="act_07", name="Robert Chen", character_name="Officer Chen (Base Security)", is_lead=False, daily_rate=5000.0, contact_info="chen@securitycast.com"),
            Actor(actor_id="act_08", name="Dr. Helen Kross", character_name="Dr. Helen Kross (Xenobiologist)", is_lead=False, daily_rate=7500.0, contact_info="kross@talent.com"),
        ]

        crew = [
            CrewMember(crew_id="crw_01", name="Elena Rostova", department="Directing", role="Director", daily_rate=15000.0),
            CrewMember(crew_id="crw_02", name="Claire Delacroix", department="Camera", role="Director of Photography", daily_rate=6500.0),
            CrewMember(crew_id="crw_03", name="James Sterling", department="Directing", role="1st Assistant Director", daily_rate=4000.0),
            CrewMember(crew_id="crw_04", name="Sound Unit Alpha", department="Sound", role="Sound Mixer & Boom Operator", daily_rate=3200.0),
            CrewMember(crew_id="crw_05", name="Marcus Webb", department="Production", role="Line Producer", daily_rate=4500.0),
            CrewMember(crew_id="crw_06", name="Victor Vance", department="Lighting", role="Gaffer / Master Electrician", daily_rate=2800.0),
            CrewMember(crew_id="crw_07", name="Hannah Abbott", department="Grip", role="Key Grip", daily_rate=2600.0),
            CrewMember(crew_id="crw_08", name="Oliver Queen", department="Special Effects", role="SFX Lead Supervisor", daily_rate=3800.0),
            CrewMember(crew_id="crw_09", name="Maria Santos", department="Art", role="Props Master", daily_rate=2400.0),
            CrewMember(crew_id="crw_10", name="Chloe Bennet", department="Production", role="Script Supervisor", daily_rate=2200.0),
        ]

        locations = [
            Location(
                location_id="loc_01",
                name="Alpine Ridge Summit",
                address="High Altitude Summit Rig, Mount Rainier Sector 4",
                indoor_outdoor=IndoorOutdoor.OUTDOOR,
                daily_rate=8000.0,
                permit_required=True,
                weather_vulnerable=True,
                notes="Extreme weather exposure. Helicopter access required.",
            ),
            Location(
                location_id="loc_02",
                name="Station Command Bunker",
                address="Stage 4 Soundstage, Pinewood Studios",
                indoor_outdoor=IndoorOutdoor.INDOOR,
                daily_rate=6500.0,
                permit_required=False,
                weather_vulnerable=False,
                notes="Primary cover set. Fully climate controlled.",
            ),
            Location(
                location_id="loc_03",
                name="Sub-Zero Quantum Vault",
                address="Stage 2 Soundstage, Pinewood Studios",
                indoor_outdoor=IndoorOutdoor.INDOOR,
                daily_rate=7000.0,
                permit_required=False,
                weather_vulnerable=False,
                notes="Specialized interior set with cryogenic lighting rigs.",
            ),
            Location(
                location_id="loc_04",
                name="Glacier Ridge Pass",
                address="North Basin Glacier Drop Zone, Sector 9",
                indoor_outdoor=IndoorOutdoor.OUTDOOR,
                daily_rate=9500.0,
                permit_required=True,
                weather_vulnerable=True,
                notes="Helicopter landing pad. Subject to blizzard shutdowns.",
            ),
        ]

        equipment = [
            Equipment(equipment_id="eq_01", name="RED V-Raptor XL 8K Camera Package", category="Camera", daily_rate=2500.0, is_critical=True),
            Equipment(equipment_id="eq_02", name="Technocrane 50ft Super-Crane", category="Crane", daily_rate=4800.0, is_critical=True),
            Equipment(equipment_id="eq_03", name="Deep Space Transceiver Prop Rig", category="Props / SFX", daily_rate=1800.0, is_critical=False),
            Equipment(equipment_id="eq_04", name="High-Output LED Storm Array", category="Lighting", daily_rate=2200.0, is_critical=False),
            Equipment(equipment_id="eq_05", name="32-Channel Ambisonic Sound Field Unit", category="Sound", daily_rate=1500.0, is_critical=False),
        ]

        scenes = [
            # Day 1 - Command Bunker
            Scene(
                scene_id="sc_01", scene_number="1A", title="Transmission Intercept",
                description="Dr. Mercer intercepts an mysterious extraterrestrial signal on high-frequency arrays.",
                shooting_date="2026-10-01", start_time="08:00", duration=4.0, location_id="loc_02",
                actor_ids=["act_01", "act_04"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_04", "crw_10"], equipment_ids=["eq_01", "eq_05"],
                estimated_cost=45000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_02", scene_number="1B", title="Bunker Lockdown Protocol",
                description="Commander Vance orders immediate security lockdown after signal verification.",
                shooting_date="2026-10-01", start_time="13:00", duration=3.5, location_id="loc_02",
                actor_ids=["act_01", "act_02", "act_07"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_06"], equipment_ids=["eq_01"],
                estimated_cost=38000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            # Day 2 - Command Bunker
            Scene(
                scene_id="sc_03", scene_number="2A", title="Decrypting the Signal",
                description="Dr. Thorne arrives to decode the complex mathematical structure of the transmission.",
                shooting_date="2026-10-02", start_time="08:30", duration=4.5, location_id="loc_02",
                actor_ids=["act_01", "act_03", "act_04"], crew_ids=["crw_01", "crw_02", "crw_04", "crw_09"], equipment_ids=["eq_01", "eq_03"],
                estimated_cost=32000.0, priority=PriorityLevel.MEDIUM, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_04", scene_number="2B", title="First Signal Anomaly",
                description="The decoded signal triggers a power flare across main station terminals.",
                shooting_date="2026-10-02", start_time="14:00", duration=3.0, location_id="loc_02",
                actor_ids=["act_02", "act_03"], crew_ids=["crw_01", "crw_02", "crw_06", "crw_08"], equipment_ids=["eq_01", "eq_04"],
                estimated_cost=29000.0, priority=PriorityLevel.MEDIUM, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            # Day 3 - Alpine Summit (Outdoor / Weather Sensitive)
            Scene(
                scene_id="sc_05", scene_number="3A", title="Summit Antenna Calibration",
                description="Dr. Mercer and Commander Vance climb the summit array to manually align high-gain dish.",
                shooting_date="2026-10-03", start_time="07:00", duration=5.0, location_id="loc_01",
                actor_ids=["act_01", "act_02"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_07", "crw_08"], equipment_ids=["eq_01", "eq_02", "eq_03"],
                estimated_cost=65000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_06", scene_number="3B", title="Ice Storm Warning",
                description="Summit meteorological sensors warn of an approaching arctic freeze.",
                shooting_date="2026-10-03", start_time="13:00", duration=3.0, location_id="loc_01",
                actor_ids=["act_02", "act_04"], crew_ids=["crw_01", "crw_02", "crw_04"], equipment_ids=["eq_01", "eq_04"],
                estimated_cost=35000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            # Day 4 - Alpine Summit & Ridge
            Scene(
                scene_id="sc_07", scene_number="4A", title="Antenna Breakdown",
                description="Sub-zero wind shear damages the primary receiver rig, forcing emergency repairs.",
                shooting_date="2026-10-04", start_time="07:30", duration=4.0, location_id="loc_01",
                actor_ids=["act_01", "act_03"], crew_ids=["crw_01", "crw_02", "crw_07"], equipment_ids=["eq_01", "eq_02"],
                estimated_cost=42000.0, priority=PriorityLevel.MEDIUM, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_08", scene_number="4B", title="Glacier Recon Inspection",
                description="Jax Miller pilots helicopter reconnaissance over glacier ridge approach.",
                shooting_date="2026-10-04", start_time="12:30", duration=4.5, location_id="loc_04",
                actor_ids=["act_02", "act_06"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_08"], equipment_ids=["eq_01"],
                estimated_cost=78000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            # Day 5 - Sub-Zero Quantum Vault
            Scene(
                scene_id="sc_09", scene_number="5A", title="Emergency Vault Descent",
                description="Dr. Mercer and Dr. Thorne descend into sub-zero crypt vault holding quantum drive.",
                shooting_date="2026-10-05", start_time="08:00", duration=4.0, location_id="loc_03",
                actor_ids=["act_01", "act_03"], crew_ids=["crw_01", "crw_02", "crw_05", "crw_10"], equipment_ids=["eq_01", "eq_05"],
                estimated_cost=48000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_10", scene_number="5B", title="Quantum Core Malfunction",
                description="The quantum drive pulses violently, overloading local environmental shielding.",
                shooting_date="2026-10-05", start_time="13:00", duration=4.0, location_id="loc_03",
                actor_ids=["act_01", "act_03", "act_08"], crew_ids=["crw_01", "crw_02", "crw_06", "crw_08"], equipment_ids=["eq_01", "eq_04"],
                estimated_cost=54000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            # Day 6 - Sub-Zero Quantum Vault
            Scene(
                scene_id="sc_11", scene_number="6A", title="Vault Power Overload",
                description="Emergency generators kick in as cryogenic coolant tubes freeze over.",
                shooting_date="2026-10-06", start_time="08:00", duration=3.5, location_id="loc_03",
                actor_ids=["act_03", "act_04"], crew_ids=["crw_01", "crw_02", "crw_06"], equipment_ids=["eq_01"],
                estimated_cost=36000.0, priority=PriorityLevel.MEDIUM, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_12", scene_number="6B", title="Sub-Level Containment Breach",
                description="General Pendelton orders cryogenic quarantine of sub-level vault 3.",
                shooting_date="2026-10-06", start_time="12:30", duration=4.5, location_id="loc_03",
                actor_ids=["act_02", "act_05", "act_07"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_08"], equipment_ids=["eq_01", "eq_04"],
                estimated_cost=58000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            # Day 7 - Glacier Pass (Outdoor / Weather Sensitive)
            Scene(
                scene_id="sc_13", scene_number="7A", title="Glacier Pass Helicopter Extraction",
                description="Jax Miller attempts precision landing on narrow ice shelf under high winds.",
                shooting_date="2026-10-07", start_time="07:00", duration=5.0, location_id="loc_04",
                actor_ids=["act_02", "act_06"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_07", "crw_08"], equipment_ids=["eq_01", "eq_02"],
                estimated_cost=85000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_14", scene_number="7B", title="Blizzard Flight Rescue",
                description="Dr. Mercer and Dr. Kross are winched aboard amidst zero-visibility blizzard.",
                shooting_date="2026-10-07", start_time="13:00", duration=4.0, location_id="loc_04",
                actor_ids=["act_01", "act_06", "act_08"], crew_ids=["crw_01", "crw_02", "crw_08"], equipment_ids=["eq_01"],
                estimated_cost=92000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            # Day 8 - Alpine Summit
            Scene(
                scene_id="sc_15", scene_number="8A", title="Base Security Patrol",
                description="Security Officer Chen surveys summit perimeter following thermal signals.",
                shooting_date="2026-10-08", start_time="08:00", duration=3.0, location_id="loc_01",
                actor_ids=["act_07"], crew_ids=["crw_01", "crw_02", "crw_04"], equipment_ids=["eq_01"],
                estimated_cost=25000.0, priority=PriorityLevel.LOW, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_16", scene_number="8B", title="Final Signal Relay",
                description="Mercer establishes high-bandwidth uplink to relay orbital telemetry.",
                shooting_date="2026-10-08", start_time="12:00", duration=5.0, location_id="loc_01",
                actor_ids=["act_01", "act_02", "act_04"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_07"], equipment_ids=["eq_01", "eq_02", "eq_03"],
                estimated_cost=68000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.OUTDOOR, weather_sensitive=True, status=SceneStatus.SCHEDULED
            ),
            # Day 9 - Command Bunker
            Scene(
                scene_id="sc_17", scene_number="9A", title="Command Center Confrontation",
                description="General Pendelton demands complete shutdown of the signal array.",
                shooting_date="2026-10-09", start_time="08:30", duration=4.0, location_id="loc_02",
                actor_ids=["act_01", "act_02", "act_05"], crew_ids=["crw_01", "crw_02", "crw_03", "crw_10"], equipment_ids=["eq_01"],
                estimated_cost=42000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_18", scene_number="9B", title="Declassifying Project Signal",
                description="Maya Lin uncovers classified logs detailing 1978 original signal discovery.",
                shooting_date="2026-10-09", start_time="13:30", duration=3.5, location_id="loc_02",
                actor_ids=["act_03", "act_04"], crew_ids=["crw_01", "crw_02", "crw_04", "crw_09"], equipment_ids=["eq_01"],
                estimated_cost=31000.0, priority=PriorityLevel.MEDIUM, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            # Day 10 - Sub-Zero Vault & Command Bunker
            Scene(
                scene_id="sc_19", scene_number="10A", title="Quantum Core Stabilized",
                description="Dr. Mercer inserts cryogenic dampening rod into the core chamber.",
                shooting_date="2026-10-10", start_time="08:00", duration=4.5, location_id="loc_03",
                actor_ids=["act_01", "act_03"], crew_ids=["crw_01", "crw_02", "crw_06", "crw_08"], equipment_ids=["eq_01", "eq_04"],
                estimated_cost=62000.0, priority=PriorityLevel.HIGH, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
            Scene(
                scene_id="sc_20", scene_number="10B", title="Transmission Epilogue",
                description="Final static fades as mountain sunrise illuminates the quiet station.",
                shooting_date="2026-10-10", start_time="13:30", duration=3.0, location_id="loc_02",
                actor_ids=["act_01", "act_02"], crew_ids=["crw_01", "crw_02", "crw_04", "crw_10"], equipment_ids=["eq_01"],
                estimated_cost=28000.0, priority=PriorityLevel.LOW, indoor_outdoor=IndoorOutdoor.INDOOR, weather_sensitive=False, status=SceneStatus.SCHEDULED
            ),
        ]

        shooting_days = [
            ShootingDay(day_number=1, date="2026-10-01", call_time="06:00", wrap_time="17:30", location_id="loc_02", scene_ids=["sc_01", "sc_02"], estimated_daily_cost=83000.0, notes="Command Bunker Interior Day 1"),
            ShootingDay(day_number=2, date="2026-10-02", call_time="06:30", wrap_time="17:30", location_id="loc_02", scene_ids=["sc_03", "sc_04"], estimated_daily_cost=61000.0, notes="Command Bunker Decryption Scenes"),
            ShootingDay(day_number=3, date="2026-10-03", call_time="05:30", wrap_time="18:30", location_id="loc_01", scene_ids=["sc_05", "sc_06"], estimated_daily_cost=100000.0, notes="Alpine Summit Exterior Unit Day 1"),
            ShootingDay(day_number=4, date="2026-10-04", call_time="05:30", wrap_time="18:30", location_id="loc_01", scene_ids=["sc_07", "sc_08"], estimated_daily_cost=120000.0, notes="Summit & Glacier Helicopter Sequence"),
            ShootingDay(day_number=5, date="2026-10-05", call_time="06:00", wrap_time="18:00", location_id="loc_03", scene_ids=["sc_09", "sc_10"], estimated_daily_cost=102000.0, notes="Quantum Vault Interior Shoot Day 1"),
            ShootingDay(day_number=6, date="2026-10-06", call_time="06:00", wrap_time="18:00", location_id="loc_03", scene_ids=["sc_11", "sc_12"], estimated_daily_cost=94000.0, notes="Quantum Core Containment Scenes"),
            ShootingDay(day_number=7, date="2026-10-07", call_time="05:00", wrap_time="18:30", location_id="loc_04", scene_ids=["sc_13", "sc_14"], estimated_daily_cost=177000.0, notes="Glacier Pass Helicopter Stunts"),
            ShootingDay(day_number=8, date="2026-10-08", call_time="05:30", wrap_time="18:00", location_id="loc_01", scene_ids=["sc_15", "sc_16"], estimated_daily_cost=93000.0, notes="Summit Relay Finale"),
            ShootingDay(day_number=9, date="2026-10-09", call_time="06:30", wrap_time="17:30", location_id="loc_02", scene_ids=["sc_17", "sc_18"], estimated_daily_cost=73000.0, notes="Command Center Climax"),
            ShootingDay(day_number=10, date="2026-10-10", call_time="06:30", wrap_time="17:00", location_id="loc_03", scene_ids=["sc_19", "sc_20"], estimated_daily_cost=90000.0, notes="Principal Photography Wrap"),
        ]

        default_schedule = ProductionSchedule(
            id="sched_last_signal",
            project_title="The Last Signal",
            director="Elena Rostova",
            producer="Marcus Webb",
            total_budget=5500000.0,
            daily_burn_rate=85000.0,
            start_date="2026-10-01",
            total_days=10,
            scenes=scenes,
            actors=actors,
            crew=crew,
            locations=locations,
            equipment=equipment,
            shooting_days=shooting_days,
        )

        self.schedules[default_schedule.id] = default_schedule
        logger.info("Initialized in-memory database with 'The Last Signal' 20-scene production dataset.")


db_session = InMemoryDatabase()
