import { useState } from "react";
import { rolesService } from "@/services/api";
import type { RoleComparison } from "@/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function RoleCompare() {
  const [roleA, setRoleA] = useState("Data Scientist");
  const [roleB, setRoleB] = useState("Full Stack Developer");
  const [comparison, setComparison] = useState<RoleComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const compare = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await rolesService.compare(roleA, roleB);
      setComparison(r.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to compare roles. Are you logged in?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 mb-1">Role Comparison</h1>
      <p className="text-slate-500">
        Compare skill requirements between two job roles.
      </p>
      {error && (
        <div className="p-3 rounded bg-red-50 text-red-700 text-sm border border-red-100">
          {error}
        </div>
      )}
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Role A
          </label>
          <select
            value={roleA}
            onChange={(e) => setRoleA(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
          >
            <option>Data Scientist</option>
            <option>Full Stack Developer</option>
            <option>Frontend Developer</option>
            <option>Backend Developer</option>
            <option>DevOps Engineer</option>
            <option>Machine Learning Engineer</option>
            <option>Data Analyst</option>
            <option>Cloud Architect</option>
            <option>Product Manager</option>
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Role B
          </label>
          <select
            value={roleB}
            onChange={(e) => setRoleB(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
          >
            <option>Full Stack Developer</option>
            <option>Data Scientist</option>
            <option>Frontend Developer</option>
            <option>Backend Developer</option>
            <option>DevOps Engineer</option>
            <option>Machine Learning Engineer</option>
            <option>Data Analyst</option>
            <option>Cloud Architect</option>
            <option>Product Manager</option>
          </select>
        </div>
        <button
          onClick={compare}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Comparing..." : "Compare Roles"}
        </button>
      </div>

      {comparison && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Match Score</CardTitle>
              </CardHeader>
              <CardContent className="p-6 text-center">
                <div className="text-4xl font-bold text-indigo-600">
                  {comparison.match_percentage}%
                </div>
                <p className="text-slate-500 text-sm mt-2">skill overlap</p>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-blue-600">{roleA}</CardTitle>
                </CardHeader>
                <CardContent className="p-3">
                  <div className="space-y-2">
                    {comparison.role_a_skills.map((s) => (
                      <div key={s.skill} className="text-sm flex justify-between">
                        <span>{s.skill}</span>
                        <span className="text-slate-500">{s.demand_score}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-green-600">{roleB}</CardTitle>
                </CardHeader>
                <CardContent className="p-3">
                  <div className="space-y-2">
                    {comparison.role_b_skills.map((s) => (
                      <div key={s.skill} className="text-sm flex justify-between">
                        <span>{s.skill}</span>
                        <span className="text-slate-500">{s.demand_score}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>Skill Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-semibold text-slate-700 mb-2">Common</h4>
                  <div className="flex flex-wrap gap-2">
                    {comparison.common_skills.map((s) => (
                      <span key={s} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded border border-green-100">
                        {s}
                      </span>
                    ))}
                    {comparison.common_skills.length === 0 && <span className="text-xs text-slate-400">None</span>}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-700 mb-2">{roleA} Only</h4>
                  <div className="flex flex-wrap gap-2">
                    {comparison.role_a_only.map((s) => (
                      <span key={s} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded border border-blue-100">
                        {s}
                      </span>
                    ))}
                    {comparison.role_a_only.length === 0 && <span className="text-xs text-slate-400">None</span>}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-700 mb-2">{roleB} Only</h4>
                  <div className="flex flex-wrap gap-2">
                    {comparison.role_b_only.map((s) => (
                      <span key={s} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded border border-green-100">
                        {s}
                      </span>
                    ))}
                    {comparison.role_b_only.length === 0 && <span className="text-xs text-slate-400">None</span>}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
