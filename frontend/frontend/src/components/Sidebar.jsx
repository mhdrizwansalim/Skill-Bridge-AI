import {
  Activity, ArrowUpRight, BriefcaseBusiness, BrainCircuit, ClipboardList, FileText,
  GraduationCap, LayoutDashboard, Mic2, Settings2, Sparkles, Target, UserRound, X
} from "lucide-react";

const navigation = [
  { label: "Overview", icon: LayoutDashboard, section: "Workspace" },
  { label: "Resume Studio", icon: FileText, section: "Workspace" },
  { label: "Candidate Profile", icon: UserRound, section: "Workspace" },
  { label: "Job Intelligence", icon: BriefcaseBusiness, section: "Workspace" },
  { label: "Skill Gap", icon: Target, section: "Workspace" },
  { label: "Career Paths", icon: GraduationCap, section: "Workspace" },
  { label: "CV Builder", icon: ClipboardList, section: "Workspace" },
  { label: "AI Career Mentor", icon: BrainCircuit, section: "AI tools" },
  { label: "Mock Interview", icon: Mic2, section: "AI tools" }
];

export default function Sidebar({ active, onNavigate, open, onClose, apiOnline }) {
  return (
    <>
      {open && <button className="mobile-scrim" aria-label="Close navigation" onClick={onClose} />}
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <div className="brand-mark"><Sparkles size={19} /></div>
          <div className="brand-copy">
            <strong>skillbridge<span>.</span></strong>
            <small>BY ZEQUA</small>
          </div>
          <button className="icon-button mobile-close" onClick={onClose} aria-label="Close menu"><X size={18} /></button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-avatar">Z</div>
          <div><strong>Zequa Workspace</strong><small>Personal account</small></div>
          <ArrowUpRight size={15} className="muted-icon" />
        </div>

        {["Workspace", "AI tools"].map((section) => (
          <div className="nav-section" key={section}>
            <div className="nav-label">{section}</div>
            {navigation.filter((item) => item.section === section).map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  className={`nav-item ${active === item.label ? "active" : ""}`}
                  onClick={() => { onNavigate(item.label); onClose(); }}
                >
                  <Icon size={17} strokeWidth={1.8} />
                  <span>{item.label}</span>
                  {active === item.label && <span className="active-indicator" />}
                </button>
              );
            })}
          </div>
        ))}

        <div className="sidebar-bottom">
          <div className="api-status">
            <span className={`status-dot ${apiOnline ? "online" : "offline"}`} />
            <span>Backend {apiOnline ? "connected" : "not connected"}</span>
            <Activity size={14} className="muted-icon" />
          </div>
          <button className="nav-item settings-item" onClick={() => onNavigate("Settings")}>
            <Settings2 size={17} /><span>Settings</span>
          </button>
          <div className="profile-mini">
            <div className="profile-avatar">CW</div>
            <div className="profile-copy"><strong>Career workspace</strong><small>Personal profile</small></div>
            <span className="profile-menu">•••</span>
          </div>
        </div>
      </aside>
    </>
  );
}
