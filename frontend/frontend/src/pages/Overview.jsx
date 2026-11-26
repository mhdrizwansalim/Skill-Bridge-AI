import { useMemo } from "react";
import {
  ArrowRight, ArrowUpRight, BriefcaseBusiness, FileText, GraduationCap,
  Target, Sparkles, Clock3, CheckCircle2, CircleAlert, BrainCircuit
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis
} from "recharts";
import StatCard from "../components/StatCard";
import Panel from "../components/Panel";

const activityData = [
  { day: "Mon", progress: 18 }, { day: "Tue", progress: 28 },
  { day: "Wed", progress: 25 }, { day: "Thu", progress: 42 },
  { day: "Fri", progress: 38 }, { day: "Sat", progress: 57 },
  { day: "Sun", progress: 64 }
];

function getCandidateName(profile) {
  const candidate = profile?.candidate || {};
  const personal = candidate.personal_details || {};
  return personal.full_name || candidate.name || candidate.full_name || "Candidate";
}

export default function Overview({ data, loading, errors, onNavigate }) {
  const candidateName = getCandidateName(data.profile);
  const resumeCount = data.resumes?.total ?? data.resumes?.resumes?.length ?? 0;
  const jobReport = data.jobs?.job_analysis || {};
  const matches = Array.isArray(jobReport.job_matches)
    ? jobReport.job_matches
    : Array.isArray(jobReport.matches) ? jobReport.matches : [];
  const recommendations = data.career?.recommendations || [];
  const skillGap = data.skillGap?.skill_gap_analysis || [];

  const summaryCards = useMemo(() => [
    { label: "Resumes in library", value: resumeCount, note: "Saved candidate profiles", icon: FileText, tone: "violet" },
    { label: "Job matches", value: matches.length || "—", note: "From latest job analysis", icon: BriefcaseBusiness, tone: "blue" },
    { label: "Career pathways", value: recommendations.length || "—", note: "Recommended directions", icon: GraduationCap, tone: "mint" },
    { label: "Skills to develop", value: skillGap.length || "—", note: "Identified skill gaps", icon: Target, tone: "amber" }
  ], [resumeCount, matches.length, recommendations.length, skillGap.length]);

  const modules = [
    { title: "Resume Studio", description: "Upload, parse and strengthen your professional story.", icon: FileText, tag: "DOCUMENTS", page: "Resume Studio", tone: "violet" },
    { title: "Job Intelligence", description: "Understand role fit and discover relevant opportunities.", icon: BriefcaseBusiness, tag: "MATCHING", page: "Job Intelligence", tone: "blue" },
    { title: "Skill Gap Analysis", description: "See the skills between your profile and target roles.", icon: Target, tag: "GROWTH", page: "Skill Gap", tone: "amber" },
    { title: "AI Career Mentor", description: "Get practical guidance grounded in your career profile.", icon: BrainCircuit, tag: "AI ASSISTANT", page: "AI Career Mentor", tone: "mint" }
  ];

  return (
    <>
      <section className="welcome-banner">
        <div className="welcome-orb orb-one" /><div className="welcome-orb orb-two" />
        <div className="welcome-content">
          <div className="eyebrow"><span className="eyebrow-dot" /> YOUR CAREER, IN FOCUS</div>
          <h1>Good to see you, {candidateName.split(" ")[0]}<span className="wave">✦</span></h1>
          <p>Your next opportunity starts with a clearer picture of where you are — and where you can go.</p>
          <button className="primary-button" onClick={() => onNavigate("Resume Studio")}>Explore your profile <ArrowRight size={16} /></button>
        </div>
        <div className="welcome-art">
          <div className="art-ring ring-a" /><div className="art-ring ring-b" />
          <div className="art-core"><Sparkles size={30} /></div>
          <span className="art-chip chip-a">AI INSIGHTS</span><span className="art-chip chip-b">CAREER GROWTH</span>
        </div>
        <div className="welcome-footer"><span><span className="status-dot online" /> Career workspace ready</span><span>SKILLBRIDGE INTELLIGENCE <b>·</b> 01</span></div>
      </section>

      {errors.health && <div className="notice warning"><CircleAlert size={16} /> Could not reach the API. Start the FastAPI server to load your project data. <span>{errors.health}</span></div>}

      <div className="section-title-row">
        <div><div className="section-kicker">YOUR WORKSPACE</div><h2>Career overview</h2></div>
        <span className="data-caption">{loading ? "Syncing project data…" : "Connected project data where available"}</span>
      </div>

      <div className="stats-grid">
        {summaryCards.map((card) => <StatCard key={card.label} {...card} />)}
      </div>

      <div className="content-grid overview-grid">
        <Panel title="Your momentum" subtitle="A preview of your weekly career activity" action={<span className="panel-period">LAST 7 DAYS</span>}>
          <div className="chart-summary"><strong>Build your momentum</strong><span>Activity will appear as you use SkillBridge</span></div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}>
                <defs><linearGradient id="progressFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#8b75ff" stopOpacity={0.28} /><stop offset="100%" stopColor="#8b75ff" stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid stroke="#252a39" strokeDasharray="3 5" vertical={false} />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#737b91", fontSize: 11 }} dy={10} />
                <YAxis hide />
                <Tooltip contentStyle={{ background: "#171b29", border: "1px solid #30364a", borderRadius: 10, color: "#f5f5fb" }} />
                <Area type="monotone" dataKey="progress" stroke="#9a85ff" strokeWidth={2.5} fill="url(#progressFill)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-footnote"><span><span className="legend-dot" /> Illustrative activity trend</span><span>Connect more modules to build your timeline</span></div>
        </Panel>

        <Panel title="Career snapshot" subtitle="A quick look at your platform readiness">
          <div className="snapshot-score">
            <div className="score-ring"><div><strong>{resumeCount > 0 ? "✓" : "—"}</strong><small>{resumeCount > 0 ? "PROFILE" : "NO DATA"}</small></div></div>
            <div><strong>{resumeCount > 0 ? "Profile detected" : "Start with your profile"}</strong><p>{resumeCount > 0 ? "Your resume library is available to SkillBridge." : "Upload a resume to begin your career analysis."}</p></div>
          </div>
          <div className="snapshot-list">
            <div><span><CheckCircle2 size={15} /> Backend connection</span><b className={data.health ? "text-green" : "text-muted"}>{data.health ? "Online" : "Pending"}</b></div>
            <div><span><FileText size={15} /> Resume library</span><b>{resumeCount} saved</b></div>
            <div><span><Clock3 size={15} /> AI mentor</span><b>{errors.mentor === "not-checked" ? "Available on request" : "Ollama required"}</b></div>
          </div>
        </Panel>
      </div>

      <div className="section-title-row modules-title">
        <div><div className="section-kicker">THE SKILLBRIDGE SUITE</div><h2>Explore your tools</h2></div>
        <button className="text-button" onClick={() => onNavigate("Resume Studio")}>View workspace <ArrowUpRight size={15} /></button>
      </div>
      <div className="module-grid">
        {modules.map((module) => {
          const Icon = module.icon;
          return <button className="module-card" key={module.title} onClick={() => onNavigate(module.page)}>
            <div className="module-card-top"><span className={`module-icon ${module.tone}`}><Icon size={19} /></span><ArrowUpRight size={16} className="module-arrow" /></div>
            <span className="module-tag">{module.tag}</span><h3>{module.title}</h3><p>{module.description}</p>
            <span className="module-link">Open module <ArrowRight size={14} /></span>
          </button>;
        })}
      </div>
    </>
  );
}
