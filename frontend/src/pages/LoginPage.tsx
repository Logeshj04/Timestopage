import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, Box, Button, Card, CardContent, TextField, Typography } from "@mui/material";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { branding } from "../config/branding";
import { useAuth } from "../features/auth/AuthContext";
import { apiErrorMessage } from "../services/api/client";

const schema = z.object({
  username: z.string().min(1, "Please enter your username."),
  password: z.string().min(1, "Please enter your password."),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  return (
    <Box minHeight="100vh" display="flex" alignItems="center" justifyContent="center" p={2} sx={{ background: "linear-gradient(180deg, #1B3A4B 0%, #2F4858 100%)" }}>
      <Card sx={{ width: "100%", maxWidth: 420 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="overline" color="secondary">
            {branding.companyName}
          </Typography>
          <Typography variant="h5" mb={1}>
            {branding.appName}
          </Typography>
          <Typography color="text.secondary" mb={3}>
            Sign in to record and review machine downtime.
          </Typography>
          {error ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : null}
          <Box
            component="form"
            onSubmit={handleSubmit(async (values) => {
              setError(null);
              try {
                await login(values.username, values.password);
                const to = (location.state as { from?: string } | null)?.from ?? "/dashboard";
                navigate(to, { replace: true });
              } catch (err) {
                setError(apiErrorMessage(err, "Invalid username or password."));
              }
            })}
          >
            <TextField label="Username" autoComplete="username" margin="normal" error={!!errors.username} helperText={errors.username?.message} {...register("username")} />
            <TextField
              label="Password"
              type="password"
              autoComplete="current-password"
              margin="normal"
              error={!!errors.password}
              helperText={errors.password?.message}
              {...register("password")}
            />
            <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }} disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
