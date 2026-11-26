import { useCallback, useEffect, useState } from "react";
import { Menu, Search, CircleHelp } from "lucide-react";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Overview from "./pages/Overview";
import ModulePage from "./pages/ModulePage";
import { api } from "./api";

const initialData = {
  health: null, resumes: null, profile: null, career: null,
  skillGap: null, jobs: null, interview: null, cvProfile: null
};

export default function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [data, setData] = useState(initialData);
  const [errors, setErrors] = useState({ health: null, mentor: "not-checked" });
  const [loading, setLoading] = useState(false);
  const [uploadState, setUploadState] = useState({ message: "", error: false });
  const [mentorState, setMentorState] = useState({ loading: false });

  const refreshData = useCallback(async () => {
    setLoading(true);
    const tasks = [
      ["health", api.health],
      ["resumes", api.resumes],
      ["profile", api.profile],
      ["career", api.career],
      ["skillGap", api.skillGap],
      ["jobs", api.jobs],
      ["interview", api.interview],
      ["cvProfile", api.cvProfile]
    ];
    const results = await Promise.all(tasks.map(async ([key, loader]) => {
      try { return [key, await loader(), null]; }
      catch (error) { return [key, null, error.message || "Data not available"]; }
    }));
    const nextData = { ...initialData };
    const nextErrors = { mentor: "not-checked" };
    results.forEach(([key, value, error]) => {
      nextData[key] = value;
      if (error) nextErrors[key] = error;
    });
    setData(nextData);
    setErrors(nextErrors);
    setLoading(false);
  }, []);

  useEffect(() => { refreshData(); }, [refreshData]);

  async function uploadResume(file) {
    setUploadState({ message: "", error: false });
    try {
      const result = await api.uploadResume(file);
      setUploadState({ message: `Uploaded ${result.original_filename}. Saved as ${result.saved_filename}.`, error: false });
      await refreshData();
    } catch (error) {
      setUploadState({ message: error.message || "Resume upload failed.", error: true });
    }
  }

  async function askMentor(question) {
    setMentorState({ loading: true });
    try {
      return await api.askMentor(question);
    } finally {
      setMentorState({ loading: false });
    }
  }

  const isApiOnline = Boolean(data.health?.status === "healthy");
  const pageTitles = {
    "Overview": "Overview", "Resume Studio": "Resume Studio",
    "Candidate Profile": "Candidate Profile",
    "Job Intelligence": "Job Intelligence", "Skill Gap": "Skill Gap",
    "Career Paths": "Career Paths", "AI Career Mentor": "AI Career Mentor",
    "Mock Interview": "Mock Interview", "CV Builder": "CV Builder", "Settings": "Settings"
  };

  return (
    <div className="app-shell">
      <Sidebar active={activePage} onNavigate={setActivePage} open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} apiOnline={isApiOnline} />
      <main className="main-area">
        <Topbar title={pageTitles[activePage] || activePage} onMenu={() => setMobileNavOpen(true)} />
        <div className="page-content">
          {activePage === "Overview"
            ? <Overview data={data} loading={loading} errors={errors} onNavigate={setActivePage} />
            : <ModulePage page={activePage} data={data} errors={errors} onRefresh={refreshData} onUpload={uploadResume} uploadState={uploadState} onAskMentor={askMentor} mentorState={mentorState} />}
          <footer className="app-footer"><span>© 2026 SkillBridge by Zequa</span><span><CircleHelp size={13} /> Built to move your career forward</span></footer>
        </div>
      </main>
    </div>
  );
}
