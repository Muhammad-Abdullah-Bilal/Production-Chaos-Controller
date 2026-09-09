import { Card } from "@/components/ui/Card";
import { formatCurrency } from "@/lib/utils";
import { Calendar, DollarSign, AlertTriangle, ShieldCheck } from "lucide-react";

interface MetricsGridProps {
  totalBudget?: number;
  dailyBurnRate?: number;
  activeDisruptionsCount?: number;
  pendingApprovalsCount?: number;
}

export function MetricsGrid({
  totalBudget = 4500000,
  dailyBurnRate = 75000,
  activeDisruptionsCount = 0,
  pendingApprovalsCount = 0,
}: MetricsGridProps) {
  const metrics = [
    {
      title: "Daily Production Burn Rate",
      value: formatCurrency(dailyBurnRate),
      subtext: "Cost per shoot day (Cast & Crew)",
      icon: DollarSign,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10 border-emerald-500/20",
    },
    {
      title: "Total Approved Budget",
      value: formatCurrency(totalBudget),
      subtext: "Day 1 of 28 scheduled",
      icon: Calendar,
      color: "text-blue-400",
      bg: "bg-blue-500/10 border-blue-500/20",
    },
    {
      title: "Active Production Disruptions",
      value: activeDisruptionsCount.toString(),
      subtext: activeDisruptionsCount > 0 ? "Requires mitigation plan" : "Production running smoothly",
      icon: AlertTriangle,
      color: activeDisruptionsCount > 0 ? "text-amber-400" : "text-slate-400",
      bg: activeDisruptionsCount > 0 ? "bg-amber-500/10 border-amber-500/20" : "bg-slate-800/40 border-slate-800",
    },
    {
      title: "Pending Producer Approvals",
      value: pendingApprovalsCount.toString(),
      subtext: "Human-in-the-loop signoff required",
      icon: ShieldCheck,
      color: pendingApprovalsCount > 0 ? "text-indigo-400" : "text-slate-400",
      bg: pendingApprovalsCount > 0 ? "bg-indigo-500/10 border-indigo-500/20" : "bg-slate-800/40 border-slate-800",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((m, idx) => {
        const Icon = m.icon;
        return (
          <Card key={idx} className="relative overflow-hidden">
            <div className="flex items-center justify-between pb-3">
              <span className="text-xs font-medium text-slate-400">{m.title}</span>
              <div className={`p-2 rounded-lg border ${m.bg}`}>
                <Icon className={`h-4 w-4 ${m.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold tracking-tight text-white">{m.value}</div>
            <p className="text-xs text-slate-400 mt-1">{m.subtext}</p>
          </Card>
        );
      })}
    </div>
  );
}
