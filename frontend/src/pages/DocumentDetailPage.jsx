import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { documentsApi } from '../api/documents';
import AppLayout from '../components/AppLayout';
import {
  FileText,
  Trash2,
  AlertCircle,
  Copy,
  Check,
  Download,
  BookOpen
} from 'lucide-react';
import './DocumentDetailPage.css';

export default function DocumentDetailPage() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchDoc() {
      setLoading(true);
      setError(null);
      try {
        const [docData, summaryData] = await Promise.all([
          documentsApi.getDocumentDetail(id),
          documentsApi.getDocumentSummary(id).catch(() => null),
        ]);
        setDoc(docData);
        setSummary(summaryData);
      } catch (err) {
        setError(err.message || 'Failed to load document analysis.');
      } finally {
        setLoading(false);
      }
    }
    fetchDoc();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentsApi.deleteDocument(id);
      navigate('/documents');
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const copyText = () => {
    if (doc?.extracted_text) {
      navigator.clipboard.writeText(doc.extracted_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="doc-detail-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <div className="search-spinner" style={{ margin: '0 auto 1rem auto' }}></div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>Analyzing document extraction & chunks...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !doc) {
    return (
      <AppLayout>
        <div className="doc-detail-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto mb-3" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>Document Not Found</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>{error || 'This document could not be retrieved.'}</p>
          <Link
            to="/documents"
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary-navy)',
              color: '#ffffff',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              fontSize: '0.8125rem',
              fontWeight: 600,
            }}
          >
            Return to Documents
          </Link>
        </div>
      </AppLayout>
    );
  }

  const isCompleted = doc.status === 'COMPLETED';

  return (
    <AppLayout>
      <div className="doc-detail-container">
        {/* Breadcrumb Navigation */}
        <nav className="doc-detail-breadcrumb">
          <Link to="/documents">My Documents</Link>
          <span className="separator">&gt;</span>
          <span className="current">{doc.title}</span>
        </nav>

        {/* Header Card */}
        <div className="doc-detail-header-card">
          <div className="doc-detail-left-info">
            <div className="doc-detail-icon-box">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h1 className="doc-detail-title">
                {doc.title?.toLowerCase().endsWith('.pdf') ? doc.title : `${doc.title}.pdf`}
              </h1>
              <div className="doc-detail-meta">
                <span>{doc.file_size ? `${(doc.file_size / (1024 * 1024)).toFixed(2)} MB` : 'PDF Document'}</span>
                <span>•</span>
                <span>{doc.page_count || 1} pages</span>
                <span>•</span>
                <span className={`doc-detail-status-pill ${isCompleted ? 'completed' : 'processing'}`}>
                  {doc.status || 'COMPLETED'}
                </span>
              </div>
            </div>
          </div>

          <div className="doc-detail-header-actions">
            {doc.file && (
              <a
                href={doc.file}
                target="_blank"
                rel="noopener noreferrer"
                className="doc-detail-btn-download"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Download PDF</span>
              </a>
            )}
            <button
              type="button"
              onClick={handleDelete}
              className="doc-detail-btn-delete"
              title="Delete Document"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* AI Summary Card (if available) */}
        {summary && (
          <div className="doc-detail-card">
            <h3 className="doc-detail-card-title">
              <BookOpen className="h-4 w-4 text-blue-600" />
              <span>Automated Legal Analysis &amp; Abstract</span>
            </h3>
            <p className="doc-detail-summary-box">
              {summary.summary || summary.text || 'Document analysis successfully indexed into private vector space.'}
            </p>
          </div>
        )}

        {/* Extracted Text Pane */}
        <div className="doc-detail-card">
          <div className="doc-detail-card-header">
            <h3 className="doc-detail-card-title">Extracted Text Content</h3>
            <button
              type="button"
              onClick={copyText}
              className="doc-detail-btn-copy"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Text'}</span>
            </button>
          </div>

          <div className="doc-detail-extracted-text">
            {doc.extracted_text || 'No extracted text available yet.'}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
