"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Briefcase,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Download,
  Mail,
  Zap,
} from "lucide-react";

export default function Dashboard() {
  const [userId, setUserId] = useState(1);
  const [searching, setSearching] = useState(false);
  const [bulkApplying, setBulkApplying] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [keywords, setKeywords] = useState(
    "Software Engineer, Full Stack Developer, Backend Developer, Frontend Developer, Java Developer"
  );
  const [location, setLocation] = useState("Remote");

  useEffect(() => {
    if (userId) {
      loadApplications(userId);
    }
  }, [userId]);

  const loadApplications = async (uid) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/applications/user/${uid}`
      );
      const data = await response.json();
      if (data.applications) {
        setApplications(data.applications);
      }
    } catch (err) {
      console.error("Failed to load applications:", err);
    }
  };

  const searchJobs = async () => {
    if (!userId) {
      alert("Please upload your resume first");
      return;
    }

    setSearching(true);

    try {
      const response = await fetch("http://localhost:8000/api/jobs/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          keywords: keywords.split(",").map((k) => k.trim()),
          location: location,
          remote_only: location.toLowerCase().includes("remote"),
          limit: 5000,
          sources: ["all"],
        }),
      });

      const data = await response.json();

      if (data.jobs) {
        setJobs(data.jobs);
        alert(
          `✅ Found ${data.jobs.length} jobs! Click "Apply to All" to generate Gmail-ready CSV.`
        );
      }
    } catch (err) {
      alert("Failed to search jobs. Make sure backend is running.");
    } finally {
      setSearching(false);
    }
  };

  const bulkApplyAll = async () => {
    if (!userId || jobs.length === 0) return;

    const confirmed = confirm(
      `🚀 Apply to all ${jobs.length} jobs?\n\nThis will:\n1. Create applications for all jobs\n2. Generate Gmail Merge compatible CSV\n3. Take ~30-60 seconds\n\nAfter completion, download CSV and send with Gmail!`
    );

    if (!confirmed) return;

    setBulkApplying(true);

    try {
      const jobIds = jobs.map((j) => j.id);

      const response = await fetch(
        "http://localhost:8000/api/applications/bulk-apply",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            job_ids: jobIds,
          }),
        }
      );

      const data = await response.json();

      alert(
        `✅ SUCCESS! Applied to ${data.total_applications} jobs!\n\n📧 Next: Click "Download CSV" below and send with Gmail Merge!`
      );

      await loadApplications(userId);

      setTimeout(() => {
        document
          .getElementById("export-section")
          ?.scrollIntoView({ behavior: "smooth" });
      }, 500);
    } catch (err) {
      alert("Error bulk applying: " + err);
    } finally {
      setBulkApplying(false);
    }
  };

  const downloadCSV = async () => {
    if (!userId) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/applications/export-csv/${userId}`
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `job_applications_${
          new Date().toISOString().split("T")[0]
        }.csv`;
        a.click();

        alert(
          `✅ CSV Downloaded!\n\n✓ Clean emails: careers@company.com\n✓ Gmail Merge compatible\n\nOpen in Google Sheets and use YAMM to send!`
        );
      } else {
        alert("No pending applications to export");
      }
    } catch (err) {
      alert("Error downloading CSV");
    }
  };

  const stats = {
    totalJobs: jobs.length,
    totalApplications: applications.length,
    pending: applications.filter(
      (a) => a.status === "pending" || a.status === "email_ready"
    ).length,
    applied: applications.filter((a) => a.status === "applied").length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Job Application Dashboard
              </h1>
              <p className="text-gray-500 mt-1">
                Apply to 5000+ jobs with Gmail Merge 🚀
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6 p-4 bg-green-50 border-2 border-green-200 rounded-lg">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-green-900 mb-2">
                ✅ CSV FORMAT FIXED - Gmail Merge Compatible!
              </h3>
              <p className="text-sm text-green-800">
                <strong>NEW:</strong> Clean single emails per row
                (careers@company.com). No brackets or multiple addresses. Works
                with Gmail Merge, YAMM, Mailchimp!
              </p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Jobs Found</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats.totalJobs}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Briefcase className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Applications</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats.totalApplications}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Ready to Send</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats.pending}
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Sent</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats.applied}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">
            🔍 Step 1: Search 5000+ Jobs
          </h2>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords (comma-separated)
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                💡 Add 5-10 keywords to find 5000+ jobs from LinkedIn, Indeed,
                RemoteOK
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <button
            onClick={searchJobs}
            disabled={searching}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-300 flex items-center justify-center"
          >
            {searching ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Searching 5000+ jobs...
              </>
            ) : (
              <>
                <Search className="w-5 h-5 mr-2" />
                Search 5000+ Jobs (LinkedIn + Indeed + More)
              </>
            )}
          </button>
        </div>

        {jobs.length > 0 && (
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl shadow-lg p-6 mb-8 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">
                  🚀 Step 2: Apply to All Jobs
                </h2>
                <p className="text-purple-100">
                  Found {jobs.length} jobs - Generate Gmail Merge compatible
                  CSV!
                </p>
                <p className="text-sm text-purple-200 mt-2">
                  ⚡ Takes 30-60 seconds • Works with Gmail, Mailchimp, YAMM
                </p>
              </div>
              <button
                onClick={bulkApplyAll}
                disabled={bulkApplying}
                className="px-8 py-4 bg-white text-purple-600 rounded-lg font-bold text-lg hover:bg-purple-50 disabled:bg-gray-300 flex items-center gap-3 shadow-xl"
              >
                {bulkApplying ? (
                  <>
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
                    Applying...
                  </>
                ) : (
                  <>
                    <Zap className="w-6 h-6" />
                    Apply to All {jobs.length} Jobs
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {applications.length > 0 && (
          <div
            id="export-section"
            className="bg-white rounded-xl shadow-sm p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">
                📧 Step 3: Download CSV ({applications.length})
              </h2>

              <button
                onClick={downloadCSV}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-bold flex items-center gap-2 shadow-lg"
              >
                <Download className="w-5 h-5" />
                Download CSV ({stats.pending} Ready)
              </button>
            </div>

            <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg">
              <div className="flex items-start gap-3">
                <Mail className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-bold text-green-900 mb-3 text-lg">
                    🎯 Send {stats.pending} Emails in 10 Minutes
                  </h3>

                  <div className="space-y-3 text-sm text-green-800">
                    <div className="bg-white p-3 rounded border border-green-200">
                      <p className="font-bold mb-2">✅ CSV Format (FIXED):</p>
                      <p className="ml-2">
                        • Clean single emails: careers@company.com
                      </p>
                      <p className="ml-2">
                        • No brackets or multiple addresses
                      </p>
                      <p className="ml-2">• Works with all mail merge tools</p>
                    </div>

                    <div className="space-y-2">
                      <p>
                        <span className="font-bold text-green-600">1.</span>{" "}
                        Click "Download CSV" button above
                      </p>
                      <p>
                        <span className="font-bold text-green-600">2.</span>{" "}
                        Open CSV in Google Sheets
                      </p>
                      <p>
                        <span className="font-bold text-green-600">3.</span>{" "}
                        Install "Yet Another Mail Merge" (YAMM) add-on
                      </p>
                      <p>
                        <span className="font-bold text-green-600">4.</span> Map
                        columns: "To Email" → Recipients, "Subject" → Subject,
                        "Message Body" → Body
                      </p>
                      <p>
                        <span className="font-bold text-green-600">5.</span>{" "}
                        <strong>Click "Send emails" - Done! 🎉</strong>
                      </p>
                    </div>

                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                      <p className="text-sm text-yellow-800">
                        <strong>⚡ Pro Tips:</strong> YAMM free: 50 emails/day •
                        For 500+: Use Mailchimp (500 free) or SendGrid • Split
                        CSV into batches if needed
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {applications.map((app) => (
                <div
                  key={app.id}
                  className="border rounded-lg p-4 flex items-center justify-between hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">
                      {app.job_title}
                    </h4>
                    <p className="text-sm text-gray-500">{app.company}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(app.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    {app.match_score && (
                      <span className="text-sm text-gray-600">
                        {app.match_score.toFixed(0)}%
                      </span>
                    )}
                    {app.status === "applied" && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                    {(app.status === "pending" ||
                      app.status === "email_ready") && (
                      <Clock className="w-5 h-5 text-yellow-500" />
                    )}
                    {app.status === "failed" && (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className="text-sm font-medium capitalize text-gray-700 min-w-20">
                      {app.status === "email_ready" ? "Ready" : app.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
