import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Dashboard from "@/pages/Dashboard";
import SkillsTrends from "@/pages/SkillsTrends";
import RoleCompare from "@/pages/RoleCompare";
import Recommendations from "@/pages/Recommendations";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Navbar from "@/components/Navbar";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Navbar />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "skills", element: <SkillsTrends /> },
      { path: "roles", element: <RoleCompare /> },
      { path: "recommend", element: <Recommendations /> },
    ],
  },
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
