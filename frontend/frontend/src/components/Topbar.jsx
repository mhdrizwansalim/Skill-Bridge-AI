import { Bell, Menu, Search, Command } from "lucide-react";

export default function Topbar({ title, onMenu }) {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="icon-button menu-trigger" onClick={onMenu} aria-label="Open navigation"><Menu size={19} /></button>
        <div className="breadcrumb"><span>Workspace</span><b>/</b><strong>{title}</strong></div>
      </div>
      <div className="topbar-actions">
        <button className="search-trigger"><Search size={16} /><span>Search anything...</span><kbd><Command size={11} /> K</kbd></button>
        <button className="icon-button notification-button" aria-label="Notifications"><Bell size={18} /><i /></button>
        <div className="topbar-avatar">RS</div>
      </div>
    </header>
  );
}
