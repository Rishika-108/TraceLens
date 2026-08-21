import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  FiUploadCloud,
  FiFile,
  FiCheckCircle,
  FiAlertTriangle,
  FiPhone,
  FiMessageSquare,
  FiMail,
  FiGlobe,
  FiFileText,
  FiImage,
} from 'react-icons/fi';
import { evidenceService } from '../../services/evidence';

const EVIDENCE_CATEGORIES = [
  { id: '', label: 'Auto Sniff & Detect', icon: FiFile },
  { id: 'WHATSAPP', label: 'WhatsApp Chat (.txt)', icon: FiMessageSquare },
  { id: 'CALL', label: 'Call Records (.csv/.json)', icon: FiPhone },
  { id: 'SMS', label: 'SMS Messages (.csv/.json)', icon: FiMessageSquare },
  { id: 'EMAIL', label: 'Email Archive (.eml/.json)', icon: FiMail },
  { id: 'BROWSER_HISTORY', label: 'Browser History (SQLite/CSV)', icon: FiGlobe },
  { id: 'DOCUMENT', label: 'Document (.pdf/.txt/.md)', icon: FiFileText },
  { id: 'IMAGE_METADATA', label: 'Image EXIF (.jpg/.png)', icon: FiImage },
];

export const EvidenceUpload = ({ caseId, onUploadSuccess }) => {
  const [fileType, setFileType] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0]);
        setError(null);
        setSuccess(null);
      }
    },
  });

  const handleUpload = async () => {
    if (!selectedFile || !caseId) return;
    setUploading(true);
    setProgress(0);
    setError(null);
    setSuccess(null);

    try {
      const result = await evidenceService.uploadEvidence(
        caseId,
        selectedFile,
        fileType || null,
        (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percent);
        }
      );

      setSuccess(`Evidence "${selectedFile.name}" ingested successfully!`);
      setSelectedFile(null);
      if (onUploadSuccess) onUploadSuccess(result);
    } catch (err) {
      console.error('Evidence upload failed', err);
      setError(err.response?.data?.detail || 'Upload or forensic parsing failed. Please verify file integrity.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 text-left">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <FiUploadCloud className="text-cyan-400 w-5 h-5" />
            Ingest Forensic Evidence
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Streaming upload with automated SHA-256 cryptographic hashing and multi-format parsing.
          </p>
        </div>
      </div>

      {/* Evidence Type Category Selector */}
      <div className="mb-4">
        <label className="block text-xs font-mono font-medium text-slate-400 mb-2">
          EVIDENCE PARSER HINT (OPTIONAL)
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {EVIDENCE_CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = fileType === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => setFileType(cat.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium border transition-all text-left truncate ${
                  isSelected
                    ? 'bg-cyan-500/15 border-cyan-500/50 text-cyan-300 shadow-sm shadow-cyan-500/20'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span className="truncate">{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Drag and Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-cyan-400 bg-cyan-500/10'
            : selectedFile
            ? 'border-emerald-500/50 bg-emerald-500/5'
            : 'border-slate-700/80 hover:border-slate-600 bg-slate-900/40 hover:bg-slate-900/60'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/10">
            <FiUploadCloud className="w-6 h-6" />
          </div>

          {selectedFile ? (
            <div>
              <div className="text-sm font-semibold text-emerald-400 flex items-center justify-center gap-1.5">
                <FiCheckCircle className="w-4 h-4" />
                {selectedFile.name}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-1">
                Size: {(selectedFile.size / 1024).toFixed(1)} KB • Click or drag to replace
              </div>
            </div>
          ) : (
            <div>
              <div className="text-sm font-semibold text-slate-200">
                Drag & Drop evidence file here, or <span className="text-cyan-400 underline underline-offset-4">browse files</span>
              </div>
              <div className="text-xs text-slate-500 mt-1">
                Supports WhatsApp (.txt), Call/SMS (.csv, .json), Email (.eml), SQLite history, PDFs & Images
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {uploading && (
        <div className="mt-4 space-y-1.5">
          <div className="flex justify-between text-xs font-mono text-cyan-400">
            <span>Uploading & Parsing Artifacts...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Success / Error alerts */}
      {success && (
        <div className="mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <FiCheckCircle className="w-4 h-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}
      {error && (
        <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
          <FiAlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Button */}
      {selectedFile && !uploading && (
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleUpload}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2"
          >
            <FiUploadCloud className="w-4 h-4" />
            Ingest & Run Pipeline
          </button>
        </div>
      )}
    </div>
  );
};
