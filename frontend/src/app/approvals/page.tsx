"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { RecoveryPlan } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import { CheckCircle2, XCircle, ShieldCheck, UserCheck } from "lucide-react";

export default function ApprovalsPage() {
  const [plans, setPlans] = useState<RecoveryPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [approverName, setApproverName] = useState("Marcus Webb (Line Producer)");
  const [notes, setNotes] = useState("");
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    // In Phase 1, query disruptions to see if any recovery plans are available
    api.getDisruptions()
      .then(async (disruptions) => {
        if (disruptions.length > 0) {
          const list = await Promise.all(
            disruptions.map((d) => api.getRecoveryPlans(d.id).catch(() => []))
          );
          setPlans(list.flat());
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const handleDecision = async (planId: string, approved: boolean) => {
    try {
      const updated = await api.approveRecoveryPlan(planId, {
        approved_by: approverName,
        notes,
        approved,
      });

      setPlans((prev) => prev.map((p) => (p.id === planId ? updated : p)));
      setActionMessage(
        approved
          ? `Plan ${planId} approved by ${approverName}. Schedule changes applied!`
          : `Plan ${planId} rejected.`
      );
    } catch (err) {
      setActionMessage("Approval submission failed. Backend may be offline.");
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-indigo-400" />
          Human-in-the-Loop Approval Workflow
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Strict production safeguard: AI proposes recovery options, but only a human producer can sign off on schedule modifications.
        </p>
      </div>

      {actionMessage && (
        <Card className="p-3 bg-indigo-950/40 border-indigo-700/50 text-xs text-indigo-200 text-center">
          {actionMessage}
        </Card>
      )}

      {loading ? (
        <Card className="p-8 text-center text-slate-400">Loading approval queue...</Card>
      ) : plans.length === 0 ? (
        <Card className="p-8 text-center text-slate-400 border-dashed space-y-2">
          <UserCheck className="h-8 w-8 text-slate-600 mx-auto" />
          <p className="text-sm font-semibold text-white">No Plans Awaiting Producer Sign-off</p>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            When a recovery plan is generated in response to an active disruption, it will enter this queue for executive authorization.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {plans.map((plan) => (
            <Card key={plan.id} className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-base font-semibold text-white">{plan.title}</span>
                  <p className="text-xs text-slate-400 mt-0.5">{plan.summary}</p>
                </div>
                <Badge
                  variant={
                    plan.status === "approved"
                      ? "success"
                      : plan.status === "rejected"
                      ? "danger"
                      : "warning"
                  }
                >
                  {plan.status.toUpperCase()}
                </Badge>
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-2">
                <span className="text-slate-400 font-medium block">Proposed Schedule Alterations:</span>
                {plan.changes.length === 0 ? (
                  <span className="text-slate-500 italic">No scene shifts in this draft plan.</span>
                ) : (
                  plan.changes.map((change, idx) => (
                    <div key={idx} className="flex items-center justify-between text-slate-300">
                      <span>Scene {change.scene_number} ({change.action})</span>
                      <span className="font-mono text-indigo-400">
                        Day {change.original_day} &rarr; Day {change.target_day}
                      </span>
                    </div>
                  ))
                )}
              </div>

              {plan.status === "proposed" && (
                <div className="space-y-3 pt-2 border-t border-slate-800">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-400 mb-1">Authorizing Producer</label>
                      <input
                        type="text"
                        value={approverName}
                        onChange={(e) => setApproverName(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 mb-1">Sign-off Notes</label>
                      <input
                        type="text"
                        placeholder="e.g. Approved with condition that crane is released by 18:00"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-2">
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDecision(plan.id, false)}
                      className="gap-1.5"
                    >
                      <XCircle className="h-4 w-4" />
                      Reject Plan
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleDecision(plan.id, true)}
                      className="gap-1.5"
                    >
                      <CheckCircle2 className="h-4 w-4" />
                      Approve &amp; Apply Schedule Change
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
