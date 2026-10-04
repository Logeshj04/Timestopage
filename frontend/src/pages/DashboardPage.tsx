import { Box, Button, MenuItem, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartCard } from "../components/ChartCard";
import { EmptyState, ErrorState, LoadingState, PageHeader } from "../components/Feedback";
import { FilterBar } from "../components/FilterBar";
import { KpiCard } from "../components/KpiCard";
import { apiErrorMessage } from "../services/api/client";
import { dashboardService } from "../services/dashboardService";
import { masterDataService } from "../services/masterDataService";
import type { ReportFilters } from "../types";
import { formatDate, formatDuration, relativeTime, todayProductionDateInput } from "../utils/datetime";

const COLORS = ["#1B3A4B", "#C45C26", "#2F4858", "#4C6A7D", "#8C5A3C", "#6B7C85"];

function rangePreset(kind: string): ReportFilters {
  const today = todayProductionDateInput();
  const date = new Date(`${today}T00:00:00`);
  if (kind === "today") return { date_from: today, date_to: today };
  if (kind === "yesterday") {
    date.setDate(date.getDate() - 1);
    const value = date.toISOString().slice(0, 10);
    return { date_from: value, date_to: value };
  }
  if (kind === "week") {
    const start = new Date(date);
    start.setDate(date.getDate() - 6);
    return { date_from: start.toISOString().slice(0, 10), date_to: today };
  }
  if (kind === "month") {
    const start = `${today.slice(0, 8)}01`;
    return { date_from: start, date_to: today };
  }
  return { date_from: today, date_to: today };
}

export function DashboardPage() {
  const today = todayProductionDateInput();
  const [draft, setDraft] = useState<ReportFilters>({ date_from: today, date_to: today });
  const [applied, setApplied] = useState<ReportFilters>({ date_from: today, date_to: today });

  const masters = useQuery({
    queryKey: ["masters"],
    queryFn: async () => ({
      supervisors: await masterDataService.supervisors(),
      machines: await masterDataService.machines(),
      shifts: await masterDataService.shifts(),
      reasons: await masterDataService.reasons(),
    }),
  });

  const summary = useQuery({
    queryKey: ["dashboard", applied],
    queryFn: () => dashboardService.summary(applied),
  });

  const activeCount = useMemo(
    () => Object.values(applied).filter((value) => value !== undefined && value !== "").length,
    [applied],
  );

  if (summary.isLoading) return <LoadingState label="Loading dashboard..." />;
  if (summary.isError) return <ErrorState message={apiErrorMessage(summary.error)} />;
  const data = summary.data!;

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle={`Current production date ${formatDate(data.kpis.current_production_date)} · Shift ${data.kpis.current_shift_code}. Totals are calculated from recorded stoppages only.`}
      />
      <Stack direction="row" gap={1} mb={2} flexWrap="wrap">
        {["today", "yesterday", "week", "month"].map((item) => (
          <Button
            key={item}
            size="small"
            variant="outlined"
            onClick={() => {
              const next = { ...draft, ...rangePreset(item) };
              setDraft(next);
              setApplied(next);
            }}
          >
            {item === "week" ? "This Week" : item === "month" ? "This Month" : item[0].toUpperCase() + item.slice(1)}
          </Button>
        ))}
      </Stack>
      <FilterBar
        activeCount={activeCount}
        onApply={() => setApplied(draft)}
        onClear={() => {
          const next = { date_from: today, date_to: today };
          setDraft(next);
          setApplied(next);
        }}
      >
        <TextField label="Date From" type="date" InputLabelProps={{ shrink: true }} value={draft.date_from ?? ""} onChange={(e) => setDraft({ ...draft, date_from: e.target.value })} />
        <TextField label="Date To" type="date" InputLabelProps={{ shrink: true }} value={draft.date_to ?? ""} onChange={(e) => setDraft({ ...draft, date_to: e.target.value })} />
        <TextField select label="Shift" sx={{ minWidth: 140 }} value={draft.shift_id ?? ""} onChange={(e) => setDraft({ ...draft, shift_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.shifts.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              Shift {item.code}
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
        <TextField select label="Supervisor" sx={{ minWidth: 180 }} value={draft.supervisor_id ?? ""} onChange={(e) => setDraft({ ...draft, supervisor_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.supervisors.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Reason" sx={{ minWidth: 220 }} value={draft.reason_id ?? ""} onChange={(e) => setDraft({ ...draft, reason_id: e.target.value || undefined })}>
          <MenuItem value="">All</MenuItem>
          {masters.data?.reasons.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </TextField>
      </FilterBar>

      <Box display="grid" gridTemplateColumns={{ xs: "1fr", sm: "1fr 1fr", md: "repeat(4, 1fr)" }} gap={2} mb={2}>
        <KpiCard label="Total Downtime" value={formatDuration(data.kpis.total_downtime_minutes)} hint="Selected filter period" />
        <KpiCard label="Current Shift Downtime" value={formatDuration(data.kpis.current_shift_downtime_minutes)} hint={`Shift ${data.kpis.current_shift_code}`} />
        <KpiCard label="Today's Downtime" value={formatDuration(data.kpis.today_downtime_minutes)} hint={formatDate(data.kpis.current_production_date)} />
        <KpiCard label="Total Stoppage Entries" value={String(data.kpis.total_entries)} />
      </Box>

      <Box display="grid" gridTemplateColumns={{ xs: "1fr", md: "1fr 1fr" }} gap={2} mb={2}>
        <ChartCard title="Machine-wise downtime">
            {data.machines.length ? (
              <ResponsiveContainer>
                <BarChart data={data.machines.slice(0, 12)} layout="vertical" margin={{ left: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" width={60} />
                  <Tooltip formatter={(value) => [`${value} min`, "Downtime"]} />
                  <Bar dataKey="downtime_minutes" fill="#1B3A4B" name="Downtime">
                    {data.machines.slice(0, 12).map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState message="No stoppage recorded for the selected filters." />
            )}
          </ChartCard>
        <ChartCard title="Reason-wise downtime">
            {data.reasons.length ? (
              <ResponsiveContainer>
                <BarChart data={data.reasons.slice(0, 10)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" hide />
                  <YAxis />
                  <Tooltip formatter={(value, _n, item) => [`${value} min`, item.payload.name]} />
                  <Bar dataKey="downtime_minutes" fill="#C45C26" name="Downtime" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState message="No stoppage recorded for the selected filters." />
            )}
          </ChartCard>
        <ChartCard title="Daily trend">
            <ResponsiveContainer>
              <LineChart data={data.daily_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="downtime_minutes" name="Downtime" stroke="#1B3A4B" />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        <ChartCard title="Shift comparison">
            <ResponsiveContainer>
              <BarChart data={data.shifts}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="downtime_minutes" fill="#2F4858" name="Downtime" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
      </Box>

      <Box display="grid" gridTemplateColumns={{ xs: "1fr", md: "7fr 5fr" }} gap={2}>
        <Box>
          <Typography variant="h6" mb={1}>
            Machine summary
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" mb={1}>
            A value of 0 means no stoppage recorded, not that the machine was running.
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Machine</TableCell>
                <TableCell>Downtime</TableCell>
                <TableCell>Entries</TableCell>
                <TableCell>Average Stoppage</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.machines.slice(0, 15).map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{formatDuration(row.downtime_minutes)}</TableCell>
                  <TableCell>{row.stoppage_count}</TableCell>
                  <TableCell>{formatDuration(row.average_minutes)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
        <Box>
          <Typography variant="h6" mb={1}>
            Top reasons
          </Typography>
          {data.reasons.slice(0, 8).map((row, index) => (
            <Typography key={row.id} mb={0.75}>
              {index + 1}. {row.name} — {formatDuration(row.downtime_minutes)}
            </Typography>
          ))}
          <Typography variant="h6" mt={3} mb={1}>
            Recent stoppages
          </Typography>
          {data.recent.length === 0 ? (
            <EmptyState message="No stoppage recorded yet." />
          ) : (
            data.recent.slice(0, 8).map((row) => (
              <Typography key={row.id} mb={1}>
                {row.machine.code} · {row.reason.name} · {formatDuration(row.duration_minutes)} · Shift {row.shift.code} · {row.supervisor.name} · {relativeTime(row.created_at)}
              </Typography>
            ))
          )}
          <Typography variant="caption" color="text.secondary">
            Charts and recent entries refresh automatically when stoppages are saved.
          </Typography>
        </Box>
      </Box>
    </>
  );
}
