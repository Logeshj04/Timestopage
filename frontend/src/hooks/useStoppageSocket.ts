import { useEffect, useRef, useState } from "react";
import { getToken } from "../services/api/client";

export function useStoppageSocket(onEvent: () => void) {
  const [status, setStatus] = useState<"live" | "disconnected">("disconnected");
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    const wsUrl = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/api/ws";
    let ws: WebSocket | null = null;
    let closed = false;
    let attempt = 0;
    let timer: number | undefined;

    const connect = () => {
      ws = new WebSocket(`${wsUrl}?token=${encodeURIComponent(token)}`);
      ws.onopen = () => {
        attempt = 0;
        setStatus("live");
        onEventRef.current();
      };
      ws.onmessage = () => onEventRef.current();
      ws.onclose = () => {
        setStatus("disconnected");
        if (!closed) {
          attempt += 1;
          timer = window.setTimeout(connect, Math.min(15000, 1000 * 2 ** attempt));
        }
      };
      ws.onerror = () => ws?.close();
    };

    connect();
    return () => {
      closed = true;
      if (timer) window.clearTimeout(timer);
      ws?.close();
    };
  }, []);

  return status;
}
