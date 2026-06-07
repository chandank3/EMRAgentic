import React, { useState, useEffect } from 'react';
import { ClipboardCheck, CheckCircle, XCircle, Clock } from 'lucide-react';

export default function Approvals({ apiBase }) {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`${apiBase}/api/approvals/pending`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch approvals');
        return res.json();
      })
      .then(data => {
        setApprovals(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [apiBase]);

  if (loading) return <div className="p-8 text-gray-500">Loading pending approvals...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Pending Approvals</h1>
      </div>

      {approvals.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <ClipboardCheck className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          <p className="text-gray-500">No pending approvals at the moment.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {approvals.map((approval) => (
            <div key={approval.id} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-4">
                  <div className="bg-yellow-100 p-3 rounded-lg">
                    <ClipboardCheck className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Care Plan Approval
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                      <Clock className="h-4 w-4" />
                      Requested on: {new Date(approval.requested_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="flex items-center gap-1 bg-green-50 text-green-700 px-3 py-1.5 rounded hover:bg-green-100 transition text-sm font-medium">
                    <CheckCircle className="h-4 w-4" /> Approve
                  </button>
                  <button className="flex items-center gap-1 bg-red-50 text-red-700 px-3 py-1.5 rounded hover:bg-red-100 transition text-sm font-medium">
                    <XCircle className="h-4 w-4" /> Reject
                  </button>
                </div>
              </div>
              <div className="bg-gray-50 rounded p-4 text-sm text-gray-700">
                <span className="font-semibold block mb-1">Details:</span>
                <pre className="whitespace-pre-wrap font-sans text-xs text-gray-600">
                  {JSON.stringify(approval.request_data, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
