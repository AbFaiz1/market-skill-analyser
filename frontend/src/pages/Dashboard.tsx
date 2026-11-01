import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { dashboardService, ingestService } from "@/services/api";
import type { DashboardStats } from "@/types";
import { ArrowUp, ArrowDown, TrendingUp, Layers, RefreshCw, Plus } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function KpiCard({ title, value, subtitle, icon: Icon, color }: any) {
  return (
    <Card className="bg-white border-slate-200 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-500">{title}</CardTitle>
        <Icon className={`h-6 w-6 ${color}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-900">{value}</div>
        <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await dashboardService.stats();
      setStats(r.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load dashboard stats. Are you logged in?");
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const seedData = async () => {
    setSeeding(true);
    setError(null);
    try {
      await ingestService.mock(10);
      await loadStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to seed sample data. Are you logged in?");
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) {
    return (
      <div className="p-4 space-y-4">
        <div className="p-3 rounded bg-red-50 text-red-700 text-sm border border-red-100">
          {error}
        </div>
        <button
          onClick={loadStats}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium"
        >
          Retry
        </button>
      </div>
    );
  }
  if (!stats) return <div className="p-4">No data</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-1">Dashboard</h1>
          <p className="text-slate-500">Overview of the job market and skill demand.</p>
        </div>
        {stats.total_jobs === 0 && (
          <button
            onClick={seedData}
            disabled={seeding}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            {seeding ? (
              <>
                <RefreshCw size={16} className="animate-spin" /> Seeding...
              </>
            ) : (
              <>
                <Plus size={16} /> Seed Sample Data
              </>
            )}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard
          title="Total Jobs Analyzed"
          value={stats.total_jobs}
          subtitle="Job postings in database"
          icon={Layers}
          color="text-blue-500"
        />
        <KpiCard
          title="Total Skills Tracked"
          value={stats.total_skills}
          subtitle="Unique skills extracted"
          icon={TrendingUp}
          color="text-green-500"
        />
        <KpiCard
          title="Top Skill Demand"
          value={stats.top_skills[0]?.name || "-"}
          subtitle={`${stats.top_skills[0]?.demand_score?.toFixed(0) || 0}% demand`}
          icon={ArrowUp}
          color="text-indigo-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="bg-white border-slate-200 shadow-sm col-span-1 lg:col-span-2">
          <CardHeader>
            <CardTitle>Top Skills by Demand</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.top_skills.slice(0, 10).reverse()}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="demand_score" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-red-600 flex items-center gap-2">
              <ArrowDown size={18} /> Declining Skills
            </CardTitle>
            <CardDescription>Skills with decreasing demand</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {stats.declining_skills.slice(0, 8).map((s) => (
                <div key={s.id} className="p-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-600">{s.name}</span>
                    <span className="text-xs font-medium text-red-500">
                      {s.demand_score?.toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
              {stats.declining_skills.length === 0 && (
                <div className="p-3 text-xs text-slate-400 text-center">No declining skills</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-white border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Emerging Skills</CardTitle>
          <CardDescription>Skills with growing market demand</CardDescription>
        </CardHeader>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-2">
            {stats.emerging_skills.slice(0, 12).map((s) => (
              <span
                key={s.id}
                className="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-full border border-indigo-100"
              >
                {s.name}
              </span>
            ))}
            {stats.emerging_skills.length === 0 && (
              <span className="text-xs text-slate-400">None detected</span>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Jobs by Role</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {stats.roles_distribution.map((r) => (
              <div key={r.role} className="flex justify-between text-sm">
                <span className="text-slate-600">{r.role}</span>
                <span className="font-medium">{r.count}</span>
              </div>
            ))}
            {stats.roles_distribution.length === 0 && (
              <div className="p-3 text-xs text-slate-400 text-center">No roles yet</div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
