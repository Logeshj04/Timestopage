import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, Box, Button, MenuItem, Stack, TextField } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef } from "react";
import { Controller, useForm } from "react-hook-form";
import { useBlocker } from "react-router-dom";
import { z } from "zod";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { LoadingState, PageHeader } from "../components/Feedback";
import { useAuth } from "../features/auth/AuthContext";
import { apiErrorMessage } from "../services/api/client";
import { masterDataService } from "../services/masterDataService";
import { stoppageService } from "../services/stoppageService";
import { currentShiftCode, todayProductionDateInput } from "../utils/datetime";
import { useSnackbar } from "../app/SnackbarProvider";

const schema = z.object({
  production_date: z.string().min(1, "Please select a production date."),
  shift_id: z.string().min(1, "Please select a shift."),
  supervisor_id: z.string().min(1, "Please select a supervisor."),
  machine_id: z.string().min(1, "Please select a machine."),
  stoppage_reason_id: z.string().min(1, "Please select a stoppage reason."),
  duration_minutes: z.coerce.number({ invalid_type_error: "Please enter the stoppage duration in minutes." }).int().gt(0, "Duration must be greater than 0 minutes."),
  details: z.string().optional(),
  remarks: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function StoppageEntryPage() {
  const notify = useSnackbar();
  const { user } = useAuth();
  const machineRef = useRef<HTMLInputElement>(null);
  const masters = useQuery({
    queryKey: ["masters-active"],
    queryFn: async () => {
      const [supervisors, machines, shifts, reasons] = await Promise.all([
        masterDataService.supervisors(true),
        masterDataService.machines(true),
        masterDataService.shifts(true),
        masterDataService.reasons(true),
      ]);
      return { supervisors, machines, shifts, reasons };
    },
  });

  const defaultShiftId = useMemo(() => {
    const code = currentShiftCode();
    return masters.data?.shifts.find((shift) => shift.code === code)?.id ?? "";
  }, [masters.data]);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      production_date: todayProductionDateInput(),
      shift_id: "",
      supervisor_id: user?.supervisor_id ?? "",
      machine_id: "",
      stoppage_reason_id: "",
      duration_minutes: undefined as unknown as number,
      details: "",
      remarks: "",
    },
  });

  useEffect(() => {
    if (defaultShiftId && !form.getValues("shift_id")) {
      form.setValue("shift_id", defaultShiftId);
    }
  }, [defaultShiftId, form]);

  const reasonId = form.watch("stoppage_reason_id");
  const selectedReason = masters.data?.reasons.find((item) => item.id === reasonId);
  const blocker = useBlocker(form.formState.isDirty && form.formState.isSubmitted === false);

  if (masters.isLoading) return <LoadingState label="Loading entry form..." />;

  const resetTransient = () => {
    form.reset({
      ...form.getValues(),
      machine_id: "",
      stoppage_reason_id: "",
      duration_minutes: undefined as unknown as number,
      details: "",
      remarks: "",
    });
    machineRef.current?.focus();
  };

  const save = async (addAnother: boolean) => {
    const values = schema.parse(form.getValues());
    await stoppageService.create({
      ...values,
      details: selectedReason?.requires_details ? values.details || null : values.details || null,
      remarks: values.remarks || null,
    });
    notify("Stoppage record saved successfully.", "success");
    if (addAnother) resetTransient();
    else {
      form.reset({
        production_date: values.production_date,
        shift_id: values.shift_id,
        supervisor_id: values.supervisor_id,
        machine_id: "",
        stoppage_reason_id: "",
        duration_minutes: undefined as unknown as number,
        details: "",
        remarks: "",
      });
    }
  };

  return (
    <>
      <PageHeader
        title="Stoppage Entry"
        subtitle="Each save creates a separate stoppage event. Repeated reasons are stored as new records."
      />
      {selectedReason?.notes ? <Alert severity="info" sx={{ mb: 2 }}>{selectedReason.notes}</Alert> : null}
      <Box
        component="form"
        onSubmit={form.handleSubmit(async () => {
          try {
            await save(false);
          } catch (error) {
            notify(apiErrorMessage(error, "Unable to save the record. Please try again."), "error");
          }
        })}
        noValidate
      >
        <Stack spacing={2} maxWidth={720}>
          <TextField
            label="Production Date"
            type="date"
            InputLabelProps={{ shrink: true }}
            error={!!form.formState.errors.production_date}
            helperText={form.formState.errors.production_date?.message}
            {...form.register("production_date")}
          />
          <TextField select label="Shift" error={!!form.formState.errors.shift_id} helperText={form.formState.errors.shift_id?.message} {...form.register("shift_id")}>
            {masters.data?.shifts.map((shift) => (
              <MenuItem key={shift.id} value={shift.id}>
                Shift {shift.code}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Supervisor"
            error={!!form.formState.errors.supervisor_id}
            helperText={form.formState.errors.supervisor_id?.message || "Shared supervisor logins must still select the person on shift."}
            {...form.register("supervisor_id")}
          >
            {masters.data?.supervisors.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Machine"
            inputRef={machineRef}
            error={!!form.formState.errors.machine_id}
            helperText={form.formState.errors.machine_id?.message}
            {...form.register("machine_id")}
          >
            {masters.data?.machines.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.code}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Stoppage Reason"
            error={!!form.formState.errors.stoppage_reason_id}
            helperText={form.formState.errors.stoppage_reason_id?.message}
            {...form.register("stoppage_reason_id")}
          >
            {masters.data?.reasons.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))}
          </TextField>
          <Controller
            control={form.control}
            name="duration_minutes"
            render={({ field, fieldState }) => (
              <TextField
                label="Duration (Minutes)"
                type="number"
                inputProps={{ min: 1, inputMode: "numeric" }}
                error={!!fieldState.error}
                helperText={fieldState.error?.message}
                value={field.value ?? ""}
                onChange={(event) => field.onChange(event.target.value === "" ? undefined : Number(event.target.value))}
              />
            )}
          />
          {selectedReason?.requires_details ? (
            <TextField
              label={selectedReason.details_label || "Details"}
              multiline
              minRows={2}
              {...form.register("details")}
            />
          ) : null}
          <TextField label="Remarks" multiline minRows={2} {...form.register("remarks")} />
          <Stack direction={{ xs: "column", sm: "row" }} gap={1}>
            <Button type="submit" variant="contained" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting ? "Saving..." : "Save"}
            </Button>
            <Button
              variant="outlined"
              disabled={form.formState.isSubmitting}
              onClick={form.handleSubmit(async () => {
                try {
                  await save(true);
                } catch (error) {
                  notify(apiErrorMessage(error, "Unable to save the record. Please try again."), "error");
                }
              })}
            >
              Save & Add Another
            </Button>
            <Button
              color="inherit"
              onClick={() =>
                form.reset({
                  production_date: form.getValues("production_date"),
                  shift_id: form.getValues("shift_id"),
                  supervisor_id: form.getValues("supervisor_id"),
                  machine_id: "",
                  stoppage_reason_id: "",
                  duration_minutes: undefined as unknown as number,
                  details: "",
                  remarks: "",
                })
              }
            >
              Reset
            </Button>
          </Stack>
        </Stack>
      </Box>
      <ConfirmDialog
        open={blocker.state === "blocked"}
        title="Leave this page?"
        message="You have unsaved stoppage details. Leave anyway?"
        confirmLabel="Leave"
        onClose={() => blocker.reset?.()}
        onConfirm={() => blocker.proceed?.()}
      />
    </>
  );
}
