import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { LoginPage } from "../../pages/LoginPage";
import { AuthProvider } from "./AuthContext";
import { SnackbarProvider } from "../../app/SnackbarProvider";

vi.mock("../../services/authService", () => ({
  authService: {
    login: vi.fn(),
    me: vi.fn(),
    logout: vi.fn(),
  },
}));

describe("LoginPage", () => {
  it("shows validation messages when submitted empty", async () => {
    render(
      <MemoryRouter>
        <SnackbarProvider>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </SnackbarProvider>
      </MemoryRouter>,
    );
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText("Please enter your username.")).toBeInTheDocument();
    expect(screen.getByText("Please enter your password.")).toBeInTheDocument();
  });
});
