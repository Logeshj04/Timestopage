import { Alert, Button, MenuItem, Stack, TextField, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PageHeader } from "../components/Feedback";
import { FilterBar } from "../components/FilterBar";
import { useSnackbar } from "../app/SnackbarProvider";
import { apiErrorMessage } from "../services/api/client";
import { reportService } from "../services/dashboardService";
import { masterDataService } from "../services/masterDataService";
import type { ReportFilters } from "../types";
import { todayProductionDateInput } from "../utils/datetime";

export function ReportsPage() {
  const notify = useSnackbar();
  const today = todayProductionDateInput();
  const [draft, setDraft] = useState<ReportFilters>({ date_from: today, date_to: today });
  const [applied, setApplied] = useState<ReportFilters>({ date_from: today, date_to: today });
  const [busy, setBusy] = useState<string | null>(null);

  const masters = useQuery({
    queryKey: ["masters"],
    queryFn: async () => ({
      supervisors: await masterDataService.supervisors(),
      machines: await masterDataService.machines(),
      shifts: await masterDataService.shifts(),
      reasons: await masterDataService.reasons(),
    }),
  });

  const activeCount = useMemo(
    () => Object.values(applied).filter((value) => value !== undefined && value !== "").length,
    [applied],
  );

  const summary = [
    applied.date_from && `From ${applied.date_from}`,
    applied.date_to && `to ${applied.date_to}`,
    applied.shift_id && "shift filtered",
    applied.machine_id && "machine filtered",
    applied.supervisor_id && "supervisor filtered",
    applied.reason_id && "reason filtered",
  ]
    .filter(Boolean)
    .join(", ");

  const run = async (kind: string) => {
    setBusy(kind);
    try {
      if (kind === "pdf") {
        await reportService.pdf(applied, "downtime-report.pdf");
      } else {
        await reportService.excel({ ...applied, report_type: kind }, `downtime-${kind}.xlsx`);
      }
      notify("Report downloaded.", "success");
    } catch (error) {
      notify(error instanceof Error ? error.message : apiErrorMessage(error, "Unable to generate the report."), "error");
    } finally {
      setBusy(null);
    }
  };

  return (
    <>
      <PageHeader
        title="Reports"
        subtitle="Excel is the primary export. The same filters are applied to every download."
      />
      <FilterBar activeCount={activeCount} onApply={() => setApplied(draft)} onClear={() => {
        const next = { date_from: today, date_to: today };
        setDraft(next);
        setApplied(next);
      }}>
        <TextField label="Date From" type="date" InputLabelProps={{ shrink: true }} value={draft.date_from ?? ""} onChange={(e) => setDraft({ ...draft, date_from: e.target.value })} />
        <TextField label="Date To" type="date" InputLabelProps={{ shrink: true }} value={draft.date_to ?? ""} onChange={(e) => setDraft({ ...draft, date_to: e.target.value })} />
        <TextField select label="Shift" sx={{ minWidth: 140 }} value={draft.shift_id ?? ""} onChange={(e) => setDraft({ ...draft, shift_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.shifts.map((item) => (
            <MenuItem key={item.id} value={item.id}>Shift {item.code}</MenuItem>
          ))}
        </TextField>
        <TextField select label="Machine" sx={{ minWidth: 140 }} value={draft.machine_id ?? ""} onChange={(e) => setDraft({ ...draft, machine_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.machines.map((item) => (
            <MenuItem key={item.id} value={item.id}>{item.code}</MenuItem>
          ))}
        </TextField>
        <TextField select label="Supervisor" sx={{ minWidth: 180 }} value={draft.supervisor_id ?? ""} onChange={(e) => setDraft({ ...draft, supervisor_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.supervisors.map((item) => (
            <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>
          ))}
        </TextField>
        <TextField select label="Reason" sx={{ minWidth: 220 }} value={draft.reason_id ?? ""} onChange={(e) => setDraft({ ...draft, reason_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.reasons.map((item) => (
            <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>
          ))}
        </TextField>
      </FilterBar>
      <Alert severity="info" sx={{ mb: 2 }}>
        Export criteria: {summary || "today's production date"}
      </Alert>
      <Typography mb={2}>If no matching records exist, the download is blocked instead of creating an empty file.</Typography>
      <Stack direction={{ xs: "column", sm: "row" }} gap={1}>
        <Button variant="contained" disabled={!!busy} onClick={() => run("raw")}>
          {busy === "raw" ? "Generating..." : "Download Raw Excel"}
        </Button>
        <Button variant="contained" disabled={!!busy} onClick={() => run("summary")}>
          {busy === "summary" ? "Generating..." : "Download Summary Excel"}
        </Button>
        <Button variant="contained" disabled={!!busy} onClick={() => run("complete")}>
          {busy === "complete" ? "Generating..." : "Download Complete Excel"}
        </Button>
        <Button variant="outlined" disabled={!!busy} onClick={() => run("pdf")}>
          {busy === "pdf" ? "Generating..." : "Download PDF"}
        </Button>
      </Stack>
    </>
  );
}
