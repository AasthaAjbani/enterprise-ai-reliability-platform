import type {
  ReliabilityReport,
} from "@/types/reliability";


const API_BASE_URL =
  process.env
    .NEXT_PUBLIC_API_BASE_URL
  ??
  "http://127.0.0.1:8000";


export async function fetchReliabilityReport():
  Promise<ReliabilityReport> {

  const response = await fetch(
    `${API_BASE_URL}/api/reliability`,
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
      `Reliability API failed: ${response.status}`
    );

  }


  const data =
    await response.json();


  return data as ReliabilityReport;
}