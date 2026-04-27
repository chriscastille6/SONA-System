import { useState, useEffect, useCallback } from 'react';
import './App.css';

const API_BASE = '';

function formatDateTime(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

function StudyCatalog({ studies, loading, error, onSignUp }) {
  if (loading) return <p className="catalog-loading">Loading studies…</p>;
  if (error) return <p className="catalog-error">Failed to load studies. Please try again.</p>;
  if (!studies?.length) return <p className="catalog-empty">No studies available at this time.</p>;

  return (
    <div className="catalog-grid">
      {studies.map((s) => (
        <article key={s.id} className="study-card">
          <h2 className="study-card-title">{s.title}</h2>
          {s.description && <p className="study-card-desc">{s.description}</p>}
          <p className="study-card-datetime">{formatDateTime(s.datetime)}</p>
          <p className="study-card-slots">
            <strong>{s.available_slots}</strong> of {s.max_capacity} slots remaining
          </p>
          <button
            type="button"
            className="btn btn-primary"
            disabled={s.available_slots === 0}
            onClick={() => onSignUp(s)}
          >
            {s.available_slots === 0 ? 'Full' : 'Sign Up'}
          </button>
        </article>
      ))}
    </div>
  );
}

function BookingModal({ study, onClose, onSuccess }) {
  const [secureId, setSecureId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!secureId.trim()) {
      setError('Please enter your Secure Participant ID.');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/api/signup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_id: study.id,
          participant_secure_id: secureId.trim(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error || 'Sign-up failed. Please try again.');
        return;
      }
      onSuccess({ study, ...data });
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Sign up: {study?.title}</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <label className="input-label">Enter your Secure Participant ID</label>
          <input
            type="text"
            className="input"
            value={secureId}
            onChange={(e) => setSecureId(e.target.value)}
            placeholder="Secure Participant ID"
            autoComplete="off"
            autoFocus
          />
          {error && <p className="form-error">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Signing up…' : 'Confirm'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function SuccessScreen({ result, onBack }) {
  const { study, cancellation_pin } = result;
  const icsUrl = `${API_BASE}/api/studies/${study.id}/ical/`;

  const handleDownloadIcs = () => {
    window.open(icsUrl, '_blank');
  };

  return (
    <div className="success-screen">
      <h1 className="success-title">Booking Confirmed!</h1>
      <p className="success-study">{study.title}</p>
      <p className="success-datetime">{formatDateTime(study.datetime)}</p>
      <div className="success-pin-box">
        <p className="success-pin-label">Your cancellation PIN</p>
        <p className="success-pin-value">{cancellation_pin}</p>
        <p className="success-pin-warning">
          Save this PIN. You will need your Secure ID and this PIN if you need to cancel your slot.
        </p>
      </div>
      <button type="button" className="btn btn-primary btn-ics" onClick={handleDownloadIcs}>
        Download Calendar Invite (.ics)
      </button>
      <button type="button" className="btn btn-secondary" onClick={onBack}>
        Back to catalog
      </button>
    </div>
  );
}

export default function App() {
  const [studies, setStudies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalStudy, setModalStudy] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  const fetchStudies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/studies/`);
      if (!res.ok) throw new Error('Failed to fetch');
      const data = await res.json();
      setStudies(data.studies || []);
    } catch (err) {
      setError(err.message);
      setStudies([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStudies();
  }, [fetchStudies]);

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">PRAMS</h1>
        <p className="app-subtitle">Participant Record and Management System — Study Catalog</p>
      </header>
      <main className="app-main">
        {successResult ? (
          <SuccessScreen result={successResult} onBack={() => setSuccessResult(null)} />
        ) : (
          <>
            <StudyCatalog
              studies={studies}
              loading={loading}
              error={error}
              onSignUp={setModalStudy}
            />
            {modalStudy && (
              <BookingModal
                study={modalStudy}
                onClose={() => setModalStudy(null)}
                onSuccess={(result) => {
                  setModalStudy(null);
                  setSuccessResult(result);
                  fetchStudies();
                }}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}
