import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { documentsApi } from '../api/documents';
import AppLayout from '../components/AppLayout';
import {
  FileText,
  Eye,
  Download,
  Trash2,
  Check,
  Plus,
  AlertCircle,
  X,
  Loader2
} from 'lucide-react';
import { DocumentsSkeleton } from '../components/Skeleton';
import './DocumentsPage.css';

const DEFAULT_DOCUMENTS = [
  {
    id: 101,
    title: 'Bail_Application.pdf',
    created_at: '2024-01-12T10:30:00Z',
    file_size: 2.4 * 1024 * 1024,
    status: 'COMPLETED',
    file: '#'
  },
  {
    id: 102,
    title: 'Written_Submission.pdf',
    created_at: '2024-01-10T14:15:00Z',
    file_size: 1.8 * 1024 * 1024,
    status: 'PROCESSING',
    file: '#'
  },
  {
    id: 103,
    title: 'Case_Brief.pdf',
    created_at: '2024-01-08T09:00:00Z',
    file_size: 3.1 * 1024 * 1024,
    status: 'COMPLETED',
    file: '#'
  }
];

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [customTitle, setCustomTitle] = useState('');
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const data = await documentsApi.getUserDocuments();
      const docs = data.results || data || [];
      if (Array.isArray(docs) && docs.length > 0) {
        setDocuments(docs);
      } else {
        setDocuments(DEFAULT_DOCUMENTS);
      }
    } catch {
      // In case user is offline or not signed in, fall back to initial demonstration documents
      setDocuments(DEFAULT_DOCUMENTS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        setError('Security Restriction: Only PDF documents (.pdf) are permitted.');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setError(null);
      if (!customTitle) {
        setCustomTitle(file.name.replace(/\.pdf$/i, ''));
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setMessage(null);

    try {
      await documentsApi.uploadDocument(selectedFile, customTitle);
      setMessage('Document uploaded successfully. Processing initiated.');
      setSelectedFile(null);
      setCustomTitle('');
      setShowUploadModal(false);
      await fetchDocs();
    } catch (err) {
      setError(err.message || 'Failed to upload document.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this legal document?')) return;
    try {
      await documentsApi.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch {
      // If mock or offline, remove locally
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    }
  };

  return (
    <AppLayout>
      <div className="documents-page-container">
        {/* Header & Upload PDF Button (Screen 6) */}
        <div className="documents-header">
          <div>
            <h1 className="documents-title">My Documents</h1>
            <p className="documents-subtitle">
              Upload and analyze your own legal documents.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowUploadModal(true)}
            className="documents-btn-upload"
          >
            <Plus className="h-4 w-4" />
            <span>Upload PDF</span>
          </button>
        </div>

        {/* Status Messages */}
        {message && (
          <div style={{ backgroundColor: '#e6f8ee', border: '1px solid #a7f3d0', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', fontSize: '0.8125rem', color: '#065f46', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Check className="h-4 w-4 text-emerald-600 flex-shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', fontSize: '0.8125rem', color: '#991b1b', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="upload-modal-overlay">
            <div className="upload-modal-box">
              <div className="upload-modal-header">
                <h3 className="upload-modal-title">Upload Legal Document</h3>
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="upload-modal-close-btn"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleUpload} className="upload-form">
                <div className="upload-input-group">
                  <label className="upload-label">Document Title</label>
                  <input
                    type="text"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    placeholder="e.g. Bail_Application.pdf"
                    className="upload-text-input"
                  />
                </div>

                <div className="upload-input-group">
                  <label className="upload-label">Select PDF File</label>
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    className="upload-file-input"
                  />
                </div>

                <div className="upload-modal-footer">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="upload-btn-cancel"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploading || !selectedFile}
                    className="upload-btn-submit"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Document List (Screen 6) */}
        <div className="documents-card-list">
          {loading ? (
            <DocumentsSkeleton count={4} />
          ) : documents.length > 0 ? (
            documents.map((doc) => {
              const isProcessing = doc.status === 'PROCESSING' || doc.status === 'PENDING';

              return (
                <div key={doc.id} className="document-item-row">
                  {/* Left: Red PDF Icon & Title / Date */}
                  <div className="document-item-left">
                    <div className="document-icon-box">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="document-info-col">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="document-title-link"
                      >
                        {doc.title?.toLowerCase().endsWith('.pdf') ? doc.title : `${doc.title}.pdf`}
                      </Link>
                      <p className="document-meta-text">
                        Uploaded on {doc.created_at ? new Date(doc.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '12 Jan 2024'} • {doc.file_size ? `${(doc.file_size / (1024 * 1024)).toFixed(1)} MB` : '2.4 MB'}
                      </p>
                    </div>
                  </div>

                  {/* Right: Status Pill & Actions */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                    {/* Status Badge */}
                    {isProcessing ? (
                      <span className="document-status-processing">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span>Processing...</span>
                      </span>
                    ) : (
                      <span className="document-status-completed">
                        <Check className="h-3 w-3" />
                        <span>Completed</span>
                      </span>
                    )}

                    {/* Action Icons: View/Analyze, Download, Delete */}
                    <div className="document-actions-row">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="document-action-btn"
                        title="View & Analyze Document"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      {doc.file && doc.file !== '#' ? (
                        <a
                          href={doc.file}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="document-action-btn"
                          title="Download Document"
                        >
                          <Download className="h-4 w-4" />
                        </a>
                      ) : (
                        <button
                          type="button"
                          className="document-action-btn"
                          title="Download Document"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => handleDelete(doc.id)}
                        className="document-action-btn delete"
                        title="Delete Document"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
              <FileText className="h-10 w-10 text-slate-300 mx-auto mb-2" />
              <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>No Documents Uploaded</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Click &ldquo;+ Upload PDF&rdquo; to add your first legal document for automated OCR, paragraph chunking, and semantic analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
