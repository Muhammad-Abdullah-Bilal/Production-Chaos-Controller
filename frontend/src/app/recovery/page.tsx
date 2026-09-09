"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { DisruptionEvent, RecoveryPlan } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import { GitMerge, CheckCircle, Sparkles, AlertCircle, ArrowRight } from "lucide-react";

export default function RecoveryPage() {
  const [disruptions, setDisruptions] = useState<DisruptionEvent[]>([]);
  const [plans, setPlans] = useState<RecoveryPlan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDisruptions()
      .then(async (dis) => {
        setDisruptions(dis);
        if (dis.length > 0) {
          const planLists = await Promise.all(
            dis.map((d) => api.getRecoveryPlans(d.id).catch(() => []))
          );
          setPlans(planLists.flat());
        }
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <GitMerge className="h-5 w-5 text-indigo-400" />
          AI Recovery Plans &amp; Comparison
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Explore candidate recovery plans, evaluate trade-offs in cost and schedule, and inspect rationale.
        </p>
      </div>

      {loading ? (
        <Card className="p-8 text-center text-slate-400">Loading recovery plans...</Card>
      ) : plans.length === 0 ? (
        <Card className="p-8 text-center text-slate-400 border-dashed space-y-3">
          <div className="mx-auto w-12 h-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
            <Sparkles className="h-6 w-6 text-indigo-400" />
          </div>
          <p className="text-sm font-semibold text-white">No Recovery Plans Generated Yet</p>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Once a disruption is reported, the Gemini Agent Orchestrator calls deterministic tools to find substitute scenes and compute cost-minimized recovery schedules.
          </p>
          <Link href="/disruptions" className="inline-block mt-2">
            <Button size="sm" variant="secondary">
              Go to Disruption Manager
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {plans.map((plan) => (
            <Card key={plan.id} className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white text-base">{plan.title}</span>
                  {plan.is_recommended && (
                    <Badge variant="success" className="gap-1">
                      <Sparkles className="h-3 w-3" />
                      RECOMMENDED
                    </Badge>
                  )}
                </div>
                <Badge variant="outline">{plan.status.toUpperCase()}</Badge>
              </div>

              <p className="text-xs text-slate-300">{plan.summary}</p>

              {/* Rationale Explanation */}
              <div className="p-3 rounded-lg bg-indigo-950/20 border border-indigo-900/40 text-xs">
                <span className="font-semibold text-indigo-300 block mb-1">Why this plan was selected:</span>
                <p className="text-slate-300 leading-relaxed">{plan.rationale}</p>
              </div>

              {/* Estimated Schedule, Cost & Resource Impact */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-center">
                <div className="p-2 bg-slate-950 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block">Schedule Impact</span>
                  <span className="text-sm font-bold text-white">
                    {plan.impact.schedule_variance_days > 0
                      ? `+${plan.impact.schedule_variance_days} Days`
                      : "0 Day Shift"}
                  </span>
                </div>
                <div className="p-2 bg-slate-950 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block">Cost Variance</span>
                  <span className="text-sm font-bold text-emerald-400">
                    {formatCurrency(plan.impact.cost_variance_usd)}
                  </span>
                </div>
                <div className="p-2 bg-slate-950 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block">Risk Score</span>
                  <span className="text-sm font-bold text-amber-400">
                    {plan.impact.risk_score.toFixed(1)} / 10
                  </span>
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <Link href="/approvals">
                  <Button size="sm" variant="primary" className="gap-1.5 text-xs">
                    Review in Approval Workflow
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
