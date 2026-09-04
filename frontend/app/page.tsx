"use client";

import { useRef, useState } from "react";

import {
  getReport,
  reportHtmlUrl,
  startRun,
  type SkillBenchReport,
  type SkillRecord,
  uploadSkill,
} from "@/lib/api";

type Phase = "idle" | "uploading" | "running" | "complete" | "error";

const chain = [
  ["01", "冻结配置", "固定 TestCase、Skill 与三种运行条件"],
  ["02", "运行取证", "保存输入、响应、Trace 与哈希指纹"],
  ["03", "原子判定", "Judge 只按断言和证据逐项判断"],
  ["04", "责任归因", "找到第一个真实偏离点后再决定计分"],
];

function verdictClass(verdict: string): string {
  return verdict === "PASS" ? "pass" : verdict === "FAIL" ? "fail" : "neutral";
}

export default function Home() {
  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [skill, setSkill] = useState<SkillRecord | null>(null);
  const [profile, setProfile] = useState<"offline-demo" | "development">("offline-demo");
  const [phase, setPhase] = useState<Phase>("idle");
  const [message, setMessage] = useState("无需 API Key，可先运行公开离线演示。");
  const [report, setReport] = useState<SkillBenchReport | null>(null);
  const [reportUrl, setReportUrl] = useState<string | null>(null);

  async function handleUpload() {
    if (!file) {
      fileInput.current?.click();
      setMessage("请选择包含 SKILL.md 的 ZIP 文件。");
      return;
    }
    try {
      setPhase("uploading");
      setMessage("正在安全校验并解析 Skill…");
      const record = await uploadSkill(file);
      setSkill(record);
      setPhase("idle");
      setMessage(`已载入 ${record.name}，现在可以开始评测。`);
    } catch (error) {
      setPhase("error");
      setMessage(error instanceof Error ? error.message : "Skill 上传失败");
    }
  }

  async function handleRun() {
    try {
      setPhase("running");
      setReport(null);
      setReportUrl(null);
      setMessage("正在执行 D0 / C_auto / C_forced 并构建证据链…");
      const run = await startRun(profile, skill?.skill_id);
      const result = await getReport(run.run_id);
      setReport(result);
      setReportUrl(reportHtmlUrl(run.run_id));
      setPhase("complete");
      setMessage("评测完成：证据校验、Judge 判定与责任归因均已生成。");
    } catch (error) {
      setPhase("error");
      setMessage(error instanceof Error ? error.message : "评测执行失败");
    }
  }

  const busy = phase === "uploading" || phase === "running";

  return (
    <main>
      <nav className="nav shell">
        <a className="brand" href="#top" aria-label="CodeReview SkillBench 首页">
          <span className="brand-mark">SB</span>
          <span>CodeReview <strong>SkillBench</strong></span>
        </a>
        <div className="nav-meta"><span className="status-dot" /> Private beta · v0.1</div>
      </nav>

      <section className="hero shell" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Evidence-backed Agent Skill Evaluation</p>
          <h1>不是“跑出一个分数”，<br /><em>而是证明这个分数可信。</em></h1>
          <p className="hero-lead">
            面向 Code Review Skill 的可复现评测工具。固定变量、保存证据、逐项判定，
            把每个失败定位到系统、资产、Skill 或模型结果。
          </p>
          <div className="hero-actions">
            <button className="primary" onClick={handleRun} disabled={busy}>
              {phase === "running" ? "正在生成证据…" : "立即运行公开演示"}
              <span aria-hidden>↗</span>
            </button>
            <a className="secondary" href="https://github.com/Li-Junming/CodeReview-SkillBench" target="_blank" rel="noreferrer">
              查看 GitHub
            </a>
          </div>
        </div>
        <div className="hero-panel" aria-label="评测决策示意">
          <div className="panel-top"><span>RUN / DEMO-CONCURRENCY-001</span><span className="live">EVIDENCE OK</span></div>
          <div className="code-line"><span>01</span><code>runner_ok</code><b>true</b></div>
          <div className="code-line"><span>02</span><code>asset_ok</code><b>true</b></div>
          <div className="code-line"><span>03</span><code>skill_loaded</code><b>true</b></div>
          <div className="code-line"><span>04</span><code>evidence_sufficient</code><b>true</b></div>
          <div className="decision"><small>QUALIFICATION</small><strong>SCORING ELIGIBLE</strong><p>只有完成责任归因，失败才进入分数。</p></div>
        </div>
      </section>

      <section className="chain-wrap">
        <div className="shell chain-grid">
          {chain.map(([number, title, detail]) => (
            <article key={number}>
              <span>{number}</span><h2>{title}</h2><p>{detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="workspace shell">
        <header className="section-head">
          <div><p className="eyebrow">Evaluation workspace</p><h2>用一个公开案例跑通完整链路</h2></div>
          <p>默认离线回放不调用商业模型，也不需要凭证；上传 Skill 后可切换开发评测配置。</p>
        </header>

        <div className="work-grid">
          <section className="control-card">
            <div className="card-title"><span>1</span><div><h3>选择 Skill</h3><p>ZIP 中必须且只能包含一个 UTF-8 `SKILL.md`</p></div></div>
            <input ref={fileInput} type="file" accept=".zip,application/zip" hidden onChange={(event) => {
              const selected = event.target.files?.[0] ?? null;
              setFile(selected); setSkill(null);
              if (selected) setMessage(`已选择 ${selected.name}`);
            }} />
            <button className="dropzone" onClick={() => fileInput.current?.click()} type="button">
              <span className="upload-icon">⇧</span>
              <strong>{file ? file.name : "选择 Skill ZIP"}</strong>
              <small>最大 2 MB · 自动拦截路径穿越与符号链接</small>
            </button>
            <button className="text-button" onClick={handleUpload} disabled={busy || !file}>
              {phase === "uploading" ? "正在校验…" : skill ? `✓ ${skill.name}` : "上传并校验 Skill"}
            </button>

            <div className="divider" />
            <div className="card-title"><span>2</span><div><h3>选择运行配置</h3><p>三种条件只改变 Skill 的可用方式</p></div></div>
            <div className="condition-row">
              {[["D0", "无 Skill"], ["C_auto", "自动触发"], ["C_forced", "强制加载"]].map(([name, detail]) => (
                <div className="condition" key={name}><strong>{name}</strong><small>{detail}</small></div>
              ))}
            </div>
            <label className="profile-label">评测配置
              <select value={profile} onChange={(event) => setProfile(event.target.value as "offline-demo" | "development")}>
                <option value="offline-demo">Public offline demo</option>
                <option value="development">Development · live provider</option>
              </select>
            </label>
            <button className="primary full" onClick={handleRun} disabled={busy}>
              {phase === "running" ? "执行与取证中…" : "开始评测"}
            </button>
            <p className={`message ${phase === "error" ? "error" : ""}`} aria-live="polite">{message}</p>
          </section>

          <section className="result-card">
            <div className="result-header"><div><span>LIVE RESULT</span><h3>证据链与责任归因</h3></div><span className={`phase phase-${phase}`}>{phase}</span></div>
            {!report ? (
              <div className="empty-state"><div className="radar"><span /></div><h4>等待评测运行</h4><p>运行后将在此展示 Qualification、Atomic Judge 和第一个真实偏离点。</p></div>
            ) : (
              <>
                <div className="metrics">
                  <div><small>有效运行</small><strong>{report.summary.eligible_runs}/{report.summary.total_runs}</strong></div>
                  <div><small>断言通过</small><strong>{report.summary.passed_runs}</strong></div>
                  <div><small>演示通过率</small><strong>{Math.round(report.summary.pass_rate * 100)}%</strong></div>
                </div>
                <div className="run-list">
                  {report.runs.map((run) => {
                    const verdict = run.judge_results[0]?.verdict ?? "INCONCLUSIVE";
                    return (
                      <article key={run.run_id}>
                        <div><span className="mono">{run.condition}</span><b className={`badge ${verdictClass(verdict)}`}>{verdict}</b></div>
                        <p>{run.response_summary}</p>
                        <footer><span>证据链 {run.evidence.integrity ? "✓" : "×"}</span><span>责任归因 {run.attribution.root_cause ?? "无失败"}</span></footer>
                      </article>
                    );
                  })}
                </div>
                {reportUrl && <a className="report-link" href={reportUrl} target="_blank" rel="noreferrer">打开完整可审计报告 <span>↗</span></a>}
                <p className="claim">{report.claim_boundary}</p>
              </>
            )}
          </section>
        </div>
      </section>

      <footer className="footer shell"><span>CodeReview SkillBench</span><p>先固定标准，再完整取证，最后确认责任并决定是否计分。</p></footer>
    </main>
  );
}

