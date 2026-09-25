import type {
  ReliabilityReport,
} from "@/types/reliability";

import type {
  DeploymentState,
} from "@/types/deployment";

import type {
  SelfHealingState,
} from "@/types/selfHealing";


const API_BASE_URL =
  process.env
    .NEXT_PUBLIC_API_BASE_URL
  ??
  "http://127.0.0.1:8000";


async function fetchJson<T>(
  endpoint: string
): Promise<T> {

  const response =
    await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: "GET",

        headers: {
          Accept: "application/json",
        },

        cache: "no-store",
      }
    );


  if (!response.ok) {

    throw new Error(
      `${endpoint} failed: ${response.status}`
    );

  }


  return (
    await response.json()
  ) as T;
}


export async function fetchReliabilityReport():
  Promise<ReliabilityReport> {

  return fetchJson<ReliabilityReport>(
    "/api/reliability"
  );
}


export async function fetchDeploymentState():
  Promise<DeploymentState> {

  return fetchJson<DeploymentState>(
    "/api/deployment"
  );
}


export async function fetchSelfHealingState():
  Promise<SelfHealingState> {

  return fetchJson<SelfHealingState>(
    "/api/self-healing"
  );
}