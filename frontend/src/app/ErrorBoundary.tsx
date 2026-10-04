import { Component, type ErrorInfo, type ReactNode } from "react";
import { Box, Button, Typography } from "@mui/material";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error(error, info);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <Box p={4} textAlign="center">
          <Typography variant="h5" gutterBottom>
            Something went wrong
          </Typography>
          <Typography color="text.secondary" mb={2}>
            This section could not be displayed. You can continue using the rest of the application.
          </Typography>
          <Button variant="contained" onClick={() => this.setState({ hasError: false })}>
            Try again
          </Button>
        </Box>
      );
    }
    return this.props.children;
  }
}
