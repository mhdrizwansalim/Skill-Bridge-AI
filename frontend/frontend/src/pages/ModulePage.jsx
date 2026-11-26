import { useEffect, useState } from "react";
import { AlertCircle, ArrowUpRight, FileText, FileUp, RefreshCw, Send, Sparkles } from "lucide-react";
import Panel from "../components/Panel";
import { api } from "../api";

function EmptyState({ title, message }) {
  return (
    <div className="empty-state">
      <div className="empty-icon"><FileText size={21} /></div>
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  );
}

function SkillBadges({ skills = [] }) {
  return <div className="badge-list">{skills.map((skill) => <span className="skill-badge" key={skill}>{skill}</span>)}</div>;
}

export default function ModulePage({ page, data, errors, onRefresh, onUpload, uploadState, onAskMentor, mentorState }) {
  const [question, setQuestion] = useState("");
  const [mentorAnswer, setMentorAnswer] = useState("");
  const [mentorError, setMentorError] = useState("");
  const [jobText, setJobText] = useState("");
  const [jobResult, setJobResult] = useState(null);
  const [jobError, setJobError] = useState("");
  const [jobLoading, setJobLoading] = useState(false);
  const [cvForm, setCvForm] = useState(data.cvProfile?.candidate || {});
  const [cvStatus, setCvStatus] = useState("");
  const [cvError, setCvError] = useState("");
  const [interviewRole, setInterviewRole] = useState("");
  const [interviewSession, setInterviewSession] = useState(null);
  const [answers, setAnswers] = useState({});
  const [interviewResult, setInterviewResult] = useState(null);
  const [interviewError, setInterviewError] = useState("");
  const [profileDraft, setProfileDraft] = useState({});
  const [profileStatus, setProfileStatus] = useState("");
  const [profileError, setProfileError] = useState("");
  const [jobHistory, setJobHistory] = useState([]);
  const [interviewHistory, setInterviewHistory] = useState([]);
  const [mentorHistory, setMentorHistory] = useState([]);
  const profile = data.profile?.candidate || {};
  const resumeCount = data.resumes?.total ?? data.resumes?.resumes?.length ?? 0;
  const candidateName = profile.personal_details?.full_name || profile.name || profile.full_name || "Candidate";
  const skills = profile.skills || profile.personal_details?.skills || [];

  useEffect(() => {
    if (data.cvProfile?.candidate) setCvForm(data.cvProfile.candidate);
  }, [data.cvProfile]);

  useEffect(() => {
    const personal = profile.personal_details || {};
    setProfileDraft({
      name: profile.name || profile.full_name || personal.full_name || "",
      email: profile.email || personal.email || "",
      phone: profile.phone || personal.phone || "",
      linkedin: profile.linkedin || personal.linkedin || "",
      github: profile.github || personal.github || "",
      summary: profile.summary || personal.professional_summary || "",
      skills: profile.skills || personal.skills || [],
      education: profile.education || "",
      experience: profile.experience || "",
      projects: profile.projects || "",
      certifications: profile.certifications || "",
      languages: profile.languages || ""
    });
  }, [profile.name, profile.full_name, profile.email, profile.phone, profile.linkedin, profile.github]);

  useEffect(() => {
    if (page === "Job Intelligence") {
      api.jobHistory().then((result) => setJobHistory(result.history || [])).catch(() => setJobHistory([]));
    }
    if (page === "Mock Interview") {
      api.interviewHistory().then((result) => setInterviewHistory(result.history || [])).catch(() => setInterviewHistory([]));
    }
    if (page === "AI Career Mentor") {
      api.mentorHistory().then((result) => setMentorHistory(result.history || [])).catch(() => setMentorHistory([]));
    }
  }, [page]);

  async function submitMentor(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setMentorError("");
    setMentorAnswer("");
    try {
      const result = await onAskMentor(question.trim());
      setMentorAnswer(result.answer || "");
      setQuestion("");
    } catch (error) {
      setMentorError(error.message || "Could not reach the AI mentor.");
    }
  }

  async function saveProfile(event) {
    event.preventDefault();
    setProfileError("");
    setProfileStatus("");
    try {
      await api.updateProfile(profileDraft, data.profile?.resume_id);
      setProfileStatus("Candidate profile saved.");
      await onRefresh();
    } catch (error) {
      setProfileError(error.message || "Could not save the candidate profile.");
    }
  }

  async function analyzeJob(event) {
    event.preventDefault();
    setJobError("");
    setJobResult(null);
    setJobLoading(true);
    try {
      const result = await api.analyzeJob(jobText);
      setJobResult(result.analysis);
    } catch (error) {
      setJobError(error.message || "Could not analyze the job description.");
    } finally {
      setJobLoading(false);
    }
  }

  async function generateCv(event) {
    event.preventDefault();
    setCvError("");
    setCvStatus("");
    try {
      await api.generateCv(cvForm);
      setCvStatus("CV generated successfully.");
      window.open(`${api.baseUrl}/cv/download`, "_blank", "noopener,noreferrer");
    } catch (error) {
      setCvError(error.message || "Could not generate the CV.");
    }
  }

  async function beginInterview(event) {
    event.preventDefault();
    setInterviewError("");
    setInterviewResult(null);
    setAnswers({});
    try {
      const result = await api.startInterview(interviewRole);
      setInterviewSession(result);
    } catch (error) {
      setInterviewError(error.message || "Could not start the interview.");
    }
  }

  async function submitInterview(event) {
    event.preventDefault();
    setInterviewError("");
    const payload = {
      target_role: interviewRole,
      answers: (interviewSession?.questions || []).map((item) => ({
        question: item.question,
        answer: answers[item.id] || ""
      }))
    };
    if (payload.answers.some((item) => item.answer.trim().length < 3)) {
      setInterviewError("Answer every question before submitting.");
      return;
    }
    try {
      const result = await api.submitInterview(payload);
      setInterviewResult(result);
    } catch (error) {
      setInterviewError(error.message || "Could not submit the interview.");
    }
  }


  return (
    <>
      <div className="page-intro">
        <div>
          <div className="section-kicker">SKILLBRIDGE WORKSPACE</div>
          <h1>{page}</h1>
          <p>Use live project data and practical tools from the SkillBridge platform.</p>
        </div>
        <button className="secondary-button" onClick={onRefresh}><RefreshCw size={15} /> Refresh data</button>
      </div>

      {page === "Resume Studio" && (
        <div className="module-content-grid">
          <Panel title="Upload a resume" subtitle="PDF files only · Maximum 10 MB">
            <label className="upload-zone">
              <input type="file" accept="application/pdf,.pdf" onChange={(event) => event.target.files?.[0] && onUpload(event.target.files[0])} />
              <span className="upload-icon"><FileUp size={22} /></span>
              <strong>Choose a PDF resume</strong>
              <span>Upload and parse a resume automatically</span>
            </label>
            {uploadState.message && <div className={`notice ${uploadState.error ? "warning" : "success"}`}>{uploadState.message}</div>}
          </Panel>
          <Panel title="Resume library" subtitle={`${resumeCount} saved profiles`}>
            {data.resumes?.resumes?.length ? (
              <div className="resume-list">
                {data.resumes.resumes.map((resume) => (
                  <div className="resume-row" key={resume.resume_id}>
                    <div className="resume-file-icon"><FileText size={17} /></div>
                    <div className="resume-row-copy"><strong>{resume.candidate_name || resume.resume_id}</strong><span>{resume.email || resume.file_name}</span></div>
                    <span className="file-status">SAVED</span>
                  </div>
                ))}
              </div>
            ) : <EmptyState title="No resume profiles found" message="Upload a PDF to create a candidate profile." />}
          </Panel>
        </div>
      )}

      {page === "Candidate Profile" && (
        <div className="module-content-grid">
          <Panel title="Candidate details" subtitle="Latest parsed or saved profile">
            {resumeCount ? (
              <div className="detail-grid">
                <div><span>Name</span><strong>{candidateName}</strong></div>
                <div><span>Email</span><strong>{profile.email || "Not extracted"}</strong></div>
                <div><span>Phone</span><strong>{profile.phone || "Not extracted"}</strong></div>
                <div><span>LinkedIn</span><strong>{profile.linkedin || "Not extracted"}</strong></div>
                <div><span>GitHub</span><strong>{profile.github || "Not extracted"}</strong></div>
              </div>
            ) : <EmptyState title="No candidate profile" message="Upload a resume to begin." />}
          </Panel>
          <Panel title="Extracted skills" subtitle={`${skills.length} detected skills`}>
            {skills.length ? <SkillBadges skills={skills} /> : <EmptyState title="No skills extracted" message="Use Resume Studio to parse a PDF." />}
          </Panel>
          <Panel title="Edit candidate profile" subtitle="Update extracted details without inventing missing values" className="wide-panel">
            <form onSubmit={saveProfile} className="cv-form">
              {["name", "email", "phone", "linkedin", "github"].map((field) => (
                <label key={field}>
                  <span>{field[0].toUpperCase() + field.slice(1)}</span>
                  <input value={profileDraft[field] || ""} onChange={(event) => setProfileDraft({ ...profileDraft, [field]: event.target.value })} />
                </label>
              ))}
              {["summary", "education", "experience", "projects", "certifications", "languages"].map((field) => (
                <label className="cv-wide" key={field}>
                  <span>{field[0].toUpperCase() + field.slice(1)}</span>
                  <textarea rows={3} value={profileDraft[field] || ""} onChange={(event) => setProfileDraft({ ...profileDraft, [field]: event.target.value })} />
                </label>
              ))}
              <label className="cv-wide">
                <span>Skills (comma separated)</span>
                <input value={(profileDraft.skills || []).join(", ")} onChange={(event) => setProfileDraft({ ...profileDraft, skills: event.target.value.split(",").map((skill) => skill.trim()).filter(Boolean) })} />
              </label>
              <button className="primary-button cv-wide" type="submit">Save candidate profile</button>
            </form>
            {profileStatus && <div className="notice success">{profileStatus}</div>}
            {profileError && <div className="notice warning"><AlertCircle size={15} /> {profileError}</div>}
          </Panel>
          <Panel title="Professional summary" subtitle="Experience and education" className="wide-panel">
            {profile.summary || profile.education || profile.experience ? (
              <div className="text-sections">
                {profile.summary && <div><strong>Summary</strong><p>{profile.summary}</p></div>}
                {profile.education && <div><strong>Education</strong><p>{profile.education}</p></div>}
                {profile.experience && <div><strong>Experience</strong><p>{profile.experience}</p></div>}
                {profile.projects && <div><strong>Projects</strong><p>{profile.projects}</p></div>}
              </div>
            ) : <EmptyState title="No detailed profile text" message="Parsed PDF text may contain scanned or unavailable content." />}
          </Panel>
        </div>
      )}

      {page === "Career Paths" && (
        <div className="career-grid">
          {data.career?.recommendations?.length ? data.career.recommendations.map((career) => (
            <Panel title={career.career_title} key={career.career_title} action={<span className="panel-period">{career.match_percentage}% MATCH</span>}>
              <div className="match-progress"><span style={{ width: `${career.match_percentage}%` }} /></div>
              <strong>Matched skills</strong><SkillBadges skills={career.matched_skills} />
              <strong>Missing skills</strong><SkillBadges skills={career.missing_skills?.slice(0, 12)} />
              <p className="muted-copy">{career.interpretation}</p>
            </Panel>
          )) : (
            <EmptyState
              title="No career recommendations"
              message={errors.career || "Career recommendations will appear after profile analysis."}
            />
          )}
        </div>
      )}

      {page === "Skill Gap" && data.skillGap?.skill_gap_analysis ? (
        <div className="module-content-grid">
          <Panel title={data.skillGap.skill_gap_analysis.target_career} subtitle="Target career skill match">
            <div className="score-block"><strong>{data.skillGap.skill_gap_analysis.skill_match_percentage}%</strong><span>skill match</span></div>
            <div className="match-progress"><span style={{ width: `${data.skillGap.skill_gap_analysis.skill_match_percentage}%` }} /></div>
          </Panel>
          <Panel title="Matched skills" subtitle={`${data.skillGap.skill_gap_analysis.matched_skills?.length || 0} overlaps`}><SkillBadges skills={data.skillGap.skill_gap_analysis.matched_skills} /></Panel>
          <Panel title="Learning priorities" subtitle="Suggested sequence" className="wide-panel">
            {data.skillGap.skill_gap_analysis.suggested_learning_sequence?.map((skill, index) => <div className="sequence-row" key={skill}><b>{index + 1}</b><span>{skill}</span></div>)}
          </Panel>
        </div>
      ) : page === "Skill Gap" ? <Panel title="Skill-gap analysis"><EmptyState title="No skill-gap analysis" message={errors.skillGap || "Run career analysis and refresh."} /></Panel> : null}

      {page === "Job Intelligence" && (
        <div className="module-content-grid">
          <Panel title="Analyze a job description" subtitle="Paste role text for a compatibility report">
            <form onSubmit={analyzeJob} className="form-stack">
              <textarea value={jobText} onChange={(event) => setJobText(event.target.value)} rows={10} minLength={20} maxLength={50000} placeholder="Paste the job title, responsibilities, required skills and qualifications..." />
              <button className="primary-button" disabled={jobLoading || jobText.trim().length < 20}>{jobLoading ? "Analyzing…" : "Analyze job"} <ArrowUpRight size={15} /></button>
            </form>
            {jobError && <div className="notice warning"><AlertCircle size={15} /> {jobError}</div>}
          </Panel>
          {jobResult && <Panel title={jobResult.job_title} subtitle={`${jobResult.job_compatibility_percentage}% compatibility`} className="wide-panel">
            <div className="match-progress"><span style={{ width: `${jobResult.job_compatibility_percentage}%` }} /></div>
            <strong>Matched skills</strong><SkillBadges skills={jobResult.matched_skills} />
            <strong>Missing skills</strong><SkillBadges skills={jobResult.missing_skills} />
            <strong>Experience</strong><p>{jobResult.experience_requirements?.join("; ") || "Not specified"}</p>
            <strong>Education</strong><p>{jobResult.education_requirements?.join("; ") || "Not specified"}</p>
          </Panel>}
          <Panel title="Saved job analyses" subtitle={`${jobHistory.length} recent matches`} className="wide-panel">
            {jobHistory.length ? jobHistory.map((item) => (
              <div className="sequence-row" key={item.id}><b>{item.match_score ?? 0}%</b><span>{item.job_title}</span></div>
            )) : <EmptyState title="No saved analyses" message="Completed job analyses will appear here." />}
          </Panel>
        </div>
      )}

      {page === "CV Builder" && (
        <Panel title="Edit and generate CV" subtitle="No missing field is filled with invented information">
          <form onSubmit={generateCv} className="cv-form">
            {["name", "email", "phone", "linkedin", "github"].map((field) => (
              <label key={field}><span>{field[0].toUpperCase() + field.slice(1)}</span><input value={cvForm[field] || ""} onChange={(event) => setCvForm({ ...cvForm, [field]: event.target.value })} /></label>
            ))}
            {["summary", "education", "experience", "projects", "certifications", "achievements", "languages"].map((field) => (
              <label className="cv-wide" key={field}><span>{field[0].toUpperCase() + field.slice(1)}</span><textarea rows={3} value={cvForm[field] || ""} onChange={(event) => setCvForm({ ...cvForm, [field]: event.target.value })} /></label>
            ))}
            <button className="primary-button cv-wide" type="submit">Generate and download PDF</button>
          </form>
          {cvStatus && <div className="notice success">{cvStatus}</div>}
          {cvError && <div className="notice warning"><AlertCircle size={15} /> {cvError}</div>}
        </Panel>
      )}

      {page === "Mock Interview" && (
        <div className="module-content-grid">
          <Panel title="Start a mock interview" subtitle="Questions are generated locally from the target role">
            <form onSubmit={beginInterview} className="form-stack">
              <label><span>Target role</span><input value={interviewRole} onChange={(event) => setInterviewRole(event.target.value)} minLength={2} maxLength={200} placeholder="e.g. Data Scientist" required /></label>
              <button className="primary-button" disabled={interviewRole.trim().length < 2}>Start interview</button>
            </form>
            {interviewError && <div className="notice warning"><AlertCircle size={15} /> {interviewError}</div>}
          </Panel>
          {interviewSession && (
            <Panel title="Interview answers" subtitle={interviewSession.target_role} className="wide-panel">
              <form onSubmit={submitInterview} className="form-stack">
                {interviewSession.questions.map((item) => (
                  <label key={item.id}><span>{item.id}. {item.question}</span><textarea rows={4} value={answers[item.id] || ""} onChange={(event) => setAnswers({ ...answers, [item.id]: event.target.value })} /></label>
                ))}
                <button className="primary-button" type="submit">Submit for local evaluation</button>
              </form>
            </Panel>
          )}
          {interviewResult && (
            <Panel title="Interview report" subtitle={`${interviewResult.performance_level} · ${interviewResult.average_score}%`} className="wide-panel">
              {interviewResult.evaluations.map((item, index) => (
                <div className="interview-result" key={item.question}>
                  <strong>{index + 1}. {item.question}</strong>
                  <p>Score: {item.evaluation.score}/100</p>
                  <p>{item.evaluation.feedback.join(" ")}</p>
                </div>
              ))}
            </Panel>
          )}
          <Panel title="Saved interview reports" subtitle={`${interviewHistory.length} recent reports`} className="wide-panel">
            {interviewHistory.length ? interviewHistory.map((item) => (
              <div className="sequence-row" key={item.id}><b>{item.average_score ?? 0}%</b><span>{item.target_role} · {item.performance_level}</span></div>
            )) : <EmptyState title="No saved interviews" message="Submitted mock interviews will appear here." />}
          </Panel>
        </div>
      )}

      {page === "AI Career Mentor" && (
        <div className="mentor-layout">
          <Panel title="Talk to your career mentor" subtitle="Grounded responses require the configured Ollama service">
            <div className="mentor-welcome"><div className="mentor-orb"><Sparkles size={25} /></div><div><strong>What would you like to work on?</strong><p>Ask about skills, career direction or interview preparation.</p></div></div>
            <form className="mentor-form" onSubmit={submitMentor}>
              <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask your career question..." rows={3} />
              <button className="primary-button" disabled={!question.trim() || mentorState.loading}>{mentorState.loading ? "Thinking…" : "Send question"} <Send size={15} /></button>
            </form>
            {mentorError && <div className="notice warning"><AlertCircle size={15} /> {mentorError}</div>}
            {mentorAnswer && <div className="mentor-answer"><strong>SkillBridge Mentor</strong><p>{mentorAnswer}</p></div>}
          </Panel>
            <Panel title="Recent mentor conversations" subtitle={`${mentorHistory.length} saved conversations`}>
              {mentorHistory.length ? mentorHistory.slice(-5).reverse().map((item) => (
                <div className="mentor-tip" key={item.id}><b>{item.question}</b><p>{item.answer}</p></div>
              )) : <EmptyState title="No conversation history" message="Mentor conversations will appear here after a successful answer." />}
            </Panel>
        </div>
      )}

      {page === "Settings" && (
        <Panel title="Connection details" subtitle="Local development environment">
          <div className="settings-list">
            <div><span>Frontend</span><strong>Vite · localhost:5173</strong></div>
            <div><span>Backend API</span><strong>{api.baseUrl}</strong></div>
            <div><span>Database</span><strong>SQLite · database/skillbridge.db</strong></div>
            <div><span>AI mentor</span><strong>Ollama (configured in backend)</strong></div>
          </div>
        </Panel>
      )}
    </>
  );
}
