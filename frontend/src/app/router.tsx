import { Navigate, Outlet, RouterProvider, createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../layouts/AppLayout";
import { useAuth } from "../features/auth/AuthContext";
import { LoadingState } from "../components/Feedback";
import { LoginPage } from "../pages/LoginPage";
import { DashboardPage } from "../pages/DashboardPage";
import { StoppageEntryPage } from "../pages/StoppageEntryPage";
import { StoppageHistoryPage } from "../pages/StoppageHistoryPage";
import { ReportsPage } from "../pages/ReportsPage";
import { AdminPage } from "../pages/AdminPage";
import { ErrorBoundary } from "./ErrorBoundary";

function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingState label="Checking session..." />;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

function GuestRoute() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingState />;
  if (user) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

export const router = createBrowserRouter([
  {
    element: <GuestRoute />,
    children: [{ path: "/login", element: <LoginPage /> }],
  },
  {
    element: <ProtectedRoute />,
    errorElement: <ErrorBoundary><div /></ErrorBoundary>,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/", element: <Navigate to="/dashboard" replace /> },
          { path: "/dashboard", element: <DashboardPage /> },
          { path: "/stoppage-entry", element: <StoppageEntryPage /> },
          { path: "/stoppage-history", element: <StoppageHistoryPage /> },
          { path: "/reports", element: <ReportsPage /> },
          { path: "/admin", element: <AdminPage /> },
          { path: "/admin/users", element: <AdminPage /> },
          { path: "/admin/supervisors", element: <AdminPage /> },
          { path: "/admin/machines", element: <AdminPage /> },
          { path: "/admin/shifts", element: <AdminPage /> },
          { path: "/admin/stoppage-reasons", element: <AdminPage /> },
        ],
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
