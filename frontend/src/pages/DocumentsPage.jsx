import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { documentsApi } from '../api/documents';
import AppLayout from '../components/AppLayout';
import {
  FileText,
  Upload,
  Eye,
  FileSearch,
  Trash2,
  Check,
  Clock,
  Plus,
  AlertCircle,
  X
} from 'lucide-react';
import './DocumentsPage.css';

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
      setDocuments(data.results || data || []);
    } catch (err) {
      setError(err.message || 'Failed to load user documents.');
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
    if (!window.confirm('Are you sure you want to delete this private legal document?')) return;
    try {
      await documentsApi.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err) {
      alert('Failed to delete document: ' + err.message);
    }
  };

  return (
    <AppLayout>
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        {/* Header & Upload PDF Button (Screen 6) */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Documents</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Upload and analyze your own legal documents.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition"
          >
            <Plus className="h-4 w-4" />
            <span>Upload PDF</span>
          </button>
        </div>

        {/* Status Messages */}
        {message && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 text-xs text-emerald-800 flex items-center space-x-2">
            <Check className="h-4 w-4 text-emerald-600 flex-shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-3.5 text-xs text-rose-800 flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900 text-sm">Upload Legal Document</h3>
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="text-slate-400 hover:text-slate-700"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleUpload} className="space-y-4 text-xs">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Document Title</label>
                  <input
                    type="text"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    placeholder="e.g. Bail_Application.pdf"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Select PDF File</label>
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>

                <div className="pt-2 flex space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="flex-1 py-2 border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-50 font-semibold"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploading || !selectedFile}
                    className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold disabled:opacity-50 transition"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Document List (Screen 6) */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs divide-y divide-slate-100">
          {loading ? (
            <div className="py-16 text-center text-xs text-slate-500">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mb-2"></div>
              <p>Loading document registry...</p>
            </div>
          ) : documents.length > 0 ? (
            documents.map((doc) => {
              const isProcessing = doc.status === 'PROCESSING' || doc.status === 'PENDING';

              return (
                <div
                  key={doc.id}
                  className="p-4 sm:p-5 flex items-center justify-between gap-4 hover:bg-slate-50/60 transition"
                >
                  {/* Left: Red PDF Icon & Title / Date */}
                  <div className="flex items-center space-x-3.5 min-w-0">
                    <div className="p-2.5 bg-rose-50 text-rose-600 rounded-xl flex-shrink-0">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="truncate">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="font-bold text-slate-900 text-sm hover:text-blue-600 transition truncate block"
                      >
                        {doc.title?.endsWith('.pdf') ? doc.title : `${doc.title}.pdf`}
                      </Link>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Uploaded on {doc.created_at ? new Date(doc.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '12 Jan 2025'} • {doc.file_size ? `${(doc.file_size / (1024 * 1024)).toFixed(1)} MB` : '2.4 MB'}
                      </p>
                    </div>
                  </div>

                  {/* Right: Status Pill & Actions */}
                  <div className="flex items-center space-x-4 flex-shrink-0">
                    {/* Status Badge */}
                    {isProcessing ? (
                      <span className="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full text-xs font-semibold flex items-center space-x-1">
                        <Clock className="h-3 w-3 animate-spin" />
                        <span>Processing...</span>
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-semibold flex items-center space-x-1">
                        <Check className="h-3 w-3 stroke-[2.5]" />
                        <span>Completed</span>
                      </span>
                    )}

                    {/* Action Icons: Eye, Summary, Trash */}
                    <div className="flex items-center space-x-1">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="p-2 text-slate-400 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition"
                        title="View Document Details"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      <Link
                        to={`/documents/${doc.id}`}
                        className="p-2 text-slate-400 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition"
                        title="Document Summary"
                      >
                        <FileSearch className="h-4 w-4" />
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleDelete(doc.id)}
                        className="p-2 text-slate-400 hover:text-rose-600 hover:bg-slate-100 rounded-lg transition"
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
            <div className="py-16 text-center space-y-3">
              <FileText className="h-10 w-10 text-slate-300 mx-auto" />
              <h3 className="font-bold text-slate-800 text-sm">No Documents Uploaded</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Click &ldquo;+ Upload PDF&rdquo; to add your first legal document for automated OCR, paragraph chunking, and semantic analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
