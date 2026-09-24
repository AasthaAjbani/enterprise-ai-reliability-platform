import type {
  ReliabilityReport,
} from "@/types/reliability";

import type {
  DeploymentStatus,
} from "@/types/deployment";

import type {
  SelfHealingStatus,
} from "@/types/selfHealing";


const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL
  ??
  "http://127.0.0.1:8000";


// =========================================================
// GENERIC REQUEST HELPER
// =========================================================

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
      `API request failed: `
      +
      `${response.status} `
      +
      `${response.statusText}`
    );

  }


  return response.json();
}


// =========================================================
// RELIABILITY
// =========================================================

export async function fetchReliabilityReport():
Promise<ReliabilityReport> {

  return fetchJson<ReliabilityReport>(
    "/api/reliability"
  );

}


// =========================================================
// DEPLOYMENT
// =========================================================

export async function fetchDeploymentStatus():
Promise<DeploymentStatus> {

  return fetchJson<DeploymentStatus>(
    "/api/deployment"
  );

}


// =========================================================
// SELF HEALING
// =========================================================

export async function fetchSelfHealingStatus():
Promise<SelfHealingStatus> {

  return fetchJson<SelfHealingStatus>(
    "/api/self-healing"
  );

}


// =========================================================
// BASE URL
// =========================================================

export {
  API_BASE_URL,
};