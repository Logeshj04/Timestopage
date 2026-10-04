import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    primary: { main: "#1B3A4B" },
    secondary: { main: "#C45C26" },
    background: { default: "#F4F6F8", paper: "#FFFFFF" },
    error: { main: "#B42318" },
    warning: { main: "#B54708" },
    success: { main: "#067647" },
  },
  typography: {
    fontFamily: '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h4: { fontWeight: 700 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 650 },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600, minHeight: 42 },
      },
    },
    MuiTextField: {
      defaultProps: { size: "medium", fullWidth: true },
    },
  },
});
