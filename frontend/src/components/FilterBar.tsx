import { Box, Button, Chip, Stack } from "@mui/material";
import type { ReactNode } from "react";

export function FilterBar({
  children,
  onApply,
  onClear,
  activeCount,
}: {
  children: ReactNode;
  onApply: () => void;
  onClear: () => void;
  activeCount: number;
}) {
  return (
    <Box mb={3}>
      <Stack direction="row" gap={2} flexWrap="wrap" alignItems="flex-end">
        {children}
        <Button variant="contained" onClick={onApply}>
          Apply Filters
        </Button>
        <Button onClick={onClear}>Clear All</Button>
        {activeCount > 0 ? <Chip color="primary" label={`${activeCount} active filter${activeCount === 1 ? "" : "s"}`} /> : null}
      </Stack>
    </Box>
  );
}
