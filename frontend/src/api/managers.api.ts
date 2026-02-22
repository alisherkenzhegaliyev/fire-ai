import client from "./client";
import type { Manager } from "../types/manager";

export async function fetchManagers(sessionId: string): Promise<Manager[]> {
  const response = await client.get<Manager[]>("/api/managers", {
    params: { session_id: sessionId },
  });
  return response.data;
}

export async function fetchManagersFromDb(): Promise<Manager[]> {
  const response = await client.get<Manager[]>("/api/managers/db");
  return response.data;
}
