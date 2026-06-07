import React, { useState, useEffect } from 'react';
import { ClipboardList, Target, Activity, Clock } from 'lucide-react';

export default function CarePlans({ apiBase, patientId }) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!patientId) return;
    
    setLoading(true);
    fetch(`${apiBase}/api/care-plans/${patientId}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch care plans');
        return res.json();
      })
      .then(data => {
        setPlans(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [apiBase, patientId]);

  if (loading) return <div className="p-8 text-gray-500">Loading care plans...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Care Plans</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          Create Plan
        </button>
      </div>

      {plans.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <ClipboardList className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          <p className="text-gray-500">No care plans active.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 hover:shadow-md transition">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-100 p-2 rounded-lg">
                    <ClipboardList className="h-6 w-6 text-purple-700" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">{plan.title}</h3>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${
                  plan.status === 'active' ? 'bg-green-100 text-green-800' :
                  plan.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {plan.status.replace('_', ' ')}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 border-t border-gray-100 pt-4">
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                    <Target className="h-4 w-4" /> Goals
                  </h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {plan.goals.map((goal, idx) => (
                      <li key={idx}>{goal}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                    <Activity className="h-4 w-4" /> Interventions
                  </h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {plan.interventions.map((intv, idx) => (
                      <li key={idx}>{intv}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-400 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Created: {new Date(plan.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
