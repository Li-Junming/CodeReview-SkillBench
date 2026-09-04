const API_BASE =
  process.env.NEXT_PUBLIC_SKILLBENCH_API ?? "http://127.0.0.1:8000";

export type SkillRecord = {
  skill_id: string;
  name: string;
  sha256: string;
  file_count: number;
};

export type RunRecord = {
  run_id: string;
  profile: string;
  status: "COMPLETED" | "FAILED";
  report_json: string;
  report_html: string;
};

export type ReportRun = {
  run_id: string;
  condition: "D0" | "C_auto" | "C_forced";
  response_summary: string;
  judge_results: Array<{ verdict: string; reason: string }>;
  qualification: { scoring_eligible: boolean; reason: string };
  attribution: { root_cause: string | null; first_deviation: string | null };
  evidence: { integrity: boolean };
};

export type SkillBenchReport = {
  report_type: string;
  claim_boundary: string;
  summary: {
    total_runs: number;
    eligible_runs: number;
    passed_runs: number;
    pass_rate: number;
  };
  runs: ReportRun[];
};

async function readJson<T>(response: Response): Promise<T> {
  const payload = await response.json();
  if (!response.ok) {
    const message =
      typeof payload?.detail === "string" ? payload.detail : "请求失败";
    throw new Error(message);
  }
  return payload as T;
}

export async function uploadSkill(file: File): Promise<SkillRecord> {
  const body = new FormData();
  body.append("file", file);
  return readJson<SkillRecord>(
    await fetch(`${API_BASE}/api/skills`, { method: "POST", body }),
  );
}

export async function startRun(
  profile: "offline-demo" | "development",
  skillId?: string,
): Promise<RunRecord> {
  return readJson<RunRecord>(
    await fetch(`${API_BASE}/api/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile, skill_id: skillId ?? null }),
    }),
  );
}

export async function getReport(runId: string): Promise<SkillBenchReport> {
  return readJson<SkillBenchReport>(
    await fetch(`${API_BASE}/api/runs/${runId}/report`, { cache: "no-store" }),
  );
}

export function reportHtmlUrl(runId: string): string {
  return `${API_BASE}/api/runs/${runId}/report?format=html`;
}

