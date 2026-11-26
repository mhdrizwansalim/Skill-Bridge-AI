const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof payload === "object" && payload?.detail
      ? payload.detail
      : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return payload;
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request("/health"),
  resumes: () => request("/candidate/resumes"),
  profile: (resumeId) => request(`/candidate/profile${resumeId ? `?resume_id=${encodeURIComponent(resumeId)}` : ""}`),
  career: () => request("/career/recommendations"),
  skillGap: () => request("/career/skill-gap"),
  jobs: () => request("/jobs/matches"),
  interview: () => request("/interview/report"),
  interviewHistory: () => request("/interview/history"),
  mentorHistory: () => request("/mentor/history"),
  jobHistory: () => request("/jobs/history"),
  updateProfile: (profile, resumeId) => request(
    `/candidate/profile${resumeId ? `/${encodeURIComponent(resumeId)}` : ""}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile)
    }
  ),
  startInterview: (targetRole) => request("/interview/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_role: targetRole })
  }),
  submitInterview: (payload) => request("/interview/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }),
  cvProfile: () => request("/cv/profile"),
  generateCv: (profile) => request("/cv/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile)
  }),
  analyzeJob: (text) => request("/jobs/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  }),
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/resume/upload", { method: "POST", body: formData });
  },
  askMentor: (question) => request("/mentor/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  })
};
