import { useEffect, useState } from "react";
import { trendsService } from "@/services/api";
import type { Skill } from "@/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  Search,
  RefreshCw,
} from "lucide-react";

export default function SkillsTrends() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selected, setSelected] = useState<Skill | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [labelFilter, setLabelFilter] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [snapshotLoading, setSnapshotLoading] = useState(false);

  const iconFor = (label: string) => {
    if (label === "in-demand") return TrendingUp;
    if (label === "declining") return TrendingDown;
    return TrendingUp;
  };

  const loadSkills = async () => {
    setError(null);
    try {
      const r = await trendsService.trending(30, labelFilter);
      setSkills(r.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load skill trends. Are you logged in?");
    }
  };

  useEffect(() => {
    loadSkills();
  }, [labelFilter]);

  const loadHistory = async (s: Skill) => {
    setSelected(s);
    setError(null);
    try {
      const r = await trendsService.history(s.id!);
      setHistory(r.data.history || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load skill history.");
    }
  };

  const rebuildSnapshot = async () => {
    setSnapshotLoading(true);
    setError(null);
    try {
      await trendsService.snapshot("2026-01-01T00:00:00", "2026-12-31T23:59:59");
      await loadSkills();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to rebuild trend snapshot. Are you logged in?");
    } finally {
      setSnapshotLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 mb-1">Skill Trends</h1>
        <p className="text-slate-500">
          Market demand and trend classification for extracted skills.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-end">
        {error && (
          <div className="w-full p-3 rounded bg-red-50 text-red-700 text-sm border border-red-100">
            {error}
          </div>
        )}
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Filter by trend (in-demand / emerging / declining / stable)"
            className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none bg-white"
            onChange={(e) =>
              setLabelFilter(e.target.value || undefined)
            }
          />
        </div>
        <button
          onClick={rebuildSnapshot}
          disabled={snapshotLoading}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
        >
          {snapshotLoading ? (
            <>
              <RefreshCw size={18} className="animate-spin" /> Rebuilding...
            </>
          ) : (
            <>
              <RefreshCw size={18} /> Rebuild Trend Snapshot
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Skill Demand Leaderboard</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-slate-500">
                      <th className="px-4 py-3 text-left">Skill</th>
                      <th className="px-4 py-3 text-left">Category</th>
                      <th className="px-4 py-3 text-left">Demand</th>
                      <th className="px-4 py-3 text-left">Trend</th>
                      <th className="px-4 py-3 text-left">Jobs</th>
                      <th className="px-4 py-3 text-left">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {skills.map((s) => (
                      <tr
                        key={s.id}
                        onClick={() => loadHistory(s)}
                        className="cursor-pointer hover:bg-slate-50 transition"
                      >
                        <td className="px-4 py-3 font-medium">{s.name}</td>
                        <td className="px-4 py-3 text-slate-600">{s.category}</td>
                        <td className="px-4 py-3 font-semibold">
                          {s.demand_score?.toFixed(1)}%
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                            s.trend_label === "in-demand"
                              ? "bg-green-100 text-green-700"
                              : s.trend_label === "declining"
                              ? "bg-red-100 text-red-700"
                              : s.trend_label === "emerging"
                              ? "bg-indigo-100 text-indigo-700"
                              : "bg-slate-100 text-slate-700"
                          }`}
                          >
                            {(() => {
                              const Icon = iconFor(s.trend_label || "stable");
                              return <Icon size={12} />;
                            })()}
                            {s.trend_label}
                          </span>
                        </td>
                        <td className="px-4 py-3">{s.job_count}</td>
                        <td className="px-4 py-3">
                          <button
                            onClick={(e) => { e.stopPropagation(); loadHistory(s); }}
                            className="text-indigo-600 hover:underline text-xs"
                          >
                            View trend
                          </button>
                        </td>
                      </tr>
                    ))}
                    {skills.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                          No skills. Build a trend snapshot first.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>
                {selected ? `Trend: ${selected.name}` : "Select a skill"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selected && history.length > 0 ? (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period_end" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="demand_score"
                        stroke="#4f46e5"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[300px] flex flex-col items-center justify-center text-slate-400 text-sm">
                  Select a skill to see its demand trend over time.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
