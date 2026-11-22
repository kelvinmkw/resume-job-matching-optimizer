'use client';

import { FormEvent, useMemo, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
type Analysis = {
  scores: { b0_tfidf: number; b1_semantic: number | null; b2_semantic_skill: number; skill_overlap: number };
  shared_skills: string[];
  not_evidenced_skills: string[];
  caveat: string;
};
type RewriteResult = { available: boolean; draft: string | null; warning: string };

function percent(value: number | null | undefined) {
  return value == null ? 'Not enabled' : `${Math.round(value * 100)}%`;
}

export default function Home() {
  const [resume, setResume] = useState('');
  const [job, setJob] = useState('');
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [rewrite, setRewrite] = useState<RewriteResult | null>(null);
  const [busy, setBusy] = useState<'analyze' | 'rewrite' | null>(null);
  const [error, setError] = useState('');

  const canAnalyze = useMemo(() => resume.trim().length >= 10 && job.trim().length >= 10, [resume, job]);

  async function analyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy('analyze'); setError(''); setAnalysis(null); setRewrite(null);
    try {
      const response = await fetch(`${API}/api/analyze`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resume, job_text: job }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Analysis request failed. Is the API running?');
      setAnalysis(data);
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not reach the API.'); }
    finally { setBusy(null); }
  }

  async function requestRewrite() {
    if (!analysis) return;
    setBusy('rewrite'); setError(''); setRewrite(null);
    try {
      const response = await fetch(`${API}/api/rewrite`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resume, job_text: job, missing_skills: analysis.not_evidenced_skills, mode: 'gap_guided' }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Rewrite request failed.');
      setRewrite(data);
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not reach the rewrite service.'); }
    finally { setBusy(null); }
  }

  return (
    <main className="shell">
      <nav className="topbar"><a className="brand" href="#top"><span className="brand-mark">R</span> resume<span className="brand-muted">match</span></a><span className="nav-note">COMP7607 · NLP project</span></nav>
      <section className="hero" id="top">
        <div className="eyebrow"><span className="pulse" /> Evidence-led resume insights</div>
        <h1>Make your experience<br /><em>easier to see.</em></h1>
        <p className="hero-copy">Understand how your resume aligns with a role through transparent language signals—not an opaque pass/fail score.</p>
        <div className="hero-tags"><span>01 · Compare</span><span>02 · Find evidence gaps</span><span>03 · Refine with care</span></div>
      </section>

      <form className="workspace" onSubmit={analyze}>
        <div className="section-heading"><div><span className="step-label">YOUR MATERIALS</span><h2>Start with the role you want.</h2></div><span className="private-pill"><span>●</span> Not saved by this demo</span></div>
        <div className="input-grid">
          <label className="text-card"><span className="field-head"><span><b>01</b> YOUR RESUME</span><small>{resume.length.toLocaleString()} / 50,000</small></span><textarea maxLength={50000} minLength={10} required value={resume} onChange={e => setResume(e.target.value)} placeholder="Paste your resume text here. Include the experience, projects, and skills you want to highlight." /></label>
          <label className="text-card"><span className="field-head"><span><b>02</b> JOB DESCRIPTION</span><small>{job.length.toLocaleString()} / 50,000</small></span><textarea maxLength={50000} minLength={10} required value={job} onChange={e => setJob(e.target.value)} placeholder="Paste the job description here. We’ll compare the language and skill evidence in both texts." /></label>
        </div>
        {error && <div className="error-box" role="alert">{error}</div>}
        <div className="form-footer"><p>Similarity is a text signal, not a hiring probability.</p><button className="primary-button" disabled={!canAnalyze || busy !== null}>{busy === 'analyze' ? 'Analyzing…' : 'Analyze alignment'} <span>↗</span></button></div>
      </form>

      {analysis && <section className="results" aria-live="polite">
        <div className="section-heading result-heading"><div><span className="step-label">YOUR ANALYSIS</span><h2>A clearer view of your alignment.</h2></div><span className="result-caption">Signals are complementary, not verdicts.</span></div>
        <div className="score-grid">
          <article className="score-card"><span className="score-index">B0 · LEXICAL</span><strong>{percent(analysis.scores.b0_tfidf)}</strong><p>TF–IDF word overlap</p><div className="meter"><i style={{ width: percent(analysis.scores.b0_tfidf) }} /></div></article>
          <article className="score-card featured"><span className="score-index">B1 · SEMANTIC</span><strong>{percent(analysis.scores.b1_semantic)}</strong><p>Sentence-BERT meaning similarity</p><div className="meter"><i style={{ width: percent(analysis.scores.b1_semantic) === 'Not enabled' ? '0%' : percent(analysis.scores.b1_semantic) }} /></div>{analysis.scores.b1_semantic == null && <small className="muted">Enable optional model in backend settings</small>}</article>
          <article className="score-card"><span className="score-index">B2 · SKILL-AWARE</span><strong>{percent(analysis.scores.b2_semantic_skill)}</strong><p>Semantic signal + skill overlap</p><div className="meter"><i style={{ width: percent(analysis.scores.b2_semantic_skill) }} /></div></article>
        </div>
        <div className="evidence-grid">
          <article className="evidence-card"><div className="evidence-title"><span className="evidence-icon good">✓</span><div><h3>Skills found in both</h3><p>Evidence detected in the supplied text</p></div></div><div className="chips">{analysis.shared_skills.length ? analysis.shared_skills.map(skill => <span className="chip matched" key={skill}>{skill}</span>) : <span className="empty-note">No shared skills detected yet.</span>}</div></article>
          <article className="evidence-card"><div className="evidence-title"><span className="evidence-icon gap">+</span><div><h3>Not evidenced in resume</h3><p>Present in the job text, not detected in your resume</p></div></div><div className="chips">{analysis.not_evidenced_skills.length ? analysis.not_evidenced_skills.map(skill => <span className="chip missing" key={skill}>{skill}</span>) : <span className="empty-note">No unmatched job skills detected.</span>}</div><p className="evidence-disclaimer">This does not mean you lack these abilities—only that they weren’t found in this text.</p></article>
        </div>
        <div className="rewrite-panel"><div><span className="step-label">OPTIONAL · LOCAL MODEL</span><h3>Want a careful rewrite draft?</h3><p>Ollama must be configured by the project team. Review every claim before using generated text.</p></div><button className="secondary-button" onClick={requestRewrite} disabled={busy !== null}>{busy === 'rewrite' ? 'Preparing…' : 'Create draft'} <span>↗</span></button></div>
        {rewrite && <article className="draft-card"><div className="draft-head"><h3>{rewrite.available ? 'Draft for your review' : 'Rewrite is not configured'}</h3><span className="review-badge">HUMAN REVIEW REQUIRED</span></div>{rewrite.draft ? <pre>{rewrite.draft}</pre> : <p>Enable Ollama in the backend to request a local draft. Your current analysis is still available above.</p>}<p className="evidence-disclaimer">{rewrite.warning}</p></article>}
        <p className="caveat">{analysis.caveat} This prototype is not an ATS, hiring recommendation, or predictor of interview outcomes.</p>
      </section>}

      <footer className="footer"><span>RESUMEMATCH · COMP7607</span><span>Built for transparency, not automated screening.</span></footer>
    </main>
  );
}
