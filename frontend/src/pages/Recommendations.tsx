import { useEffect, useState } from "react";
import { recommendService } from "@/services/api";
import type { RecommendationsOut } from "@/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Recommendations() {
  const [targetRole, setTargetRole] = useState("Data Scientist");
  const [data, setData] = useState<RecommendationsOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await recommendService.get(targetRole, 12);
      setData(r.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load recommendations. Are you logged in?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, [targetRole]);

  const priorityColor = (p: string) => {
    if (p === "high") return "bg-red-50 text-red-700 border-red-100";
    if (p === "medium") return "bg-indigo-50 text-indigo-700 border-indigo-100";
    return "bg-slate-50 text-slate-700 border-slate-100";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 mb-1">Recommendations</h1>
      <p className="text-slate-500">
        Personalized skills to learn based on your target role.
      </p>
      {error && (
        <div className="p-3 rounded bg-red-50 text-red-700 text-sm border border-red-100">
          {error}
        </div>
      )}
      </div>

      <div className="flex gap-3">
        <input
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          placeholder="Target role (e.g. Data Scientist)"
          className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
        />
        <button onClick={fetch} className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition disabled:opacity-50" disabled={loading}>
          {loading ? "..." : "Get Recommendations"}
        </button>
      </div>

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Target Role</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-medium text-indigo-600">{data.target_role}</p>
              <p className="text-sm text-slate-500 mt-1">
                Current skills: {data.current_skills.length || "none set"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Skills to Learn</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.recommendations.map((r, i) => (
                  <div
                    key={i}
                    className={`flex items-center justify-between p-2 rounded-lg border ${priorityColor(r.priority)}`}
                  >
                    <div>
                      <div className="font-medium text-slate-900">{r.skill}</div>
                      <div className="text-xs text-slate-500">{r.reason}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs font-semibold">{r.demand_score.toFixed(0)}%</div>
                      <div className="text-[10px] uppercase text-slate-400">{r.trend_label}</div>
                    </div>
                  </div>
                ))}
                {data.recommendations.length === 0 && (
                  <p className="text-xs text-slate-400 text-center">No recommendations</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
