"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ProductionSchedule } from "@/lib/types";
import { ScheduleView } from "@/components/views/ScheduleView";

export default function SchedulePage() {
  const [schedule, setSchedule] = useState<ProductionSchedule | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProduction()
      .then(setSchedule)
      .catch(() => setSchedule(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <ScheduleView shootingDays={schedule?.shooting_days || []} schedule={schedule} />
    </div>
  );
}
