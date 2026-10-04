import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { EmptyState, ErrorState, LoadingState, PageHeader } from "../components/Feedback";
import { FilterBar } from "../components/FilterBar";
import { useAuth } from "../features/auth/AuthContext";
import { useStoppageSocket } from "../hooks/useStoppageSocket";
import { apiErrorMessage } from "../services/api/client";
import { masterDataService } from "../services/masterDataService";
import { stoppageService } from "../services/stoppageService";
import type { ReportFilters, StoppageRecord } from "../types";
import { formatDate, formatDateTime, formatDuration } from "../utils/datetime";
import { useSnackbar } from "../app/SnackbarProvider";

function canMutate(role: string | undefined, supervisorId: string | null | undefined, userId: string | undefined, record: StoppageRecord) {
  if (role === "admin") return true;
  if (supervisorId) return record.supervisor_id === supervisorId;
  return record.created_by === userId;
}

export function StoppageHistoryPage() {
  const notify = useSnackbar();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<ReportFilters & { search?: string }>({});
  const [applied, setApplied] = useState<ReportFilters & { search?: string }>({});
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [view, setView] = useState<StoppageRecord | null>(null);
  const [edit, setEdit] = useState<StoppageRecord | null>(null);
  const [remove, setRemove] = useState<StoppageRecord | null>(null);

  const masters = useQuery({
    queryKey: ["masters"],
    queryFn: async () => ({
      supervisors: await masterDataService.supervisors(),
      machines: await masterDataService.machines(),
      shifts: await masterDataService.shifts(),
      reasons: await masterDataService.reasons(),
    }),
  });

  const list = useQuery({
    queryKey: ["stoppages", applied, page, pageSize],
    queryFn: () =>
      stoppageService.list({
        ...applied,
        page: page + 1,
        page_size: pageSize,
        sort_by: "created_at",
        sort_order: "desc",
      }),
  });

  useStoppageSocket(() => {
    queryClient.invalidateQueries({ queryKey: ["stoppages"] });
  });

  const removeMutation = useMutation({
    mutationFn: (id: string) => stoppageService.remove(id),
    onSuccess: () => {
      notify("Stoppage record deleted successfully.", "success");
      queryClient.invalidateQueries({ queryKey: ["stoppages"] });
      setRemove(null);
    },
    onError: (error) => notify(apiErrorMessage(error), "error"),
  });

  const updateMutation = useMutation({
    mutationFn: () =>
      stoppageService.update(edit!.id, {
        duration_minutes: Number(edit!.duration_minutes),
        details: edit!.details,
        remarks: edit!.remarks,
      }),
    onSuccess: () => {
      notify("Stoppage record updated successfully.", "success");
      queryClient.invalidateQueries({ queryKey: ["stoppages"] });
      setEdit(null);
    },
    onError: (error) => notify(apiErrorMessage(error), "error"),
  });

  const activeCount = useMemo(
    () => Object.values(applied).filter((value) => value !== undefined && value !== "").length,
    [applied],
  );

  return (
    <>
      <PageHeader title="Stoppage History" subtitle="Filter, search, and maintain previously entered downtime records." />
      <FilterBar
        activeCount={activeCount}
        onApply={() => {
          setPage(0);
          setApplied(draft);
        }}
        onClear={() => {
          setDraft({});
          setApplied({});
          setPage(0);
        }}
      >
        <TextField
          label="Date From"
          type="date"
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 180 }}
          value={draft.date_from ?? ""}
          onChange={(e) => setDraft({ ...draft, date_from: e.target.value || undefined })}
        />
        <TextField
          label="Date To"
          type="date"
          InputLabelProps={{ shrink: true }}
          sx={{ minWidth: 180 }}
          value={draft.date_to ?? ""}
          onChange={(e) => setDraft({ ...draft, date_to: e.target.value || undefined })}
        />
        <TextField select label="Shift" sx={{ minWidth: 140 }} value={draft.shift_id ?? ""} onChange={(e) => setDraft({ ...draft, shift_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.shifts.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              Shift {item.code}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Supervisor" sx={{ minWidth: 180 }} value={draft.supervisor_id ?? ""} onChange={(e) => setDraft({ ...draft, supervisor_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.supervisors.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Machine" sx={{ minWidth: 140 }} value={draft.machine_id ?? ""} onChange={(e) => setDraft({ ...draft, machine_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.machines.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.code}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Stoppage Reason" sx={{ minWidth: 220 }} value={draft.reason_id ?? ""} onChange={(e) => setDraft({ ...draft, reason_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.reasons.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="Search"
          sx={{ minWidth: 220 }}
          value={draft.search ?? ""}
          onChange={(e) => setDraft({ ...draft, search: e.target.value || undefined })}
        />
      </FilterBar>
      {list.isError ? <ErrorState message={apiErrorMessage(list.error)} /> : null}
      {list.isLoading ? (
        <LoadingState />
      ) : !list.data?.data.length ? (
        <EmptyState message="No stoppage records found for the selected filters." />
      ) : (
        <>
          <TableContainer sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {["Date", "Shift", "Supervisor", "Machine", "Reason", "Duration", "Details", "Remarks", "Created Time", "Actions"].map((col) => (
                    <TableCell key={col} sx={{ fontWeight: 700 }}>
                      {col}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {list.data.data.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>{formatDate(row.production_date)}</TableCell>
                    <TableCell>{row.shift.code}</TableCell>
                    <TableCell>{row.supervisor.name}</TableCell>
                    <TableCell>{row.machine.code}</TableCell>
                    <TableCell>{row.reason.name}</TableCell>
                    <TableCell>{formatDuration(row.duration_minutes)}</TableCell>
                    <TableCell>{row.details || "—"}</TableCell>
                    <TableCell>{row.remarks || "—"}</TableCell>
                    <TableCell>{formatDateTime(row.created_at)}</TableCell>
                    <TableCell>
                      <Button size="small" onClick={() => setView(row)}>
                        View
                      </Button>
                      {canMutate(user?.role, user?.supervisor_id, user?.id, row) ? (
                        <>
                          <Button size="small" onClick={() => setEdit({ ...row })}>
                            Edit
                          </Button>
                          <Button size="small" color="error" onClick={() => setRemove(row)}>
                            Delete
                          </Button>
                        </>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={list.data.pagination.total}
            page={page}
            onPageChange={(_, next) => setPage(next)}
            rowsPerPage={pageSize}
            onRowsPerPageChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(0);
            }}
            rowsPerPageOptions={[25, 50, 100]}
          />
        </>
      )}
      <Dialog open={!!view} onClose={() => setView(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Stoppage record</DialogTitle>
        <DialogContent>
          {view ? (
            <Stack spacing={1} mt={1}>
              <div>Production Date: {formatDate(view.production_date)}</div>
              <div>Shift: {view.shift.code}</div>
              <div>Supervisor: {view.supervisor.name}</div>
              <div>Machine: {view.machine.code}</div>
              <div>Reason: {view.reason.name}</div>
              <div>Duration: {formatDuration(view.duration_minutes)}</div>
              <div>Details: {view.details || "—"}</div>
              <div>Remarks: {view.remarks || "—"}</div>
              <div>Created: {formatDateTime(view.created_at)}</div>
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setView(null)}>Close</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={!!edit} onClose={() => setEdit(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit stoppage</DialogTitle>
        <DialogContent>
          {edit ? (
            <Stack spacing={2} mt={1}>
              <TextField
                label="Duration (Minutes)"
                type="number"
                value={edit.duration_minutes}
                onChange={(e) => setEdit({ ...edit, duration_minutes: Number(e.target.value) })}
              />
              <TextField label="Details" multiline value={edit.details ?? ""} onChange={(e) => setEdit({ ...edit, details: e.target.value })} />
              <TextField label="Remarks" multiline value={edit.remarks ?? ""} onChange={(e) => setEdit({ ...edit, remarks: e.target.value })} />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEdit(null)}>Cancel</Button>
          <Button variant="contained" onClick={() => updateMutation.mutate()} disabled={updateMutation.isPending}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
      <ConfirmDialog
        open={!!remove}
        title="Delete stoppage record?"
        message={
          remove
            ? `Are you sure you want to delete this stoppage record? ${remove.machine.code}, ${remove.reason.name}, ${formatDuration(remove.duration_minutes)}, production date ${formatDate(remove.production_date)}.`
            : ""
        }
        onClose={() => setRemove(null)}
        onConfirm={() => remove && removeMutation.mutate(remove.id)}
        loading={removeMutation.isPending}
      />
    </>
  );
}
