import { useState } from "react";
import { Link, useNavigate, useLocation, Outlet } from "react-router-dom";
import { Menu, LogOut, TrendingUp, Users, Lightbulb, Home } from "lucide-react";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const navItems = [
    { path: "/", label: "Dashboard", icon: Home },
    { path: "/skills", label: "Skill Trends", icon: TrendingUp },
    { path: "/roles", label: "Role Comparison", icon: Users },
    { path: "/recommend", label: "Recommendations", icon: Lightbulb },
  ];

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 bg-slate-900 text-white z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <div className="w-8 h-8 bg-indigo-500 rounded flex items-center justify-center text-white font-bold">
              AI
            </div>
            <span>Skill Trend Analyzer</span>
          </Link>
          <div className="flex items-center gap-4">
            {!token ? (
              <>
                <Link to="/login" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-sm font-medium transition">
                  Login
                </Link>
                <Link to="/register" className="px-4 py-2 border border-slate-600 hover:bg-slate-800 rounded-md text-sm font-medium transition">
                  Register
                </Link>
              </>
            ) : (
              <button onClick={handleLogout} className="px-4 py-2 text-sm font-medium hover:text-indigo-300 transition flex items-center gap-2">
                <LogOut size={18} /> Sign out
              </button>
            )}
          </div>
        </div>
        <div className="md:hidden">
          <button
            onClick={() => setOpen(!open)}
            className="p-2 text-slate-400 hover:text-white"
          >
            <Menu size={24} />
          </button>
        </div>
      </nav>

      {open && (
        <div
          className={`fixed inset-0 bg-slate-900 z-[60] flex flex-col transition-transform duration-300 ${
            open ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <span className="font-bold text-xl">Menu</span>
            <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white">
              ×
            </button>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${
                  location.pathname === item.path
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <item.icon size={20} />
                {item.label}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-white transition"
            >
              <LogOut size={20} /> Sign out
            </button>
          </nav>
        </div>
      )}

      <main className="pt-16 min-h-screen bg-slate-50 pb-24">
        {typeof window !== "undefined" && window.innerWidth >= 768 && (
          <aside className="fixed left-0 top-16 h-full w-64 bg-slate-900 text-white hidden md:block z-40">
            <div className="p-6 border-b border-slate-800">
              <div className="flex items-center gap-2 font-bold text-xl tracking-tight mb-8">
                <div className="w-8 h-8 bg-indigo-500 rounded flex items-center justify-center text-white font-bold">
                  AI
                </div>
                <span>Skill Trend</span>
              </div>
            </div>
            <nav className="p-4 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    location.pathname === item.path
                      ? "bg-indigo-600 text-white"
                      : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <item.icon size={18} />
                  {item.label}
                </Link>
              ))}
            </nav>
          </aside>
        )}
        <div className="md:ml-64 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </>
  );
}
