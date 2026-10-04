import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import DashboardOutlinedIcon from "@mui/icons-material/DashboardOutlined";
import HistoryOutlinedIcon from "@mui/icons-material/HistoryOutlined";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import NoteAddOutlinedIcon from "@mui/icons-material/NoteAddOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import {
  AppBar,
  Box,
  Chip,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { branding } from "../config/branding";
import { useAuth } from "../features/auth/AuthContext";
import { useStoppageSocket } from "../hooks/useStoppageSocket";

const drawerWidth = 260;

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: <DashboardOutlinedIcon /> },
  { to: "/stoppage-entry", label: "Stoppage Entry", icon: <NoteAddOutlinedIcon /> },
  { to: "/stoppage-history", label: "Stoppage History", icon: <HistoryOutlinedIcon /> },
  { to: "/reports", label: "Reports", icon: <AssessmentOutlinedIcon /> },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const queryClient = useQueryClient();
  const status = useStoppageSocket(() => {
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["stoppages"] });
  });
  const title = [...nav, { to: "/admin", label: "Master Data" }].find((item) => location.pathname.startsWith(item.to))?.label ?? branding.appName;

  const drawer = (
    <Box>
      <Box px={2} py={3}>
        <Typography variant="subtitle2" color="secondary">
          {branding.companyName}
        </Typography>
        <Typography variant="h6" color="white">
          {branding.appName}
        </Typography>
      </Box>
      <Divider sx={{ borderColor: "rgba(255,255,255,0.12)" }} />
      <List>
        {nav.map((item) => (
          <ListItemButton
            key={item.to}
            component={NavLink}
            to={item.to}
            onClick={() => setMobileOpen(false)}
            selected={location.pathname.startsWith(item.to)}
            sx={{ mx: 1, borderRadius: 1, "&.Mui-selected": { bgcolor: "rgba(196,92,38,0.2)" } }}
          >
            <ListItemIcon sx={{ color: "inherit" }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
        {user?.role === "admin" ? (
          <>
            <Divider sx={{ my: 1, borderColor: "rgba(255,255,255,0.12)" }} />
            <ListItemButton
              component={NavLink}
              to="/admin"
              selected={location.pathname.startsWith("/admin")}
              onClick={() => setMobileOpen(false)}
              sx={{ mx: 1, borderRadius: 1 }}
            >
              <ListItemIcon sx={{ color: "inherit" }}>
                <SettingsOutlinedIcon />
              </ListItemIcon>
              <ListItemText primary="Master Data" />
            </ListItemButton>
          </>
        ) : null}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }} elevation={0}>
        <Toolbar>
          <IconButton color="inherit" edge="start" sx={{ mr: 2, display: { md: "none" } }} onClick={() => setMobileOpen(true)} aria-label="Open navigation">
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          {status ? (
            <Chip
              size="small"
              label={status === "live" ? "Live updates connected" : "Live updates disconnected"}
              color={status === "live" ? "success" : "warning"}
              sx={{ mr: 2 }}
            />
          ) : null}
          <Chip label={user?.role === "admin" ? "Admin" : "Supervisor"} sx={{ mr: 1, bgcolor: "rgba(255,255,255,0.12)", color: "white" }} />
          <Typography sx={{ mr: 2 }}>{user?.username}</Typography>
          <IconButton color="inherit" onClick={logout} aria-label="Sign out">
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: "block", md: "none" }, "& .MuiDrawer-paper": { width: drawerWidth, bgcolor: "#1B3A4B", color: "white" } }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{ display: { xs: "none", md: "block" }, "& .MuiDrawer-paper": { width: drawerWidth, bgcolor: "#1B3A4B", color: "white", border: 0 } }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, width: { md: `calc(100% - ${drawerWidth}px)` } }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
