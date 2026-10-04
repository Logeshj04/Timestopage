import { format, parseISO } from "date-fns";
import { formatInTimeZone, toZonedTime } from "date-fns-tz";

export const APP_TZ = "Asia/Kolkata";

export function todayProductionDateInput(now = new Date()): string {
  const zoned = toZonedTime(now, APP_TZ);
  const hour = zoned.getHours();
  if (hour < 6) {
    zoned.setDate(zoned.getDate() - 1);
  }
  return format(zoned, "yyyy-MM-dd");
}

export function currentShiftCode(now = new Date()): string {
  const zoned = toZonedTime(now, APP_TZ);
  const minutes = zoned.getHours() * 60 + zoned.getMinutes();
  if (minutes >= 6 * 60 && minutes < 14 * 60) return "A";
  if (minutes >= 14 * 60 && minutes < 22 * 60) return "B";
  return "C";
}

export function formatDate(value?: string | Date | null): string {
  if (!value) return "—";
  const date = typeof value === "string" ? parseISO(value) : value;
  return format(date, "dd MMM yyyy");
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "—";
  return formatInTimeZone(value, APP_TZ, "dd MMM yyyy hh:mm a");
}

export function formatDuration(minutes: number | string): string {
  return `${Number(minutes)} min`;
}

export function relativeTime(value: string): string {
  const then = new Date(value).getTime();
  const diff = Math.max(0, Date.now() - then);
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}
