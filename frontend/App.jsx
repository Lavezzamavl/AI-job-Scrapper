import { useState, useEffect, useCallback } from "react";
import JobList from "./JobList";
import JobDetail from "./JobDetail";
import StatsBar from "./StatsBar";
import Filters from "./Filters";
import "./App.css";

const API = "http://localhost:5000/api";

export default function App() {
  const [jobs, setJobs]           = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [pages, setPages]         = useState(1);
  const [selected, setSelected]   = useState(null);
  const [stats, setStats]         = useState(null);
  const [scraping, setScraping]   = useState(false);
  const [loading, setLoading]     = useState(false);
  const [filters, setFilters]     = useState({
    city: "All", type: "All", source: "All", search: ""
  });

  const fetchJobs = useCallback(async (f = filters, p = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        city: f.city, type: f.type, source: f.source,
        search: f.search, page: p
      });
      const res  = await fetch(`${API}/jobs?${params}`);
      const data = await res.json();
      setJobs(data.jobs);
      setTotal(data.total);
      setPage(data.page);
      setPages(data.pages);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStats = async () => {
    try {
      const res  = await fetch(`${API}/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {}
  };

  useEffect(() => {
    fetchJobs(filters, 1);
    fetchStats();
  }, []);

  const applyFilters = (newFilters) => {
    setFilters(newFilters);
    setSelected(null);
    fetchJobs(newFilters, 1);
  };

  const handleScrape = async () => {
    setScraping(true);
    await fetch(`${API}/scrape`, { method: "POST" });
    setTimeout(() => {
      fetchJobs(filters, 1);
      fetchStats();
      setScraping(false);
    }, 15000);
  };

  const handleSelect = async (job) => {
    const res  = await fetch(`${API}/jobs/${job.id}`);
    const data = await res.json();
    setSelected(data);
  };

  const handleUpdate = (updatedJob) => {
    setSelected(updatedJob);
    setJobs(prev => prev.map(j => j.id === updatedJob.id ? { ...j, ...updatedJob } : j));
    fetchStats();
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-ke">KE</span>
            <div>
              <div className="logo-title">Kazi Kenya</div>
              <div className="logo-sub">Entry Jobs · Internships · Junior Roles</div>
            </div>
          </div>
        </div>
        <div className="header-right">
          {stats && (
            <div className="header-stats">
              <span><strong>{stats.total}</strong> jobs</span>
              <span><strong>{stats.applied}</strong> applied</span>
              <span><strong>{stats.saved}</strong> saved</span>
            </div>
          )}
          <button className={`btn-scrape ${scraping ? "loading" : ""}`} onClick={handleScrape} disabled={scraping}>
            {scraping ? "Searching…" : "🔍 Find New Jobs"}
          </button>
        </div>
      </header>

      <StatsBar stats={stats} />

      <div className="main">
        <aside className="sidebar">
          <Filters filters={filters} onApply={applyFilters} />
        </aside>

        <section className="job-list-panel">
          <div className="list-header">
            <span className="result-count">{total} jobs found</span>
            {loading && <span className="loading-dot">Loading…</span>}
          </div>
          <JobList
            jobs={jobs}
            selected={selected}
            onSelect={handleSelect}
          />
          {pages > 1 && (
            <div className="pagination">
              {Array.from({ length: pages }, (_, i) => i + 1).map(p => (
                <button
                  key={p}
                  className={`page-btn ${p === page ? "active" : ""}`}
                  onClick={() => { setPage(p); fetchJobs(filters, p); }}
                >{p}</button>
              ))}
            </div>
          )}
        </section>

        <section className="detail-panel">
          {selected ? (
            <JobDetail job={selected} apiBase={API} onUpdate={handleUpdate} />
          ) : (
            <div className="detail-empty">
              <div className="empty-icon">📋</div>
              <p>Select a job to view details and generate your cover letter</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
