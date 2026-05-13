import { useState } from "react";
import axios from "axios";
import {
  RadarChart, Radar, PolarGrid,
  PolarAngleAxis, ResponsiveContainer, Tooltip
} from "recharts";

const API = "http://localhost:8000";

const severityColour = (s) =>
  s === "high" ? "#ef4444" : s === "medium" ? "#f59e0b" : "#22c55e";

const scoreColour = (score) =>
  score >= 70 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444";

// ── Score Ring ────────────────────────────────────────────
function ScoreRing({ score }) {
  const colour = scoreColour(score);
  return (
    <div style={{ textAlign: "center", margin: "24px 0" }}>
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="60"
          fill="none" stroke="#1e293b" strokeWidth="12" />
        <circle cx="70" cy="70" r="60"
          fill="none" stroke={colour} strokeWidth="12"
          strokeDasharray={`${(score / 100) * 377} 377`}
          strokeLinecap="round"
          transform="rotate(-90 70 70)" />
        <text x="70" y="68" textAnchor="middle"
          fill={colour} fontSize="28" fontWeight="bold">{score}</text>
        <text x="70" y="88" textAnchor="middle"
          fill="#94a3b8" fontSize="12">/ 100</text>
      </svg>
      <p style={{ color: "#94a3b8", marginTop: 4 }}>AI Readiness Score</p>
    </div>
  );
}

// ── Gap Card ──────────────────────────────────────────────
function GapCard({ gap }) {
  const colour = severityColour(gap.severity);
  return (
    <div style={{
      background: "#1e293b", borderRadius: 10,
      padding: "16px 20px", marginBottom: 12,
      borderLeft: `4px solid ${colour}`
    }}>
      <div style={{
        display: "flex", justifyContent: "space-between", marginBottom: 6
      }}>
        <span style={{ color: "#e2e8f0", fontWeight: 600, fontSize: 15 }}>
          {gap.dimension.replace(/_/g, " ").toUpperCase()}
        </span>
        <span style={{
          background: colour + "22", color: colour,
          borderRadius: 6, padding: "2px 10px",
          fontSize: 12, fontWeight: 700
        }}>{gap.severity.toUpperCase()}</span>
      </div>
      <p style={{ color: "#94a3b8", fontSize: 14, margin: "0 0 8px" }}>
        {gap.description}
      </p>
      <div style={{
        background: "#0f172a", borderRadius: 6,
        padding: "10px 14px", fontSize: 13, color: "#38bdf8"
      }}>
        💡 {gap.suggested_fix}
      </div>
    </div>
  );
}

// ── Radar Chart ───────────────────────────────────────────
function RadarView({ report }) {
  const dimensions = [
    "query_coverage", "policy_clarity",
    "hallucination_risk", "answer_consistency", "persona_coverage"
  ];
  const gapMap = {};
  report.gaps.forEach(g => { gapMap[g.dimension] = g.severity; });

  const data = dimensions.map(d => ({
    subject: d.replace(/_/g, " "),
    score: gapMap[d] === "high" ? 30
         : gapMap[d] === "medium" ? 60
         : 90,
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data}>
        <PolarGrid stroke="#334155" />
        <PolarAngleAxis dataKey="subject"
          tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Radar dataKey="score" stroke="#38bdf8"
          fill="#38bdf8" fillOpacity={0.2} />
        <Tooltip
          contentStyle={{ background: "#1e293b", border: "none" }}
          labelStyle={{ color: "#e2e8f0" }} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

// ── Fixes Tab ─────────────────────────────────────────────
function FixesTab({ productId }) {
  const [fixes, setFixes]       = useState(null);
  const [loading, setLoading]   = useState(false);
  const [expanded, setExpanded] = useState({});

  const loadFixes = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/fixes/${productId}`);
      setFixes(res.data);
    } catch (e) {
      setFixes({ error: "Failed to generate fixes." });
    }
    setLoading(false);
  };

  if (!fixes && !loading) return (
    <div style={{
      background: "#1e293b", borderRadius: 12,
      padding: 32, textAlign: "center"
    }}>
      <p style={{ color: "#94a3b8", marginBottom: 16 }}>
        Generate AI-powered rewrites for every gap found in this product.
      </p>
      <button onClick={loadFixes} style={{
        padding: "10px 28px", borderRadius: 8, border: "none",
        background: "#6366f1", color: "#fff",
        fontWeight: 700, fontSize: 14, cursor: "pointer"
      }}>
        ✍️ Generate Copy Fixes
      </button>
    </div>
  );

  if (loading) return (
    <div style={{
      background: "#1e293b", borderRadius: 12,
      padding: 48, textAlign: "center", color: "#94a3b8"
    }}>
      <div style={{ fontSize: 28, marginBottom: 12 }}>✍️</div>
      <p>Generating AI rewrites for each gap…</p>
      <p style={{ fontSize: 13 }}>Takes ~20 seconds</p>
    </div>
  );

  if (fixes?.error) return (
    <div style={{
      background: "#450a0a", border: "1px solid #ef4444",
      borderRadius: 10, padding: 16, color: "#fca5a5"
    }}>{fixes.error}</div>
  );

  return (
    <div>
      {fixes.fixes?.map((fix, i) => (
        <div key={i} style={{
          background: "#1e293b", borderRadius: 12,
          marginBottom: 16, overflow: "hidden",
          borderLeft: `4px solid ${severityColour(fix.severity)}`
        }}>
          {/* Header — click to expand */}
          <div
            onClick={() => setExpanded(e => ({ ...e, [i]: !e[i] }))}
            style={{
              padding: "16px 20px", cursor: "pointer",
              display: "flex", justifyContent: "space-between",
              alignItems: "center"
            }}>
            <div>
              <span style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 15 }}>
                {fix.dimension.replace(/_/g, " ").toUpperCase()}
              </span>
              <span style={{
                marginLeft: 12,
                background: severityColour(fix.severity) + "22",
                color: severityColour(fix.severity),
                borderRadius: 6, padding: "2px 10px",
                fontSize: 11, fontWeight: 700
              }}>{fix.severity.toUpperCase()}</span>
            </div>
            <span style={{ color: "#64748b", fontSize: 18 }}>
              {expanded[i] ? "▲" : "▼"}
            </span>
          </div>

          {/* Expanded before/after */}
          {expanded[i] && (
            <div style={{ padding: "0 20px 20px" }}>
              <p style={{ fontSize: 13, color: "#94a3b8", marginBottom: 16 }}>
                {fix.problem}
              </p>

              {/* Before */}
              <p style={{
                fontSize: 12, color: "#64748b",
                fontWeight: 700, marginBottom: 6
              }}>❌ ORIGINAL — what AI agents see now</p>
              <div style={{
                background: "#0f172a", borderRadius: 8,
                padding: 14, fontSize: 13, color: "#94a3b8",
                marginBottom: 16, whiteSpace: "pre-wrap",
                borderLeft: "3px solid #ef4444"
              }}>
                {fix.original_content || "Empty — nothing here currently"}
              </div>

              {/* After */}
              <p style={{
                fontSize: 12, color: "#64748b",
                fontWeight: 700, marginBottom: 6
              }}>✅ AI-GENERATED REWRITE — optimised for AI agents</p>
              <div style={{
                background: "#0f172a", borderRadius: 8,
                padding: 14, fontSize: 13, color: "#e2e8f0",
                whiteSpace: "pre-wrap",
                borderLeft: "3px solid #22c55e"
              }}>
                {fix.suggested_fix}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────
export default function App() {
  const [productId, setProductId] = useState("001");
  const [report, setReport]       = useState(null);
  const [product, setProduct]     = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [activeTab, setActiveTab] = useState("gaps");

  const analyse = async () => {
    setLoading(true);
    setError(null);
    setReport(null);
    setProduct(null);
    try {
      const [rep, prod] = await Promise.all([
        axios.get(`${API}/analyse/${productId}`),
        axios.get(`${API}/product/${productId}`),
      ]);
      setReport(rep.data);
      setProduct(prod.data);
      setActiveTab("gaps");
    } catch (e) {
      setError("Analysis failed. Is the backend running on port 8000?");
    }
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh", background: "#0f172a",
      color: "#e2e8f0", fontFamily: "system-ui, sans-serif"
    }}>

      {/* Header */}
      <div style={{
        background: "#1e293b", padding: "16px 32px",
        borderBottom: "1px solid #334155",
        display: "flex", alignItems: "center", gap: 12
      }}>
        <span style={{ fontSize: 22, fontWeight: 800, color: "#38bdf8" }}>
          ⚡ StoreSignal
        </span>
        <span style={{ color: "#475569", fontSize: 14 }}>
          AI Readiness Intelligence
        </span>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 24px" }}>

        {/* Product selector */}
        <div style={{
          background: "#1e293b", borderRadius: 12,
          padding: 24, marginBottom: 28
        }}>
          <p style={{ color: "#94a3b8", marginBottom: 12, fontSize: 14 }}>
            Select a product to analyse how AI shopping agents perceive it
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            {["001", "002", "003"].map(id => (
              <button key={id}
                onClick={() => { setProductId(id); setReport(null); }}
                style={{
                  padding: "8px 18px", borderRadius: 8, border: "none",
                  cursor: "pointer", fontWeight: 600, fontSize: 14,
                  background: productId === id ? "#38bdf8" : "#334155",
                  color: productId === id ? "#0f172a" : "#94a3b8",
                }}>
                Product {id}
              </button>
            ))}
            <button onClick={analyse} disabled={loading}
              style={{
                marginLeft: "auto", padding: "8px 24px",
                borderRadius: 8, border: "none", cursor: "pointer",
                fontWeight: 700, fontSize: 14,
                background: loading ? "#334155" : "#6366f1",
                color: loading ? "#64748b" : "#fff",
              }}>
              {loading ? "Analysing…" : "▶ Run Analysis"}
            </button>
          </div>
        </div>

        {/* Loading state */}
        {loading && (
          <div style={{
            textAlign: "center", padding: 48, color: "#94a3b8"
          }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>🤖</div>
            <p style={{ fontSize: 16, marginBottom: 8 }}>
              Simulating AI buyer personas…
            </p>
            <p style={{ fontSize: 13 }}>
              Running 12 questions × 4 personas + drift analysis.
              Takes ~30 seconds.
            </p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div style={{
            background: "#450a0a", border: "1px solid #ef4444",
            borderRadius: 10, padding: 16, color: "#fca5a5",
            marginBottom: 20
          }}>{error}</div>
        )}

        {/* Results */}
        {report && product && (
          <>
            {/* Product title */}
            <div style={{ marginBottom: 20 }}>
              <h2 style={{ margin: 0, fontSize: 20, color: "#f1f5f9" }}>
                {product.title}
              </h2>
              <p style={{ color: "#475569", fontSize: 13, marginTop: 4 }}>
                Product ID: {product.product_id}
              </p>
            </div>

            {/* Score + Radar */}
            <div style={{
              display: "grid", gridTemplateColumns: "1fr 1fr",
              gap: 20, marginBottom: 24
            }}>
              <div style={{
                background: "#1e293b", borderRadius: 12, padding: 20
              }}>
                <ScoreRing score={report.overall_score} />
                <div style={{
                  display: "flex", justifyContent: "space-around", marginTop: 8
                }}>
                  {[
                    { label: "Questions", value: report.simulation_results.length },
                    { label: "Gaps found", value: report.gaps.length },
                    {
                      label: "High severity",
                      value: report.gaps.filter(g => g.severity === "high").length
                    },
                  ].map(({ label, value }) => (
                    <div key={label} style={{ textAlign: "center" }}>
                      <div style={{
                        fontSize: 22, fontWeight: 700, color: "#f1f5f9"
                      }}>{value}</div>
                      <div style={{ fontSize: 11, color: "#64748b" }}>
                        {label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{
                background: "#1e293b", borderRadius: 12, padding: 20
              }}>
                <p style={{
                  fontSize: 13, color: "#64748b",
                  margin: "0 0 8px", fontWeight: 600
                }}>DIMENSION SCORES</p>
                <RadarView report={report} />
              </div>
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
              {["gaps", "fixes", "simulations"].map(tab => (
                <button key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: "8px 20px", borderRadius: 8,
                    border: "none", cursor: "pointer",
                    fontWeight: 600, fontSize: 14,
                    background: activeTab === tab ? "#334155" : "transparent",
                    color: activeTab === tab ? "#e2e8f0" : "#64748b",
                  }}>
                  {tab === "gaps" ? "🔍 Gaps & Fixes"
                   : tab === "fixes" ? "✍️ Rewritten Copy"
                   : "💬 Simulation Log"}
                </button>
              ))}
            </div>

            {/* Gaps tab */}
            {activeTab === "gaps" && (
              <div>
                {report.gaps.length === 0
                  ? <p style={{ color: "#22c55e" }}>
                      ✅ No significant gaps found!
                    </p>
                  : report.gaps.map((gap, i) =>
                      <GapCard key={i} gap={gap} />
                    )
                }
              </div>
            )}

            {/* Fixes tab */}
            {activeTab === "fixes" && (
              <FixesTab productId={productId} />
            )}

            {/* Simulation log tab */}
            {activeTab === "simulations" && (
              <div style={{
                background: "#1e293b", borderRadius: 12, padding: 20
              }}>
                <p style={{
                  fontSize: 13, color: "#64748b",
                  margin: "0 0 16px", fontWeight: 600
                }}>AI SIMULATION LOG</p>
                {report.simulation_results.map((r, i) => (
                  <div key={i} style={{
                    borderBottom: "1px solid #334155",
                    padding: "12px 0",
                  }}>
                    <div style={{
                      display: "flex", justifyContent: "space-between",
                      marginBottom: 4
                    }}>
                      <span style={{
                        fontSize: 11, color: "#6366f1",
                        fontWeight: 700, textTransform: "uppercase"
                      }}>{r.persona}</span>
                      <div style={{ display: "flex", gap: 8 }}>
                        <span style={{
                          fontSize: 11,
                          color: r.confidence >= 0.5 ? "#22c55e" : "#ef4444"
                        }}>
                          conf: {r.confidence.toFixed(1)}
                        </span>
                        {r.is_hallucination && (
                          <span style={{ fontSize: 11, color: "#f59e0b" }}>
                            ⚠️ hallucination
                          </span>
                        )}
                      </div>
                    </div>
                    <p style={{
                      fontSize: 13, color: "#94a3b8", margin: "0 0 4px"
                    }}>Q: {r.question}</p>
                    <p style={{
                      fontSize: 13, color: "#e2e8f0", margin: 0
                    }}>A: {r.answer}</p>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}