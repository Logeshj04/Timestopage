import { Card, CardContent, CardHeader } from "@mui/material";
import type { ReactNode } from "react";

export function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardHeader title={title} titleTypographyProps={{ variant: "h6" }} />
      <CardContent sx={{ height: 320 }}>{children}</CardContent>
    </Card>
  );
}
