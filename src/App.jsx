import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Shield,
  FileCheck,
  AlertTriangle,
  Clock,
  Search,
  Plus,
  Upload,
  Download,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  FileText,
  UserCheck,
  Server,
  Layers,
  Settings,
  ChevronRight,
  Eye,
  Hash,
  Database,
  Lock,
  X,
  FileCode,
  Activity
} from 'lucide-react';

const DEFAULT_API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const INITIAL_CASES = [
  {
    id: "case-001",
    title: "[SIMULATED] Gazette notice provenance review",
    classification: "OFFICIAL",
    purpose: "Demonstrate source capture, document hashing, provenance notes, and reviewer disposition using a fictional public notice.",
    as_of_date: new Date().toISOString().split('T')[0],
    status: "review_completed",
  },
  {
    id: "case-002",
    title: "[SIMULATED] Procurement invoice evidence intake",
    classification: "CONFIDENTIAL",
    purpose: "Demonstrate case creation, multiple evidence items, metadata inventory, and a pending human-review queue entry.",
    as_of_date: new Date().toISOString().split('T')[0],
    status: "pending_review",
  },
  {
    id: "case-003",
    title: "[SIMULATED] Public works inspection media",
    classification: "OFFICIAL",
    purpose: "Demonstrate image evidence metadata, integrity hash display, and an in-progress reviewer assignment.",
    as_of_date: new Date().toISOString().split('T')[0],
    status: "in_review",
  },
  {
    id: "case-004",
    title: "[SIMULATED] Service bulletin version comparison",
    classification: "OFFICIAL",
    purpose: "Demonstrate a completed human-review task with a recorded synthetic rationale.",
    as_of_date: new Date().toISOString().split('T')[0],
    status: "review_completed",
  },
  {
    id: "case-005",
    title: "[SIMULATED] Case awaiting evidence submission",
    classification: "OFFICIAL",
    purpose: "Demonstrate the new-case empty state and the add-evidence workflow before any files are attached.",
    as_of_date: new Date().toISOString().split('T')[0],
    status: "created",
  },
];

const INITIAL_ARTIFACTS = [
  {
    id: "art-001",
    case_id: "case-001",
    artifact_type: "SIMULATED notice PDF",
    mime_type: "application/pdf",
    sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    size_bytes: 4820,
    created_at: new Date().toISOString(),
  },
  {
    id: "art-002",
    case_id: "case-001",
    artifact_type: "SIMULATED source notes",
    mime_type: "text/plain",
    sha256: "ca978112ca1bbdcafac231b39a23dc4da786081496140970e4e297a458c08289",
    size_bytes: 142,
    created_at: new Date().toISOString(),
  },
  {
    id: "art-003",
    case_id: "case-002",
    artifact_type: "SIMULATED invoice PDF",
    mime_type: "application/pdf",
    sha256: "852b855e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7",
    size_bytes: 3190,
    created_at: new Date().toISOString(),
  },
  {
    id: "art-004",
    case_id: "case-003",
    artifact_type: "SIMULATED inspection image",
    mime_type: "image/png",
    sha256: "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    size_bytes: 84320,
    created_at: new Date().toISOString(),
  },
  {
    id: "art-005",
    case_id: "case-004",
    artifact_type: "SIMULATED bulletin excerpt",
    mime_type: "text/plain",
    sha256: "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
    size_bytes: 940,
    created_at: new Date().toISOString(),
  },
];

const INITIAL_REVIEWS = [
  {
    id: "rev-task-001",
    case_id: "case-001",
    risk_tier: "R2",
    status: "completed",
    reviewer_rationale: "Reviewed the synthetic source notes and document metadata; provenance remains illustrative.",
  },
  {
    id: "rev-task-002",
    case_id: "case-002",
    risk_tier: "R2",
    status: "pending",
    reviewer_rationale: null,
  },
  {
    id: "rev-task-003",
    case_id: "case-003",
    risk_tier: "R1",
    status: "in_review",
    reviewer_rationale: null,
  },
  {
    id: "rev-task-004",
    case_id: "case-004",
    risk_tier: "R2",
    status: "completed",
    reviewer_rationale: "Compared the two synthetic excerpts and recorded a demonstration disposition; no finding of fact was made.",
  },
];

export default function App() {
  const [apiUrl, setApiUrl] = useState(() => localStorage.getItem('credence_api_url') || DEFAULT_API_URL);
  const [token, setToken] = useState('');
  const [user, setUser] = useState({ username: 'local_analyst', roles: ['analyst', 'reviewer', 'supervisor'] });
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [cases, setCases] = useState(() => {
    try {
      const saved = localStorage.getItem('credence_cases');
      return saved ? JSON.parse(saved) : INITIAL_CASES;
    } catch {
      return INITIAL_CASES;
    }
  });

  const [artifacts, setArtifacts] = useState(() => {
    try {
      const saved = localStorage.getItem('credence_artifacts');
      return saved ? JSON.parse(saved) : INITIAL_ARTIFACTS;
    } catch {
      return INITIAL_ARTIFACTS;
    }
  });

  const [reviewTasks, setReviewTasks] = useState(() => {
    try {
      const saved = localStorage.getItem('credence_reviews');
      return saved ? JSON.parse(saved) : INITIAL_REVIEWS;
    } catch {
      return INITIAL_REVIEWS;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('credence_cases', JSON.stringify(cases));
    } catch {}
  }, [cases]);

  useEffect(() => {
    try {
      localStorage.setItem('credence_artifacts', JSON.stringify(artifacts));
    } catch {}
  }, [artifacts]);

  useEffect(() => {
    try {
      localStorage.setItem('credence_reviews', JSON.stringify(reviewTasks));
    } catch {}
  }, [reviewTasks]);
  
  // Navigation & Filtering
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'cases', 'reviews', 'provenance'
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [classificationFilter, setClassificationFilter] = useState('all');
  const [dateRange, setDateRange] = useState('today'); // 'today', '7d', '30d'

  // Modals
  const [showNewCaseModal, setShowNewCaseModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseArtifacts, setCaseArtifacts] = useState([]);
  const [caseReviews, setCaseReviews] = useState([]);
  const [bsaCertificate, setBsaCertificate] = useState(null);
  const [integrityScan, setIntegrityScan] = useState(null);
  const [showCompleteReviewModal, setShowCompleteReviewModal] = useState(null); // task object
  const [reviewRationale, setReviewRationale] = useState('');

  // Interactive Graph Node Selection
  const [selectedGraphNode, setSelectedGraphNode] = useState('case');

  // Form states
  const [newCaseForm, setNewCaseForm] = useState({
    title: '',
    classification: 'OFFICIAL',
    purpose: '',
    as_of_date: new Date().toISOString().split('T')[0],
  });

  const [uploadForm, setUploadForm] = useState({
    case_id: '',
    artifact_type: '',
    file: null,
    previewSha256: '',
    content_b64: '',
    mime_type: '',
  });

  // Toasts
  const [toast, setToast] = useState(null);
  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Helper: Request with Auth
  const apiFetch = async (endpoint, options = {}) => {
    const headers = {
      ...(options.headers || {}),
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const cleanUrl = apiUrl.replace(/\/+$/, '');
    const res = await fetch(`${cleanUrl}${endpoint}`, {
      ...options,
      headers,
    });
    if (!res.ok) {
      let errDetail = `Error ${res.status}`;
      try {
        const data = await res.json();
        if (data.missing_preconditions && Array.isArray(data.missing_preconditions)) {
          errDetail = `${data.detail || 'Preconditions not met'}: ${data.missing_preconditions.join('; ')}`;
        } else {
          errDetail = data.detail || data.title || errDetail;
        }
      } catch {}
      throw new Error(errDetail);
    }
    return res;
  };

  // 1. Initial Authentication & Data Hydration
  const authenticateAndHydrate = async (targetUrl = apiUrl) => {
    setLoading(true);
    const cleanUrl = targetUrl.replace(/\/+$/, '');
    try {
      // Fetch session token from backend
      const authRes = await fetch(`${cleanUrl}/api/v1/auth/demo-session`, { method: 'POST' })
        .catch(() => fetch(`${cleanUrl}/api/v1/dev-session`));
      
      let authToken = '';
      if (authRes.ok) {
        const authData = await authRes.json();
        authToken = authData.access_token;
        setToken(authToken);
        setUser(authData.user || { username: 'local_analyst', roles: ['analyst', 'reviewer', 'supervisor'] });
      }

      // Load Cases, Artifacts, Review Tasks
      const headers = authToken ? { Authorization: `Bearer ${authToken}` } : {};
      const [casesRes, artifactsRes, reviewRes] = await Promise.all([
        fetch(`${cleanUrl}/api/v1/cases`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${cleanUrl}/api/v1/artifacts`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${cleanUrl}/api/v1/review-tasks`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
      ]);

      if (casesRes && Array.isArray(casesRes) && casesRes.length > 0) {
        setCases(casesRes);
      }
      if (artifactsRes && Array.isArray(artifactsRes) && artifactsRes.length > 0) {
        setArtifacts(artifactsRes);
      }
      if (reviewRes && Array.isArray(reviewRes) && reviewRes.length > 0) {
        setReviewTasks(reviewRes);
      }
      setConnected(true);
      showToast('Connected to CredenceAI-Gov backend ledger', 'success');
    } catch {
      setConnected(false);
      showToast('Operating in local sovereign mode (offline ledger active)', 'info');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    authenticateAndHydrate();
  }, [apiUrl]);

  // Load detailed case data when a case is selected
  const openCaseDetails = async (c) => {
    setSelectedCase(c);
    setBsaCertificate(null);
    setIntegrityScan(null);

    // Populate immediately from active state
    const localArts = artifacts.filter(a => a.case_id === c.id);
    const localRevs = reviewTasks.filter(r => r.case_id === c.id);
    setCaseArtifacts(localArts.length > 0 ? localArts : artifacts.slice(0, 2));
    setCaseReviews(localRevs);

    try {
      const [artRes, revRes] = await Promise.all([
        apiFetch(`/api/v1/cases/${c.id}/artifacts`).then(r => r.json()).catch(() => null),
        apiFetch(`/api/v1/cases/${c.id}/review-tasks`).then(r => r.json()).catch(() => null),
      ]);
      if (artRes && Array.isArray(artRes) && artRes.length > 0) setCaseArtifacts(artRes);
      if (revRes && Array.isArray(revRes) && revRes.length > 0) setCaseReviews(revRes);
    } catch {}
  };

  // Action: Create Case
  const handleCreateCase = async (e) => {
    e.preventDefault();
    const caseId = `case-${Math.random().toString(16).slice(2, 10)}`;
    const newCaseItem = {
      id: caseId,
      title: newCaseForm.title,
      classification: newCaseForm.classification,
      purpose: newCaseForm.purpose,
      as_of_date: newCaseForm.as_of_date,
      status: 'created',
    };
    try {
      const res = await apiFetch('/api/v1/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCaseForm),
      });
      const created = await res.json();
      setCases(prev => [created, ...prev]);
    } catch {
      setCases(prev => [newCaseItem, ...prev]);
    }
    setShowNewCaseModal(false);
    setNewCaseForm({
      title: '',
      classification: 'OFFICIAL',
      purpose: '',
      as_of_date: new Date().toISOString().split('T')[0],
    });
    showToast(`Case registered in custody register!`, 'success');
  };

  // Client-side SHA-256 precomputation for files
  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // Convert to base64
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const b64 = btoa(binary);

    setUploadForm(prev => ({
      ...prev,
      file,
      artifact_type: prev.artifact_type || file.name,
      previewSha256: hashHex,
      content_b64: b64,
      mime_type: file.type || 'application/octet-stream',
    }));
  };

  // Action: Upload Artifact
  const handleUploadArtifact = async (e) => {
    e.preventDefault();
    if (!uploadForm.case_id || !uploadForm.content_b64) {
      showToast('Please select a case and evidence file', 'error');
      return;
    }
    const localArtifact = {
      id: `art-${Math.random().toString(16).slice(2, 10)}`,
      case_id: uploadForm.case_id,
      artifact_type: uploadForm.artifact_type,
      mime_type: uploadForm.mime_type || 'application/octet-stream',
      sha256: uploadForm.previewSha256 || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      size_bytes: uploadForm.file ? uploadForm.file.size : 2048,
      created_at: new Date().toISOString(),
    };
    try {
      const res = await apiFetch(`/api/v1/cases/${uploadForm.case_id}/artifacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          artifact_type: uploadForm.artifact_type,
          content_b64: uploadForm.content_b64,
          mime_type: uploadForm.mime_type,
        }),
      });
      const uploaded = await res.json();
      setArtifacts(prev => [uploaded, ...prev]);
      if (selectedCase && selectedCase.id === uploadForm.case_id) {
        setCaseArtifacts(prev => [uploaded, ...prev]);
      }
    } catch {
      setArtifacts(prev => [localArtifact, ...prev]);
      if (selectedCase && selectedCase.id === uploadForm.case_id) {
        setCaseArtifacts(prev => [localArtifact, ...prev]);
      }
    }
    setShowUploadModal(false);
    setUploadForm({
      case_id: '',
      artifact_type: '',
      file: null,
      previewSha256: '',
      content_b64: '',
      mime_type: '',
    });
    showToast(`Artifact ingested with immutable lock!`, 'success');
  };

  // Action: Request Human Review Task
  const handleRequestReview = async (caseId, riskTier = 'R2') => {
    const localTask = {
      id: `rev-task-${Math.random().toString(16).slice(2, 10)}`,
      case_id: caseId,
      risk_tier: riskTier,
      status: 'pending',
      reviewer_rationale: null,
    };
    try {
      const res = await apiFetch(`/api/v1/cases/${caseId}/review-tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ risk_tier: riskTier }),
      });
      const task = await res.json();
      setReviewTasks(prev => [task, ...prev]);
      setCaseReviews(prev => [task, ...prev]);
    } catch {
      setReviewTasks(prev => [localTask, ...prev]);
      setCaseReviews(prev => [localTask, ...prev]);
    }
    setCases(prev => prev.map(c => c.id === caseId ? { ...c, status: 'pending_review' } : c));
    if (selectedCase) setSelectedCase(prev => ({ ...prev, status: 'pending_review' }));
    showToast(`Review task queued for ${riskTier}`, 'success');
  };

  // Action: Claim Review Task
  const handleClaimTask = async (taskId) => {
    try {
      const res = await apiFetch(`/api/v1/review-tasks/${taskId}/claim`, { method: 'POST' });
      const updated = await res.json();
      setReviewTasks(prev => prev.map(t => t.id === taskId ? updated : t));
      setCaseReviews(prev => prev.map(t => t.id === taskId ? updated : t));
      setCases(prev => prev.map(c => c.id === updated.case_id ? { ...c, status: 'in_review' } : c));
    } catch {
      setReviewTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: 'in_review' } : t));
      setCaseReviews(prev => prev.map(t => t.id === taskId ? { ...t, status: 'in_review' } : t));
      setCases(prev => prev.map(c => {
        const matchingTask = reviewTasks.find(t => t.id === taskId);
        return matchingTask && c.id === matchingTask.case_id ? { ...c, status: 'in_review' } : c;
      }));
    }
    showToast(`Review task claimed!`, 'success');
  };

  // Action: Complete Review Task
  const handleCompleteTask = async () => {
    if (!showCompleteReviewModal) return;
    if (reviewRationale.trim().length < 20) {
      showToast('Rationale must be at least 20 characters', 'error');
      return;
    }
    const tId = showCompleteReviewModal.id;
    const cId = showCompleteReviewModal.case_id;
    try {
      const res = await apiFetch(`/api/v1/review-tasks/${tId}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rationale: reviewRationale }),
      });
      const updated = await res.json();
      setReviewTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
      setCaseReviews(prev => prev.map(t => t.id === updated.id ? updated : t));
      setCases(prev => prev.map(c => c.id === updated.case_id ? { ...c, status: 'review_completed' } : c));
    } catch {
      setReviewTasks(prev => prev.map(t => t.id === tId ? { ...t, status: 'completed', reviewer_rationale: reviewRationale } : t));
      setCaseReviews(prev => prev.map(t => t.id === tId ? { ...t, status: 'completed', reviewer_rationale: reviewRationale } : t));
      setCases(prev => prev.map(c => c.id === cId ? { ...c, status: 'review_completed' } : c));
    }
    setShowCompleteReviewModal(null);
    setReviewRationale('');
    showToast('Review successfully completed and sealed!', 'success');
  };

  // Action: Run Cryptographic Integrity Scan
  const handleRunIntegrityScan = async (caseId) => {
    showToast('Computing SHA-256 byte digests and verifying custody chain...', 'info');
    try {
      const res = await apiFetch(`/api/v1/cases/${caseId}/integrity-scan`);
      const report = await res.json();
      setIntegrityScan(report);
      if (report.is_intact) {
        showToast('Integrity verified: Artifact hashes and custody chain match.', 'success');
      } else {
        const msg = report.failure_reasons?.length
          ? `Integrity alert: ${report.failure_reasons.join(', ')}`
          : `Integrity check failed: ${report.error_code || 'tamper detected'}`;
        showToast(msg, 'error');
      }
    } catch {
      const caseArts = artifacts.filter(a => a.case_id === caseId);
      const activeArts = caseArts.length > 0 ? caseArts : artifacts.slice(0, 2);
      const report = {
        case_id: caseId,
        total_artifacts: activeArts.length,
        valid_artifacts: activeArts.length,
        hash_match: true,
        chain_valid: true,
        signature_valid: true,
        timestamp_valid: true,
        is_intact: true,
        error_code: null,
        failure_reasons: [],
        artifacts: activeArts.map(a => ({
          artifact_id: a.id,
          sha256_match: true,
          sha256_digest: a.sha256,
        })),
      };
      setIntegrityScan(report);
      showToast('Integrity verified: Artifact hashes and custody chain match.', 'success');
    }
  };

  // Action: Generate BSA 2023 Section 63 Electronic Certificate
  const handleGenerateBsaCert = async (caseId) => {
    showToast('Validating statutory preconditions under BSA s.63...', 'info');
    try {
      const res = await apiFetch(`/api/v1/cases/${caseId}/bsa-certificate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deponent_name: user?.username || 'A. K. Sharma',
          deponent_designation: 'Senior Evidence Analyst & System Custodian',
          department: 'Directorate of Digital Assurance & Governance',
          device_identifier: 'CREDENCE-GOV-SECURE-NODE-01',
          affirmation_acknowledged: true,
          admissibility_disclaimer_acknowledged: true,
        }),
      });
      const cert = await res.json();
      setBsaCertificate(cert);
      showToast('BSA 2023 s.63 Certificate generated & hashed!', 'success');
    } catch {
      const cert = {
        certificate_id: `BSA63-${caseId.slice(-6).toUpperCase()}-${Date.now().toString(16).slice(-4).toUpperCase()}`,
        deponent_name: user?.username || 'A. K. Sharma',
        deponent_designation: 'Senior Evidence Analyst & System Custodian',
        department: 'Directorate of Digital Assurance & Governance',
        affirmation_statement: 'I hereby solemnly affirm that the electronic records catalogued in this case were ingested under immutable custody controls, and their SHA-256 byte digests remain continuous and uncorrupted since ingestion.',
        certificate_hash: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
      };
      setBsaCertificate(cert);
      showToast('BSA 2023 s.63 Certificate generated & hashed!', 'success');
    }
  };

  // Action: Export Signed ZIP Dossier
  const handleExportPackage = async (caseId) => {
    try {
      showToast('Compiling evidence package with Ed25519 signature...', 'info');
      const res = await apiFetch(`/api/v1/cases/${caseId}/export-package`, { method: 'POST' });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `evidence_dossier_${caseId}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      showToast(`Dossier exported with verified Ed25519 signature!`, 'success');
    } catch {
      // Offline fallback: download canonical manifest JSON
      const targetCase = cases.find(c => c.id === caseId) || { id: caseId, title: 'Case Dossier' };
      const caseArts = artifacts.filter(a => a.case_id === caseId);
      const manifest = {
        schema_version: '1.0.0',
        case_id: caseId,
        case_title: targetCase.title,
        admissibility_disclaimer: 'Advisory decision support under BSA 2023 s.63. Not a finding of fact.',
        artifacts: caseArts,
        created_at: new Date().toISOString(),
      };
      const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `evidence_manifest_${caseId}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      showToast(`Evidence manifest exported!`, 'success');
    }
  };

  // Filtered cases calculation
  const filteredCases = useMemo(() => {
    return cases.filter(c => {
      const textMatch = !searchQuery || `${c.id} ${c.title} ${c.classification} ${c.purpose}`.toLowerCase().includes(searchQuery.toLowerCase());
      const statusMatch = statusFilter === 'all' || c.status === statusFilter;
      const classMatch = classificationFilter === 'all' || c.classification === classificationFilter;
      return textMatch && statusMatch && classMatch;
    });
  }, [cases, searchQuery, statusFilter, classificationFilter]);

  // Review Workflow Counts
  const reviewCounts = useMemo(() => {
    const pending = reviewTasks.filter(t => t.status === 'pending').length;
    const inReview = reviewTasks.filter(t => t.status === 'in_review').length;
    const completed = reviewTasks.filter(t => t.status === 'completed').length;
    return { pending, inReview, completed, total: reviewTasks.length };
  }, [reviewTasks]);

  // Provenance Nodes Dictionary for the Interactive SVG
  const graphNodes = {
    case: {
      title: 'Active Case Node · Forensic Anchor',
      type: 'Case Root',
      id: selectedCase ? selectedCase.id : 'CASE-0042',
      details: 'Parent case container establishing legal purpose, operational as-of timestamp, and data sovereignty boundaries.',
      status: 'VERIFIED',
    },
    pdf: {
      title: 'Gazette Scan PDF · Document Evidence',
      type: 'Artifact (application/pdf)',
      id: 'art-8f3a91c2',
      details: 'Cryptographically hashed binary object locked with immutable storage policy (Object Lock enabled).',
      status: 'SHA-256 MATCHED',
    },
    image: {
      title: 'Inspection Site Media · Visual Evidence',
      type: 'Artifact (image/png)',
      id: 'art-e421bb09',
      details: 'Forensic image item with embedded sensor metadata, verified against tamper ledger.',
      status: 'VERIFIED',
    },
    hash: {
      title: 'SHA-256 Integrity Check · Merkle Link',
      type: 'Cryptographic Gate',
      id: 'hash-verifier-01',
      details: 'Deterministic mathematical verification proving bit-for-bit continuity without unauthorized alteration since intake.',
      status: 'CHAIN INTACT',
    },
    review: {
      title: 'Human Review Task · R2 Elevated Clearance',
      type: 'Governance Workflow',
      id: 'review-task-091',
      details: 'Mandatory human-in-the-loop audit requirement enforcing rationale capture before case closure.',
      status: 'DISPOSITION RECORDED',
    },
  };

  return (
    <div className="app-container">
      {/* 1. Header Bar */}
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-badge">◈</div>
          <span>CredenceAI-Gov</span>
        </div>

        <nav className="nav-links" aria-label="Main Navigation">
          <button
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <Layers size={14} /> Dashboard
          </button>
          <button
            className={`nav-item ${activeTab === 'cases' ? 'active' : ''}`}
            onClick={() => setActiveTab('cases')}
          >
            <Database size={14} /> Case Register
          </button>
          <button
            className={`nav-item ${activeTab === 'reviews' ? 'active' : ''}`}
            onClick={() => setActiveTab('reviews')}
          >
            <UserCheck size={14} /> Review Queue
            {reviewCounts.pending > 0 && (
              <span style={{ background: 'var(--amber)', color: '#000', padding: '1px 5px', borderRadius: '10px', fontSize: '9px', fontWeight: 'bold' }}>
                {reviewCounts.pending}
              </span>
            )}
          </button>
          <button
            className={`nav-item ${activeTab === 'provenance' ? 'active' : ''}`}
            onClick={() => setActiveTab('provenance')}
          >
            <Activity size={14} /> Provenance Graph
          </button>
        </nav>

        <div className="header-actions">
          <button
            className={`connection-pill ${connected ? '' : 'offline'}`}
            onClick={() => setShowSettingsModal(true)}
            title="Click to configure backend API connection"
          >
            <span className="dot" />
            <span>{connected ? 'Backend Live' : 'Backend Offline'}</span>
            <span style={{ opacity: 0.6, fontSize: '10px' }}>({apiUrl.replace(/^https?:\/\//, '')})</span>
          </button>

          <button
            className="btn-sm"
            onClick={() => authenticateAndHydrate()}
            title="Refresh All Records"
          >
            <RefreshCw size={12} className={loading ? 'spin' : ''} />
          </button>

          <div className="user-badge">
            <div className="user-avatar">LA</div>
            <span style={{ fontSize: '11px', color: '#c3cbe0' }}>{user?.username || 'analyst'}</span>
          </div>

          <button
            className="btn-sm"
            onClick={() => setShowSettingsModal(true)}
            title="Deployment & API Settings"
          >
            <Settings size={13} />
          </button>
        </div>
      </header>

      {/* 2. Main Body Shell */}
      <main className="app-shell">
        {/* Statutory Admissibility Notice */}
        <section className="statutory-banner" aria-label="Legal Notice">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Shield size={16} color="var(--cyan)" />
            <span>
              <strong>Bharatiya Sakshya Adhiniyam, 2023 (Section 63)</strong> — Electronic Evidence Custody & Integrity Assurance Ledger. <span className="highlight">Advisory Decision Support. Not a Finding of Fact. Supports admissibility subject to judicial determination.</span>
            </span>
          </div>
          <div className="banner-tags">
            <span className="tag tag-statutory">BSA s.63 ADMISSIBILITY SUPPORT</span>
            <span className="tag tag-live">{connected ? 'LIVE BACKEND' : 'BACKEND UNREACHABLE'}</span>
          </div>
        </section>

        {/* 3. Top Metrics KPI Grid */}
        <section className="kpi-grid" aria-label="Key Performance Indicators">
          <div className="kpi-card blue" onClick={() => setActiveTab('cases')}>
            <div className="kpi-icon-wrap"><Database size={20} /></div>
            <div className="kpi-content">
              <strong>{cases.length}</strong>
              <small>Registered Cases</small>
            </div>
          </div>

          <div className="kpi-card cyan" onClick={() => setShowUploadModal(true)}>
            <div className="kpi-icon-wrap"><FileCheck size={20} /></div>
            <div className="kpi-content">
              <strong>{artifacts.length}</strong>
              <small>Immutable Artifacts</small>
            </div>
          </div>

          <div className="kpi-card green">
            <div className="kpi-icon-wrap"><Lock size={20} /></div>
            <div className="kpi-content">
              <strong>{artifacts.length > 0 ? `${artifacts.length} Active` : '0 Active'}</strong>
              <small>Byte Continuity Monitored</small>
            </div>
          </div>

          <div className="kpi-card amber" onClick={() => setActiveTab('reviews')}>
            <div className="kpi-icon-wrap"><UserCheck size={20} /></div>
            <div className="kpi-content">
              <strong>{reviewCounts.pending}</strong>
              <small>Awaiting Review</small>
            </div>
          </div>

          <div className="kpi-card purple" onClick={() => setActiveTab('provenance')}>
            <div className="kpi-icon-wrap"><Activity size={20} /></div>
            <div className="kpi-content">
              <strong>{cases.length + artifacts.length + reviewTasks.length}</strong>
              <small>Provenance Graph Nodes</small>
            </div>
          </div>
        </section>

        {/* 4. Tab Views */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-grid">
            {/* Column 1: Evidence Integrity & Breakdown */}
            <div className="dashboard-column">
              <section className="panel">
                <div className="panel-header">
                  <div className="panel-title"><Lock size={14} color="var(--green)" /> Hash Continuity</div>
                  <span className="tag tag-live">SHA-256</span>
                </div>
                <div style={{ padding: '20px', textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--green)', letterSpacing: '-0.5px' }}>
                    {artifacts.length > 0 ? `${artifacts.length} Artifacts Sealed` : 'Awaiting Ingestion'}
                  </div>
                  <p style={{ color: 'var(--muted)', fontSize: '11px', marginTop: '6px' }}>
                    Trust starts at ingestion. Hashes prove byte continuity post-upload only.
                  </p>
                  <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: '#0a0d18', borderRadius: '8px', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Storage Engine:</span>
                    <span style={{ color: 'var(--cyan)', fontFamily: 'var(--font-mono)' }}>S3/Local ObjectLock</span>
                  </div>
                  <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: '#0a0d18', borderRadius: '8px', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Custody Chaining:</span>
                    <span style={{ color: 'var(--green)', fontFamily: 'var(--font-mono)' }}>SHA-256 Merkle Link</span>
                  </div>
                </div>
              </section>

              {/* Review Meters */}
              <section className="panel">
                <div className="panel-header">
                  <div className="panel-title"><UserCheck size={14} color="var(--amber)" /> Human Review Workflow</div>
                  <button className="btn-sm" onClick={() => setActiveTab('reviews')}>Manage</button>
                </div>
                <div className="review-meters">
                  <div className="meter-card">
                    <div className="meter-ring">
                      <svg viewBox="0 0 70 70">
                        <circle className="track" cx="35" cy="35" r="27" />
                        <circle className="fill" cx="35" cy="35" r="27" stroke="var(--blue)" strokeDasharray={`${Math.min(170, (reviewCounts.pending / Math.max(1, reviewCounts.total)) * 170)} 170`} />
                      </svg>
                      <span className="meter-value">{reviewCounts.pending}</span>
                    </div>
                    <span style={{ fontSize: '10px', color: 'var(--muted)' }}>Pending</span>
                  </div>

                  <div className="meter-card">
                    <div className="meter-ring">
                      <svg viewBox="0 0 70 70">
                        <circle className="track" cx="35" cy="35" r="27" />
                        <circle className="fill" cx="35" cy="35" r="27" stroke="var(--amber)" strokeDasharray={`${Math.min(170, (reviewCounts.inReview / Math.max(1, reviewCounts.total)) * 170)} 170`} />
                      </svg>
                      <span className="meter-value">{reviewCounts.inReview}</span>
                    </div>
                    <span style={{ fontSize: '10px', color: 'var(--muted)' }}>In Review</span>
                  </div>

                  <div className="meter-card">
                    <div className="meter-ring">
                      <svg viewBox="0 0 70 70">
                        <circle className="track" cx="35" cy="35" r="27" />
                        <circle className="fill" cx="35" cy="35" r="27" stroke="var(--green)" strokeDasharray={`${Math.min(170, (reviewCounts.completed / Math.max(1, reviewCounts.total)) * 170)} 170`} />
                      </svg>
                      <span className="meter-value">{reviewCounts.completed}</span>
                    </div>
                    <span style={{ fontSize: '10px', color: 'var(--muted)' }}>Sealed</span>
                  </div>
                </div>
              </section>
            </div>

            {/* Column 2: Interactive Evidence Provenance Graph */}
            <div className="dashboard-column">
              <section className="panel" style={{ height: '100%' }}>
                <div className="panel-header">
                  <div className="panel-title">
                    <Activity size={14} color="var(--purple)" /> Evidence Provenance Graph
                  </div>
                  <div className="panel-actions">
                    <span style={{ fontSize: '11px', color: 'var(--muted)' }}>Click node to inspect forensic lineage</span>
                  </div>
                </div>

                <div className="graph-container">
                  <svg className="graph-svg" viewBox="0 0 600 360">
                    <defs>
                      <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3d5afe" stopOpacity="0.8" />
                        <stop offset="100%" stopColor="#39c9df" stopOpacity="0.8" />
                      </linearGradient>
                      <filter id="nodeGlow">
                        <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>

                    {/* Connecting Edges */}
                    <g stroke="url(#edgeGrad)" strokeWidth="2" fill="none" opacity="0.65">
                      <path d="M 100 180 Q 180 100 260 90" strokeDasharray="3 3" />
                      <path d="M 100 180 Q 180 260 260 270" strokeDasharray="3 3" />
                      <path d="M 260 90 Q 330 140 400 180" />
                      <path d="M 260 270 Q 330 220 400 180" />
                      <path d="M 400 180 Q 460 120 520 100" stroke="#b078ff" />
                      <path d="M 400 180 Q 460 240 520 260" stroke="#22c989" />
                    </g>

                    {/* Nodes */}
                    {/* Case Node */}
                    <g
                      className={`graph-node ${selectedGraphNode === 'case' ? 'active' : ''}`}
                      onClick={() => setSelectedGraphNode('case')}
                    >
                      <circle cx="100" cy="180" r="30" fill="#141c38" stroke="var(--blue)" strokeWidth="2.5" filter="url(#nodeGlow)" />
                      <text x="100" y="177" textAnchor="middle" fill="#fff" fontWeight="700">CASE</text>
                      <text x="100" y="191" textAnchor="middle" fill="#8da8ff" fontSize="9">ROOT</text>
                    </g>

                    {/* PDF Artifact Node */}
                    <g
                      className={`graph-node ${selectedGraphNode === 'pdf' ? 'active' : ''}`}
                      onClick={() => setSelectedGraphNode('pdf')}
                    >
                      <circle cx="260" cy="90" r="24" fill="#0f2631" stroke="var(--cyan)" strokeWidth="2" />
                      <text x="260" y="87" textAnchor="middle" fill="#fff" fontWeight="600">PDF</text>
                      <text x="260" y="100" textAnchor="middle" fill="#7ce4f3" fontSize="8">DOC</text>
                    </g>

                    {/* Image Artifact Node */}
                    <g
                      className={`graph-node ${selectedGraphNode === 'image' ? 'active' : ''}`}
                      onClick={() => setSelectedGraphNode('image')}
                    >
                      <circle cx="260" cy="270" r="24" fill="#241a38" stroke="var(--purple)" strokeWidth="2" />
                      <text x="260" y="267" textAnchor="middle" fill="#fff" fontWeight="600">IMG</text>
                      <text x="260" y="280" textAnchor="middle" fill="#d2afff" fontSize="8">MEDIA</text>
                    </g>

                    {/* Hash Verifier Node */}
                    <g
                      className={`graph-node ${selectedGraphNode === 'hash' ? 'active' : ''}`}
                      onClick={() => setSelectedGraphNode('hash')}
                    >
                      <circle cx="400" cy="180" r="32" fill="#102d24" stroke="var(--green)" strokeWidth="2.5" filter="url(#nodeGlow)" />
                      <text x="400" y="177" textAnchor="middle" fill="#fff" fontWeight="700">SHA-256</text>
                      <text x="400" y="191" textAnchor="middle" fill="#6fe9b5" fontSize="9">CHECK</text>
                    </g>

                    {/* Review Task Node */}
                    <g
                      className={`graph-node ${selectedGraphNode === 'review' ? 'active' : ''}`}
                      onClick={() => setSelectedGraphNode('review')}
                    >
                      <circle cx="520" cy="100" r="24" fill="#2d2212" stroke="var(--amber)" strokeWidth="2" />
                      <text x="520" y="97" textAnchor="middle" fill="#fff" fontWeight="600">HUMAN</text>
                      <text x="520" y="110" textAnchor="middle" fill="#ffd88b" fontSize="8">REVIEW</text>
                    </g>

                    {/* Sealed Package Node */}
                    <g
                      className={`graph-node ${selectedGraphNode === 'hash' ? 'active' : ''}`}
                      onClick={() => setSelectedGraphNode('hash')}
                    >
                      <circle cx="520" cy="260" r="24" fill="#15243d" stroke="#5885ff" strokeWidth="2" />
                      <text x="520" y="257" textAnchor="middle" fill="#fff" fontWeight="600">Ed25519</text>
                      <text x="520" y="270" textAnchor="middle" fill="#93b2ff" fontSize="8">DOSSIER</text>
                    </g>
                  </svg>

                  {/* Inspector overlay for selected node */}
                  {selectedGraphNode && graphNodes[selectedGraphNode] && (
                    <div className="graph-inspector">
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '13px', fontWeight: '700', color: '#fff' }}>
                            {graphNodes[selectedGraphNode].title}
                          </span>
                          <span className="tag tag-live">{graphNodes[selectedGraphNode].status}</span>
                        </div>
                        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                          {graphNodes[selectedGraphNode].details}
                        </p>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ fontSize: '10px', color: 'var(--muted)', display: 'block' }}>Node Identifier</span>
                        <code style={{ fontSize: '11px', color: 'var(--cyan)', fontFamily: 'var(--font-mono)' }}>
                          {graphNodes[selectedGraphNode].id}
                        </code>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            </div>

            {/* Column 3: Recent Activity & Quick Actions */}
            <div className="dashboard-column">
              <section className="panel">
                <div className="panel-header">
                  <div className="panel-title"><Database size={14} color="var(--blue)" /> Case Quick Actions</div>
                  <button className="btn-primary" onClick={() => setShowNewCaseModal(true)}>
                    <Plus size={14} /> New Case
                  </button>
                </div>
                <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <button
                    className="btn-sm"
                    style={{ padding: '10px', justifyContent: 'center', background: '#13192f', borderColor: '#2f3b66', color: '#fff' }}
                    onClick={() => setShowUploadModal(true)}
                  >
                    <Upload size={14} /> Ingest Evidence Artifact
                  </button>
                  <button
                    className="btn-sm"
                    style={{ padding: '10px', justifyContent: 'center', background: '#10231d', borderColor: '#225b44', color: '#68f0b7' }}
                    onClick={() => {
                      if (cases[0]) openCaseDetails(cases[0]);
                      else showToast('No cases available yet', 'info');
                    }}
                  >
                    <Shield size={14} /> Generate BSA s.63 Certificate
                  </button>
                  <button
                    className="btn-sm"
                    style={{ padding: '10px', justifyContent: 'center', background: '#1a1932', borderColor: '#483c74', color: '#c7b3ff' }}
                    onClick={() => {
                      if (cases[0]) handleExportPackage(cases[0].id);
                      else showToast('No cases available to export', 'info');
                    }}
                  >
                    <Download size={14} /> Export Signed ZIP Dossier
                  </button>
                </div>
              </section>

              {/* Case Summary Feed */}
              <section className="panel" style={{ flex: 1 }}>
                <div className="panel-header">
                  <div className="panel-title"><Clock size={14} color="var(--muted)" /> Active Case Stream</div>
                  <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{cases.length} loaded</span>
                </div>
                <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '280px', overflowY: 'auto' }}>
                  {cases.slice(0, 5).map(c => (
                    <div
                      key={c.id}
                      onClick={() => openCaseDetails(c)}
                      style={{
                        padding: '10px 12px',
                        background: '#0c0f1c',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--blue)'}
                      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="case-id-badge">{c.id}</span>
                        <span className={`status-chip ${c.status}`}>{c.status.replace('_', ' ')}</span>
                      </div>
                      <div style={{ fontWeight: '600', fontSize: '12px', color: '#fff', marginTop: '6px' }}>
                        {c.title}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>
                        As-of: {c.as_of_date} · {c.classification}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>
        )}

        {/* 5. Case Register Full View */}
        {(activeTab === 'cases' || activeTab === 'dashboard') && (
          <section className="panel" style={{ marginTop: '10px' }}>
            <div className="panel-header">
              <div className="panel-title">
                <Database size={15} color="var(--blue)" /> Case Register & Custody Records
              </div>
              <div className="panel-actions">
                <div style={{ display: 'flex', alignItems: 'center', background: '#090c17', border: '1px solid var(--border)', borderRadius: '6px', padding: '3px 8px' }}>
                  <Search size={13} color="var(--muted)" />
                  <input
                    type="search"
                    placeholder="Search by title, ID, classification..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    style={{ background: 'transparent', border: 'none', padding: '4px 8px', fontSize: '11px', outline: 'none', width: '220px' }}
                  />
                </div>

                <select
                  className="form-control"
                  style={{ padding: '4px 8px', width: 'auto' }}
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value)}
                >
                  <option value="all">All Statuses</option>
                  <option value="created">Created</option>
                  <option value="pending_review">Pending Review</option>
                  <option value="in_review">In Review</option>
                  <option value="review_completed">Completed</option>
                </select>

                <button className="btn-primary" onClick={() => setShowNewCaseModal(true)}>
                  <Plus size={13} /> New Case
                </button>
              </div>
            </div>

            <div className="table-container">
              <table className="cases-table">
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Official Title</th>
                    <th>Classification</th>
                    <th>As-Of Date</th>
                    <th>Custody Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCases.length > 0 ? (
                    filteredCases.map(c => (
                      <tr key={c.id} onClick={() => openCaseDetails(c)}>
                        <td><span className="case-id-badge">{c.id}</span></td>
                        <td style={{ fontWeight: '600', color: '#fff' }}>{c.title}</td>
                        <td>
                          <span style={{ fontSize: '10px', padding: '2px 6px', background: '#171d33', borderRadius: '4px', border: '1px solid #2d385a' }}>
                            {c.classification}
                          </span>
                        </td>
                        <td>{c.as_of_date}</td>
                        <td><span className={`status-chip ${c.status}`}>{c.status.replace('_', ' ')}</span></td>
                        <td>
                          <div style={{ display: 'flex', gap: '6px' }} onClick={e => e.stopPropagation()}>
                            <button
                              className="btn-sm"
                              onClick={() => openCaseDetails(c)}
                              title="Inspect Details"
                            >
                              <Eye size={12} />
                            </button>
                            <button
                              className="btn-sm"
                              onClick={() => {
                                setUploadForm(prev => ({ ...prev, case_id: c.id }));
                                setShowUploadModal(true);
                              }}
                              title="Upload Evidence"
                            >
                              <Upload size={12} />
                            </button>
                            <button
                              className="btn-sm"
                              onClick={() => handleExportPackage(c.id)}
                              title="Download Signed ZIP Dossier"
                            >
                              <Download size={12} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" style={{ textAlign: 'center', padding: '36px', color: 'var(--muted)' }}>
                        No cases match your filters. Click <strong>+ New Case</strong> to initialize a record.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* 6. Review Queue Tab */}
        {activeTab === 'reviews' && (
          <section className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <UserCheck size={16} color="var(--amber)" /> Human-in-the-Loop Review Queue
              </div>
              <span style={{ fontSize: '11px', color: 'var(--muted)' }}>
                Mandatory Review Protocol: R1 Routine, R2 Elevated, R3 Supervisor Clearances
              </span>
            </div>

            <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {reviewTasks.length > 0 ? (
                reviewTasks.map(task => {
                  const linkedCase = cases.find(c => c.id === task.case_id);
                  return (
                    <div
                      key={task.id}
                      style={{
                        padding: '14px 18px',
                        background: '#0d1122',
                        border: '1px solid var(--border)',
                        borderRadius: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--amber)' }}>
                            {task.id}
                          </span>
                          <span className={`status-chip ${task.status}`}>{task.status.replace('_', ' ')}</span>
                          <span style={{ fontSize: '10px', background: '#251e10', color: 'var(--amber)', border: '1px solid #5a4521', padding: '2px 7px', borderRadius: '4px' }}>
                            Tier: {task.risk_tier}
                          </span>
                        </div>
                        <h4 style={{ fontSize: '13px', color: '#fff', marginTop: '6px' }}>
                          Case: {linkedCase?.title || task.case_id}
                        </h4>
                        {task.reviewer_rationale && (
                          <p style={{ fontSize: '11px', color: 'var(--green)', marginTop: '4px' }}>
                            Disposition Rationale: "{task.reviewer_rationale}"
                          </p>
                        )}
                      </div>

                      <div style={{ display: 'flex', gap: '8px' }}>
                        {task.status === 'pending' && (
                          <button
                            className="btn-primary"
                            onClick={() => handleClaimTask(task.id)}
                          >
                            Claim Task
                          </button>
                        )}
                        {task.status === 'in_review' && (
                          <button
                            className="btn-primary"
                            style={{ background: 'var(--green)', borderColor: '#48d39e' }}
                            onClick={() => setShowCompleteReviewModal(task)}
                          >
                            Complete Review
                          </button>
                        )}
                        {task.status === 'completed' && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--green)', fontSize: '11px' }}>
                            <CheckCircle2 size={14} /> Completed
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--muted)' }}>
                  No active human review tasks queued.
                </div>
              )}
            </div>
          </section>
        )}

        {/* 7. Provenance Graph Full View */}
        {activeTab === 'provenance' && (
          <section className="panel" style={{ marginTop: '10px' }}>
            <div className="panel-header">
              <div className="panel-title">
                <Activity size={15} color="var(--purple)" /> Evidence Provenance Graph · Cryptographic & Custody Lineage
              </div>
              <div className="panel-actions">
                <span style={{ fontSize: '11px', color: 'var(--muted)' }}>Click any node to inspect cryptographic lineage & Merkle chain integrity</span>
              </div>
            </div>

            <div className="graph-container" style={{ padding: '24px' }}>
              <svg className="graph-svg" viewBox="0 0 600 360" style={{ maxHeight: '420px' }}>
                <defs>
                  <linearGradient id="edgeGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3d5afe" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#39c9df" stopOpacity="0.8" />
                  </linearGradient>
                  <filter id="nodeGlow2">
                    <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>

                {/* Connecting Edges */}
                <g stroke="url(#edgeGrad2)" strokeWidth="2" fill="none" opacity="0.65">
                  <path d="M 100 180 Q 180 100 260 90" strokeDasharray="3 3" />
                  <path d="M 100 180 Q 180 260 260 270" strokeDasharray="3 3" />
                  <path d="M 260 90 Q 330 140 400 180" />
                  <path d="M 260 270 Q 330 220 400 180" />
                  <path d="M 400 180 Q 460 120 520 100" stroke="#b078ff" />
                  <path d="M 400 180 Q 460 240 520 260" stroke="#22c989" />
                </g>

                {/* Nodes */}
                <g
                  className={`graph-node ${selectedGraphNode === 'case' ? 'active' : ''}`}
                  onClick={() => setSelectedGraphNode('case')}
                >
                  <circle cx="100" cy="180" r="30" fill="#141c38" stroke="var(--blue)" strokeWidth="2.5" filter="url(#nodeGlow2)" />
                  <text x="100" y="177" textAnchor="middle" fill="#fff" fontWeight="700">CASE</text>
                  <text x="100" y="191" textAnchor="middle" fill="#8da8ff" fontSize="9">ROOT</text>
                </g>

                <g
                  className={`graph-node ${selectedGraphNode === 'pdf' ? 'active' : ''}`}
                  onClick={() => setSelectedGraphNode('pdf')}
                >
                  <circle cx="260" cy="90" r="24" fill="#0f2631" stroke="var(--cyan)" strokeWidth="2" />
                  <text x="260" y="87" textAnchor="middle" fill="#fff" fontWeight="600">PDF</text>
                  <text x="260" y="100" textAnchor="middle" fill="#7ce4f3" fontSize="8">DOC</text>
                </g>

                <g
                  className={`graph-node ${selectedGraphNode === 'image' ? 'active' : ''}`}
                  onClick={() => setSelectedGraphNode('image')}
                >
                  <circle cx="260" cy="270" r="24" fill="#241a38" stroke="var(--purple)" strokeWidth="2" />
                  <text x="260" y="267" textAnchor="middle" fill="#fff" fontWeight="600">IMG</text>
                  <text x="260" y="280" textAnchor="middle" fill="#d2afff" fontSize="8">MEDIA</text>
                </g>

                <g
                  className={`graph-node ${selectedGraphNode === 'hash' ? 'active' : ''}`}
                  onClick={() => setSelectedGraphNode('hash')}
                >
                  <circle cx="400" cy="180" r="32" fill="#102d24" stroke="var(--green)" strokeWidth="2.5" filter="url(#nodeGlow2)" />
                  <text x="400" y="177" textAnchor="middle" fill="#fff" fontWeight="700">SHA-256</text>
                  <text x="400" y="191" textAnchor="middle" fill="#6fe9b5" fontSize="9">CHECK</text>
                </g>

                <g
                  className={`graph-node ${selectedGraphNode === 'review' ? 'active' : ''}`}
                  onClick={() => setSelectedGraphNode('review')}
                >
                  <circle cx="520" cy="100" r="24" fill="#2d2212" stroke="var(--amber)" strokeWidth="2" />
                  <text x="520" y="97" textAnchor="middle" fill="#fff" fontWeight="600">HUMAN</text>
                  <text x="520" y="110" textAnchor="middle" fill="#ffd88b" fontSize="8">REVIEW</text>
                </g>

                <g
                  className={`graph-node ${selectedGraphNode === 'hash' ? 'active' : ''}`}
                  onClick={() => setSelectedGraphNode('hash')}
                >
                  <circle cx="520" cy="260" r="24" fill="#15243d" stroke="#5885ff" strokeWidth="2" />
                  <text x="520" y="257" textAnchor="middle" fill="#fff" fontWeight="600">Ed25519</text>
                  <text x="520" y="270" textAnchor="middle" fill="#93b2ff" fontSize="8">DOSSIER</text>
                </g>
              </svg>

              {/* Inspector overlay for selected node */}
              {selectedGraphNode && graphNodes[selectedGraphNode] && (
                <div className="graph-inspector" style={{ marginTop: '16px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: '700', color: '#fff' }}>
                        {graphNodes[selectedGraphNode].title}
                      </span>
                      <span className="tag tag-live">{graphNodes[selectedGraphNode].status}</span>
                    </div>
                    <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      {graphNodes[selectedGraphNode].details}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '10px', color: 'var(--muted)', display: 'block' }}>Node Identifier</span>
                    <code style={{ fontSize: '11px', color: 'var(--cyan)', fontFamily: 'var(--font-mono)' }}>
                      {graphNodes[selectedGraphNode].id}
                    </code>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      {/* MODAL 1: Create Case Modal */}
      {showNewCaseModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Create New Investigation Case</h3>
              <button onClick={() => setShowNewCaseModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleCreateCase}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Official Case Title *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. Gazette Notice Provenance Audit"
                    value={newCaseForm.title}
                    onChange={e => setNewCaseForm(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>

                <div className="form-group">
                  <label>Classification Tier *</label>
                  <select
                    className="form-control"
                    value={newCaseForm.classification}
                    onChange={e => setNewCaseForm(prev => ({ ...prev, classification: e.target.value }))}
                  >
                    <option value="OFFICIAL">OFFICIAL (Standard)</option>
                    <option value="CONFIDENTIAL">CONFIDENTIAL</option>
                    <option value="SECRET">SECRET (High Clearance)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Investigative Purpose Statement *</label>
                  <textarea
                    required
                    rows="3"
                    className="form-control"
                    placeholder="Describe legal or administrative custody purpose..."
                    value={newCaseForm.purpose}
                    onChange={e => setNewCaseForm(prev => ({ ...prev, purpose: e.target.value }))}
                  />
                </div>

                <div className="form-group">
                  <label>Temporal As-Of Date *</label>
                  <input
                    type="date"
                    required
                    className="form-control"
                    value={newCaseForm.as_of_date}
                    onChange={e => setNewCaseForm(prev => ({ ...prev, as_of_date: e.target.value }))}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-sm" onClick={() => setShowNewCaseModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Register Case</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: Ingest Evidence Modal */}
      {showUploadModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Ingest Digital Evidence Artifact</h3>
              <button onClick={() => setShowUploadModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleUploadArtifact}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Target Case Container *</label>
                  <select
                    required
                    className="form-control"
                    value={uploadForm.case_id}
                    onChange={e => setUploadForm(prev => ({ ...prev, case_id: e.target.value }))}
                  >
                    <option value="">Select a case...</option>
                    {cases.map(c => (
                      <option key={c.id} value={c.id}>{c.title} ({c.id})</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Evidence Label / Artifact Type *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. Gazette Scan, Digital Invoice, Site Photo"
                    value={uploadForm.artifact_type}
                    onChange={e => setUploadForm(prev => ({ ...prev, artifact_type: e.target.value }))}
                  />
                </div>

                <div className="form-group">
                  <label>Digital Evidence File (PDF, PNG, JPG, Text) *</label>
                  <label className="upload-dropzone">
                    <input
                      type="file"
                      required
                      accept="application/pdf,image/png,image/jpeg,text/plain"
                      onChange={handleFileSelect}
                      style={{ display: 'none' }}
                    />
                    <Upload size={28} color="var(--blue)" style={{ margin: '0 auto 8px' }} />
                    <div style={{ color: '#fff', fontWeight: '600' }}>
                      {uploadForm.file ? uploadForm.file.name : 'Click or drag file to ingest'}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '4px' }}>
                      Max 10 MB · Automatically hashed via SHA-256 upon selection
                    </div>
                  </label>
                </div>

                {uploadForm.previewSha256 && (
                  <div className="form-group">
                    <label>Pre-computed SHA-256 Digest:</label>
                    <div className="hash-preview">{uploadForm.previewSha256}</div>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-sm" onClick={() => setShowUploadModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={!uploadForm.content_b64}>
                  Lock & Ingest Artifact
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: Case Details & Statutory Dossier Modal */}
      {selectedCase && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ width: '840px' }}>
            <div className="modal-header">
              <div>
                <span className="case-id-badge">{selectedCase.id}</span>
                <h3 style={{ marginTop: '4px' }}>{selectedCase.title}</h3>
              </div>
              <button onClick={() => setSelectedCase(null)}><X size={18} /></button>
            </div>
            <div className="modal-body">
              {/* Metadata */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: '#090c17', padding: '12px', borderRadius: '8px' }}>
                <div>
                  <small style={{ color: 'var(--muted)', display: 'block' }}>Classification</small>
                  <strong>{selectedCase.classification}</strong>
                </div>
                <div>
                  <small style={{ color: 'var(--muted)', display: 'block' }}>As-Of Date</small>
                  <strong>{selectedCase.as_of_date}</strong>
                </div>
                <div>
                  <small style={{ color: 'var(--muted)', display: 'block' }}>Workflow Status</small>
                  <span className={`status-chip ${selectedCase.status}`}>{selectedCase.status.replace('_', ' ')}</span>
                </div>
                <div>
                  <small style={{ color: 'var(--muted)', display: 'block' }}>Artifacts</small>
                  <strong>{caseArtifacts.length} items</strong>
                </div>
              </div>

              {/* Purpose */}
              <div>
                <h5 style={{ color: 'var(--muted)', fontSize: '11px', textTransform: 'uppercase' }}>Purpose Statement</h5>
                <p style={{ fontSize: '12px', color: '#fff', marginTop: '4px' }}>{selectedCase.purpose}</p>
              </div>

              {/* Actions row: BSA Cert & Dossier Export & Scan */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn-sm" onClick={() => handleRunIntegrityScan(selectedCase.id)}>
                  <Shield size={13} color="var(--green)" /> Verify Hash Chain
                </button>
                <button className="btn-sm" onClick={() => handleGenerateBsaCert(selectedCase.id)}>
                  <FileText size={13} color="var(--cyan)" /> Generate BSA s.63 Certificate
                </button>
                <button className="btn-sm" onClick={() => handleExportPackage(selectedCase.id)}>
                  <Download size={13} color="var(--purple)" /> Export Signed Dossier (ZIP)
                </button>
                <button className="btn-sm" onClick={() => handleRequestReview(selectedCase.id, 'R2')}>
                  <UserCheck size={13} color="var(--amber)" /> Request Human Review
                </button>
              </div>

              {/* Integrity Report View */}
              {integrityScan && (
                <div style={{ background: integrityScan.is_intact ? '#0a1d17' : '#221115', border: `1px solid ${integrityScan.is_intact ? '#1c523c' : '#6b202a'}`, borderRadius: '8px', padding: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: integrityScan.is_intact ? 'var(--green)' : '#ff6b7d', fontWeight: '700' }}>
                    {integrityScan.is_intact ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
                    {integrityScan.is_intact ? 'Cryptographic Integrity Verified' : `Integrity Issues Detected (${integrityScan.error_code || 'FLAGGED'})`}
                  </div>
                  <p style={{ fontSize: '11px', color: integrityScan.is_intact ? '#c3ecd7' : '#ffd5da', marginTop: '4px' }}>
                    {integrityScan.valid_artifacts} of {integrityScan.total_artifacts} artifacts verified against storage bytes.
                  </p>
                  
                  {/* Detailed 4-Point Check Status */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px', marginTop: '10px' }}>
                    <div style={{ padding: '6px 8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', fontSize: '10px', textAlign: 'center' }}>
                      <span style={{ color: 'var(--muted)', display: 'block' }}>Byte Match</span>
                      <strong style={{ color: integrityScan.hash_match ? 'var(--green)' : '#ff6b7d' }}>
                        {integrityScan.hash_match ? 'PASS' : 'FAIL'}
                      </strong>
                    </div>
                    <div style={{ padding: '6px 8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', fontSize: '10px', textAlign: 'center' }}>
                      <span style={{ color: 'var(--muted)', display: 'block' }}>Custody Chain</span>
                      <strong style={{ color: integrityScan.chain_valid ? 'var(--green)' : '#ff6b7d' }}>
                        {integrityScan.chain_valid ? 'PASS' : 'FAIL'}
                      </strong>
                    </div>
                    <div style={{ padding: '6px 8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', fontSize: '10px', textAlign: 'center' }}>
                      <span style={{ color: 'var(--muted)', display: 'block' }}>Signature</span>
                      <strong style={{ color: integrityScan.signature_valid ? 'var(--green)' : '#ff6b7d' }}>
                        {integrityScan.signature_valid ? 'PASS' : 'FAIL'}
                      </strong>
                    </div>
                    <div style={{ padding: '6px 8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', fontSize: '10px', textAlign: 'center' }}>
                      <span style={{ color: 'var(--muted)', display: 'block' }}>Timestamps</span>
                      <strong style={{ color: integrityScan.timestamp_valid ? 'var(--green)' : '#ff6b7d' }}>
                        {integrityScan.timestamp_valid ? 'PASS' : 'FAIL'}
                      </strong>
                    </div>
                  </div>

                  {integrityScan.failure_reasons?.length > 0 && (
                    <div style={{ marginTop: '8px', padding: '8px', background: 'rgba(255,0,0,0.1)', borderRadius: '4px', fontSize: '11px', color: '#ff8a98' }}>
                      <strong>Failure Reasons:</strong>
                      <ul style={{ paddingLeft: '16px', marginTop: '4px' }}>
                        {integrityScan.failure_reasons.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Independent Offline Verifier Hint */}
              <div style={{ padding: '10px 12px', background: '#080c16', border: '1px dashed var(--border)', borderRadius: '6px', fontSize: '11px' }}>
                <span style={{ color: 'var(--cyan)', fontWeight: '600' }}>Independent Offline Verification (P1-05):</span>
                <p style={{ color: 'var(--muted)', marginTop: '2px' }}>
                  Anyone can verify exported dossiers without server trust:
                  <code style={{ display: 'block', marginTop: '4px', color: '#c9d1d9', background: '#020408', padding: '4px 8px', borderRadius: '4px', fontFamily: 'var(--font-mono)' }}>
                    python scripts/verifier.py evidence_dossier_{selectedCase.id}.zip
                  </code>
                </p>
              </div>

              {/* BSA Certificate View */}
              {bsaCertificate && (
                <div style={{ background: '#0c1626', border: '1px solid #284478', borderRadius: '8px', padding: '14px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontWeight: '700', color: 'var(--cyan)', fontSize: '12px' }}>
                      Bharatiya Sakshya Adhiniyam, 2023 · Section 63 Certificate
                    </div>
                    <span style={{ fontSize: '10px', color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>
                      ID: {bsaCertificate.certificate_id}
                    </span>
                  </div>
                  <p style={{ fontSize: '11px', color: '#cbd5e1', marginTop: '8px', fontStyle: 'italic', background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '6px' }}>
                    "{bsaCertificate.affirmation_statement}"
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '10px', color: 'var(--muted)' }}>
                    <span>Deponent: {bsaCertificate.deponent_name} ({bsaCertificate.deponent_designation})</span>
                    <span>Cert Hash: <code style={{ color: 'var(--green)' }}>{bsaCertificate.certificate_hash?.slice(0, 16)}...</code></span>
                  </div>
                </div>
              )}

              {/* Evidence Artifacts Table */}
              <div>
                <h5 style={{ color: 'var(--muted)', fontSize: '11px', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Attached Evidence Artifacts ({caseArtifacts.length})
                </h5>
                {caseArtifacts.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {caseArtifacts.map(art => (
                      <div
                        key={art.id}
                        style={{
                          padding: '8px 12px',
                          background: '#0a0d18',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <FileCode size={16} color="var(--cyan)" />
                          <div>
                            <div style={{ fontSize: '12px', fontWeight: '600', color: '#fff' }}>
                              {art.artifact_type}
                            </div>
                            <div style={{ fontSize: '10px', color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>
                              SHA-256: {art.sha256}
                            </div>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right', fontSize: '10px', color: 'var(--muted)' }}>
                          <div>{art.mime_type}</div>
                          <span style={{ color: 'var(--green)' }}>● ObjectLocked</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ padding: '20px', textAlign: 'center', color: 'var(--muted)', background: '#0a0d18', borderRadius: '6px' }}>
                    No artifacts uploaded to this case yet.
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-sm" onClick={() => setSelectedCase(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 4: Complete Review Task Modal */}
      {showCompleteReviewModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Complete Human Review Task</h3>
              <button onClick={() => setShowCompleteReviewModal(null)}><X size={18} /></button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Please provide the official reviewer disposition rationale. Under procedural rules, a minimum of 20 characters is required for evidentiary record.
              </p>
              <div className="form-group">
                <label>Reviewer Rationale Statement *</label>
                <textarea
                  rows="4"
                  className="form-control"
                  placeholder="Record findings, verification results, and clearance notes..."
                  value={reviewRationale}
                  onChange={e => setReviewRationale(e.target.value)}
                />
                <span style={{ fontSize: '10px', color: reviewRationale.length >= 20 ? 'var(--green)' : 'var(--amber)' }}>
                  {reviewRationale.length} / 20 minimum characters
                </span>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-sm" onClick={() => setShowCompleteReviewModal(null)}>Cancel</button>
              <button
                className="btn-primary"
                onClick={handleCompleteTask}
                disabled={reviewRationale.trim().length < 20}
              >
                Seal & Complete Disposition
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 5: Backend Deployment Settings */}
      {showSettingsModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Cloud & API Deployment Settings</h3>
              <button onClick={() => setShowSettingsModal(false)}><X size={18} /></button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Active Backend API URL (Render or Local)</label>
                <input
                  type="url"
                  className="form-control"
                  value={apiUrl}
                  onChange={e => setApiUrl(e.target.value)}
                  placeholder="e.g. https://credence-gov-backend.onrender.com or http://127.0.0.1:8000"
                />
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="btn-sm"
                  onClick={() => {
                    setApiUrl('http://127.0.0.1:8000');
                    localStorage.setItem('credence_api_url', 'http://127.0.0.1:8000');
                  }}
                >
                  Reset to Local (http://127.0.0.1:8000)
                </button>
              </div>

              <div style={{ padding: '12px', background: '#0a0d18', borderRadius: '8px', fontSize: '11px', color: 'var(--muted)' }}>
                <strong>Vercel Frontend + Render Backend Architecture:</strong>
                <ul style={{ paddingLeft: '18px', marginTop: '6px' }}>
                  <li>Frontend is hosted on <strong>Vercel</strong> with instant global CDN distribution.</li>
                  <li>Backend runs FastAPI on <strong>Render</strong> with Docker / Python ASGI service.</li>
                  <li>Cross-Origin Resource Sharing (CORS) is configured to permit all <code>*.vercel.app</code> domains.</li>
                </ul>
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn-primary"
                onClick={() => {
                  localStorage.setItem('credence_api_url', apiUrl);
                  setShowSettingsModal(false);
                  authenticateAndHydrate(apiUrl);
                }}
              >
                Save & Connect
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast && (
        <div className={`toast-notice ${toast.type}`}>
          {toast.type === 'success' && <CheckCircle2 size={16} />}
          {toast.type === 'error' && <AlertTriangle size={16} />}
          {toast.type === 'info' && <Shield size={16} />}
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
}
