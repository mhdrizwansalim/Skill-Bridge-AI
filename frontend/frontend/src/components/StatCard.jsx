import { ArrowUpRight } from "lucide-react";

export default function StatCard({ label, value, note, icon: Icon, tone = "violet" }) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <span className={`stat-icon ${tone}`}><Icon size={18} /></span>
        <span className="stat-trend"><ArrowUpRight size={13} /> Live data</span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      <div className="stat-note">{note}</div>
    </div>
  );
}
