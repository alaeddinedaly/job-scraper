"use client";

import { useState } from "react";
import {
  Upload,
  CheckCircle,
  AlertCircle,
  FileText,
  Briefcase,
} from "lucide-react";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/resume/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        // Store user ID in localStorage for later use
        localStorage.setItem("userId", data.user_id);
        localStorage.setItem("resumeId", data.resume_id);
      } else {
        setError(data.detail || "Upload failed");
      }
    } catch (err) {
      setError(
        "Failed to connect to server. Make sure the backend is running."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Briefcase className="w-12 h-12 text-indigo-600 mr-3" />
            <h1 className="text-5xl font-bold text-gray-900">AutoJobApply</h1>
          </div>
          <p className="text-xl text-gray-600">
            Automated Job Applications • 100% Free & Open Source
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Upload your resume once, apply to hundreds of jobs automatically
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">
            Step 1: Upload Your Resume
          </h2>

          <div className="space-y-6">
            {/* File Input */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors">
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
                className="hidden"
                id="resume-upload"
              />
              <label
                htmlFor="resume-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="w-16 h-16 text-gray-400 mb-4" />
                <span className="text-lg font-medium text-gray-700">
                  {file ? file.name : "Choose resume file"}
                </span>
                <span className="text-sm text-gray-500 mt-2">
                  PDF, DOCX, or DOC (max 10MB)
                </span>
              </label>
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full bg-indigo-600 text-white py-4 rounded-lg font-semibold text-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Parsing Resume...
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5 mr-2" />
                  Parse Resume
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-800 font-medium">Error</p>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Success Result */}
          {result && (
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-start mb-4">
                <CheckCircle className="w-6 h-6 text-green-600 mr-3 flex-shrink-0" />
                <div>
                  <p className="text-green-800 font-semibold text-lg">
                    Resume Parsed Successfully!
                  </p>
                  <p className="text-green-600 text-sm mt-1">
                    {result.message}
                  </p>
                </div>
              </div>

              {/* Parsed Data Preview */}
              <div className="grid grid-cols-2 gap-4 mt-6 bg-white rounded-lg p-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase">Name</p>
                  <p className="font-medium">
                    {result.parsed_data.name || "Not detected"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Email</p>
                  <p className="font-medium">
                    {result.parsed_data.email || "Not detected"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">
                    Skills Found
                  </p>
                  <p className="font-medium">
                    {result.parsed_data.skills?.length || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Experiences</p>
                  <p className="font-medium">
                    {result.parsed_data.num_experiences || 0}
                  </p>
                </div>
              </div>

              {/* Next Steps */}
              <div className="mt-6 pt-6 border-t border-green-200">
                <p className="text-green-800 font-medium mb-4">Next Steps:</p>
                <div className="space-y-2">
                  <a
                    href="/dashboard"
                    className="block w-full bg-green-600 text-white py-3 rounded-lg font-semibold text-center hover:bg-green-700 transition-colors"
                  >
                    Go to Dashboard →
                  </a>
                  <button
                    onClick={() => {
                      setFile(null);
                      setResult(null);
                    }}
                    className="block w-full bg-white text-green-600 py-3 rounded-lg font-semibold border-2 border-green-600 hover:bg-green-50 transition-colors"
                  >
                    Upload Different Resume
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Smart Parsing</h3>
            <p className="text-gray-600 text-sm">
              AI-powered resume parser extracts skills, experience, and
              education
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Briefcase className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Job Matching</h3>
            <p className="text-gray-600 text-sm">
              NLP algorithms match you with relevant jobs across multiple
              platforms
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <CheckCircle className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Auto-Apply</h3>
            <p className="text-gray-600 text-sm">
              Automated form filling applies to jobs while you focus on
              interviews
            </p>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>
            🔓 100% Free & Open Source • No API Keys Required • Privacy-First
          </p>
          <p className="mt-2">
            Data stays on your machine • No tracking • No ads
          </p>
        </div>
      </div>
    </div>
  );
}
