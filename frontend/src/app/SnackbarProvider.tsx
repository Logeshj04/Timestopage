import { Alert, Snackbar } from "@mui/material";
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

type Severity = "success" | "error" | "warning" | "info";

const SnackbarContext = createContext<(message: string, severity?: Severity) => void>(() => undefined);

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<{ message: string; severity: Severity; open: boolean }>({
    message: "",
    severity: "info",
    open: false,
  });
  const notify = useCallback((message: string, severity: Severity = "info") => {
    setState({ message, severity, open: true });
  }, []);
  const value = useMemo(() => notify, [notify]);
  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <Snackbar open={state.open} autoHideDuration={4000} onClose={() => setState((prev) => ({ ...prev, open: false }))}>
        <Alert severity={state.severity} variant="filled" onClose={() => setState((prev) => ({ ...prev, open: false }))}>
          {state.message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export function useSnackbar() {
  return useContext(SnackbarContext);
}
