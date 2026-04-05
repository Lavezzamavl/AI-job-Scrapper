import { useState } from "react";

export default function JobDetail({ job, apiBase, onUpdate }) {
  const [tab, setTab]         = useState("cover");
  const [generating, setGen]  = useState(false);
  const [copied, setCopied]   = useState(false);
  const [profile, setProfile] = useState("");
  const [showProfile, setShowProfile] = useState(false);

  const generate = async () => {
    setGen(true);
    try {
      const res  = await fetch(`${apiBase}/jobs/${job.id}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile }),
      });
      const data = await res.json();
      onUpdate({ ...job, cover_letter: data.cover_letter, email_draft: data.email_draft });
      setTab("cover");
    } catch (e) {
      console.error(e);
    } finally {
      setGen(false);
    }
  };

  const markApplied = async () => {
    await fetch(`${apiBase}/jobs/${job.id}/apply`, { method: "POST" });
    onUpdate({ ...job, applied: 1 });
  };

  const toggleBookmark = async () => {
    const res  = await fetch(`${apiBase}/jobs/${job.id}/bookmark`, { method: "POST" });
    const data = await res.json();
    onUpdate({ ...job, bookmarked: data.bookmarked ? 1 : 0 });
  };

  const copyText = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const activeContent = tab === "cover" ? job.cover_letter : job.email_draft;

  return (
    <div className="detail">
      {/* Job header */}
      <div className="detail-header">
        <div>
          <h2 className="detail-title">{job.title}</h2>
          <div className="detail-company">{job.company}</div>
          <div className="detail-meta">
            <span>📍 {job.location}</span>
            {job.salary && <span>💰 {job.salary}</span>}
            <span className="detail-source">{job.source}</span>
          </div>
        </div>
        <div className="detail-actions">
          <button
            className={`btn-bookmark ${job.bookmarked ? "active" : ""}`}
            onClick={toggleBookmark}
            title="Save job"
          >
            {job.bookmarked ? "🔖" : "📌"}
          </button>
          <a href={job.url} target="_blank" rel="noreferrer" className="btn-view-job">
            View Job ↗
          </a>
          {!job.applied ? (
            <button className="btn-applied" onClick={markApplied}>
              Mark Applied ✓
            </button>
          ) : (
            <span className="applied-label">✓ Applied</span>
          )}
        </div>
      </div>

      {/* Description */}
      {job.description && (
        <div className="detail-desc">
          <div className="desc-label">Job description</div>
          <p className="desc-text">{job.description}</p>
        </div>
      )}

      {/* AI Section */}
      <div className="ai-section">
        <div className="ai-section-header">
          <span className="ai-label">✦ AI Application Materials</span>
          <button
            className="btn-profile-toggle"
            onClick={() => setShowProfile(!showProfile)}
          >
            {showProfile ? "Hide profile" : "Edit my profile"}
          </button>
        </div>

        {showProfile && (
          <div className="profile-editor">
            <div className="profile-label">Your profile (used to personalise the cover letter)</div>
            <textarea
              className="profile-textarea"
              value={profile}
              onChange={e => setProfile(e.target.value)}
              placeholder={`Name: Nathanael\nEducation: BSc Software Engineering (in progress)\nSkills: PHP, Laravel, Python, Django, JavaScript\nExperience: Task Management API (Laravel), E-commerce (Django)\nLooking for: Internship or junior developer role in Kenya`}
              rows={8}
            />
          </div>
        )}

        {!job.cover_letter ? (
          <div className="generate-prompt">
            <p>Generate a tailored cover letter and application email for this role using AI.</p>
            <button className="btn-generate" onClick={generate} disabled={generating}>
              {generating ? (
                <span className="gen-loading">
                  <span className="gen-dot" />Generating…
                </span>
              ) : "✦ Generate Cover Letter"}
            </button>
          </div>
        ) : (
          <div className="materials">
            <div className="mat-tabs">
              <button
                className={`mat-tab ${tab === "cover" ? "active" : ""}`}
                onClick={() => setTab("cover")}
              >Cover Letter</button>
              <button
                className={`mat-tab ${tab === "email" ? "active" : ""}`}
                onClick={() => setTab("email")}
              >Email Draft</button>
              <button className="btn-regen" onClick={generate} disabled={generating}>
                {generating ? "Regenerating…" : "↺ Regenerate"}
              </button>
            </div>
            <div className="mat-content">
              <pre className="mat-text">{activeContent}</pre>
            </div>
            <div className="mat-footer">
              <button className="btn-copy" onClick={() => copyText(activeContent)}>
                {copied ? "✓ Copied!" : "Copy to clipboard"}
              </button>
              <a href={job.url} target="_blank" rel="noreferrer" className="btn-apply-now">
                Apply now ↗
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
