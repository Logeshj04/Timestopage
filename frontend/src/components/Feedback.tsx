import { Alert, Box, CircularProgress, Typography } from "@mui/material";
import type { ReactNode } from "react";

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: ReactNode }) {
  return (
    <Box display="flex" justifyContent="space-between" alignItems={{ xs: "flex-start", md: "center" }} gap={2} mb={3} flexWrap="wrap">
      <Box>
        <Typography variant="h5">{title}</Typography>
        {subtitle ? (
          <Typography color="text.secondary" mt={0.5}>
            {subtitle}
          </Typography>
        ) : null}
      </Box>
      {actions}
    </Box>
  );
}

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <Box display="flex" alignItems="center" gap={2} py={6} justifyContent="center">
      <CircularProgress size={28} />
      <Typography>{label}</Typography>
    </Box>
  );
}

export function EmptyState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <Box py={6} textAlign="center">
      <Typography color="text.secondary" mb={2}>
        {message}
      </Typography>
      {action}
    </Box>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <Alert severity="error" sx={{ mb: 2 }}>
      {message}
    </Alert>
  );
}
