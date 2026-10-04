import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import { PageHeader } from "../components/Feedback";
import { useAuth } from "../features/auth/AuthContext";
import { useSnackbar } from "../app/SnackbarProvider";
import { apiErrorMessage } from "../services/api/client";
import { masterDataService } from "../services/masterDataService";

export function AdminPage() {
  const { user } = useAuth();
  const notify = useSnackbar();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState(0);
  const [search, setSearch] = useState("");
  const [dialog, setDialog] = useState<{ type: string; item?: Record<string, unknown> } | null>(null);

  const masters = useQuery({
    queryKey: ["admin-masters"],
    queryFn: async () => ({
      users: await masterDataService.users(),
      supervisors: await masterDataService.supervisors(),
      machines: await masterDataService.machines(),
      shifts: await masterDataService.shifts(),
      reasons: await masterDataService.reasons(),
    }),
    enabled: user?.role === "admin",
  });

  const save = useMutation({
    mutationFn: async () => {
      if (!dialog) return;
      const item = dialog.item ?? {};
      if (dialog.type === "users") {
        if (item.id) await masterDataService.updateUser(String(item.id), item);
        else await masterDataService.createUser(item);
      } else if (dialog.type === "supervisors") {
        if (item.id) await masterDataService.updateSupervisor(String(item.id), item);
        else await masterDataService.createSupervisor(item);
      } else if (dialog.type === "machines") {
        if (item.id) await masterDataService.updateMachine(String(item.id), item);
        else await masterDataService.createMachine(item);
      } else if (dialog.type === "shifts") {
        if (item.id) await masterDataService.updateShift(String(item.id), item);
        else await masterDataService.createShift(item);
      } else if (dialog.type === "reasons") {
        if (item.id) await masterDataService.updateReason(String(item.id), item);
        else await masterDataService.createReason(item);
      }
    },
    onSuccess: () => {
      notify("Master data saved.", "success");
      queryClient.invalidateQueries({ queryKey: ["admin-masters"] });
      queryClient.invalidateQueries({ queryKey: ["masters"] });
      queryClient.invalidateQueries({ queryKey: ["masters-active"] });
      setDialog(null);
    },
    onError: (error) => notify(apiErrorMessage(error), "error"),
  });

  if (user?.role !== "admin") return <Navigate to="/dashboard" replace />;

  const tabs = ["users", "supervisors", "machines", "shifts", "reasons"] as const;
  const current = tabs[tab];
          const rows = ((masters.data?.[current === "reasons" ? "reasons" : current] ?? []) as unknown as Array<Record<string, unknown>>).filter((row) =>
    JSON.stringify(row).toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <>
      <PageHeader title="Master Data" subtitle="Activate or deactivate records instead of deleting history." />
      <Tabs value={tab} onChange={(_, value) => setTab(value)} sx={{ mb: 2 }}>
        <Tab label="Users" />
        <Tab label="Supervisors" />
        <Tab label="Machines" />
        <Tab label="Shifts" />
        <Tab label="Stoppage Reasons" />
      </Tabs>
      <Stack direction="row" gap={2} mb={2}>
        <TextField label="Search" value={search} onChange={(e) => setSearch(e.target.value)} sx={{ maxWidth: 320 }} />
        <Button variant="contained" onClick={() => setDialog({ type: current, item: current === "users" ? { role: "supervisor", is_active: true } : { active: true } })}>
          Add
        </Button>
      </Stack>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Name / Code</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={String(row.id)}>
              <TableCell>{String(row.username ?? row.name ?? row.code)}</TableCell>
              <TableCell>{row.active === false || row.is_active === false ? "Inactive" : "Active"}</TableCell>
              <TableCell>
                <Button size="small" onClick={() => setDialog({ type: current, item: { ...row } })}>
                  Edit
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    const next = { ...row };
                    if ("is_active" in next) next.is_active = !Boolean(next.is_active);
                    else next.active = !Boolean(next.active);
                    setDialog({ type: current, item: next });
                  }}
                >
                  Activate/Deactivate
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Dialog open={!!dialog} onClose={() => setDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{dialog?.item && "id" in (dialog.item ?? {}) ? "Edit" : "Add"} {current}</DialogTitle>
        <DialogContent>
          <Box mt={1} display="grid" gap={2}>
            {current === "users" ? (
              <>
                <TextField label="Username" value={dialog?.item?.username ?? ""} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, username: e.target.value } })} />
                <TextField label="Password" type="password" onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, password: e.target.value } })} helperText="Leave blank when editing if you do not want to change it." />
                <TextField select label="Role" value={dialog?.item?.role ?? "supervisor"} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, role: e.target.value } })}>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="supervisor">Supervisor</MenuItem>
                </TextField>
              </>
            ) : null}
            {current === "supervisors" || current === "reasons" ? (
              <TextField label="Name" value={dialog?.item?.name ?? ""} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, name: e.target.value } })} />
            ) : null}
            {current === "machines" ? (
              <TextField label="Code" value={dialog?.item?.code ?? ""} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, code: e.target.value } })} />
            ) : null}
            {current === "shifts" ? (
              <>
                <TextField label="Code" value={dialog?.item?.code ?? ""} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, code: e.target.value } })} />
                <TextField label="Name" value={dialog?.item?.name ?? ""} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, name: e.target.value } })} />
                <TextField label="Start time" type="time" InputLabelProps={{ shrink: true }} value={String(dialog?.item?.start_time ?? "").slice(0, 5)} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, start_time: `${e.target.value}:00` } })} />
                <TextField label="End time" type="time" InputLabelProps={{ shrink: true }} value={String(dialog?.item?.end_time ?? "").slice(0, 5)} onChange={(e) => setDialog({ ...dialog!, item: { ...dialog!.item, end_time: `${e.target.value}:00` } })} />
              </>
            ) : null}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(null)}>Cancel</Button>
          <Button variant="contained" onClick={() => save.mutate()} disabled={save.isPending}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
