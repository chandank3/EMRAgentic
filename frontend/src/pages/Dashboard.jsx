import React, { useState, useEffect } from 'react';
import { Users, Calendar, ClipboardList, Activity, ShieldAlert, ClipboardCheck } from 'lucide-react';

export default function Dashboard({ apiBase, patientId }) {
  const [stats, setStats] = useState({ appointments: 0, carePlans: 0, pendingApprovals: 0, recentAudits: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    
    setLoading(true);
    // Fetch multiple endpoints in parallel
    Promise.all([
      fetch(`${apiBase}/api/appointments/${patientId}`).then(r => r.ok ? r.json() : []),
      fetch(`${apiBase}/api/care-plans/${patientId}`).then(r => r.ok ? r.json() : []),
      fetch(`${apiBase}/api/approvals/pending`).then(r => r.ok ? r.json() : []),
      fetch(`${apiBase}/api/audit/logs?limit=5`).then(r => r.ok ? r.json() : [])
    ])
    .then(([appointments, plans, approvals, audits]) => {
      setStats({
        appointments: appointments.length || 0,
        carePlans: plans.length || 0,
        pendingApprovals: approvals.length || 0,
        recentAudits: audits.length || 0
      });
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [apiBase, patientId]);

  if (loading) return <div className="p-8 text-gray-500">Loading dashboard...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-600">Overview of patient coordination activities.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm flex items-center gap-4">
          <div className="bg-blue-100 p-3 rounded-lg"><Calendar className="h-6 w-6 text-blue-600" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Appointments</p>
            <p className="text-2xl font-bold text-gray-900">{stats.appointments}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm flex items-center gap-4">
          <div className="bg-purple-100 p-3 rounded-lg"><ClipboardList className="h-6 w-6 text-purple-600" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Active Care Plans</p>
            <p className="text-2xl font-bold text-gray-900">{stats.carePlans}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm flex items-center gap-4">
          <div className="bg-yellow-100 p-3 rounded-lg"><ClipboardCheck className="h-6 w-6 text-yellow-600" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Pending Approvals</p>
            <p className="text-2xl font-bold text-gray-900">{stats.pendingApprovals}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm flex items-center gap-4">
          <div className="bg-green-100 p-3 rounded-lg"><ShieldAlert className="h-6 w-6 text-green-600" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Recent Audit Logs</p>
            <p className="text-2xl font-bold text-gray-900">{stats.recentAudits}</p>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <button className="bg-blue-50 text-blue-700 px-4 py-2 rounded-lg font-medium hover:bg-blue-100 transition">Schedule Appointment</button>
          <button className="bg-purple-50 text-purple-700 px-4 py-2 rounded-lg font-medium hover:bg-purple-100 transition">Create Care Plan</button>
          <button className="bg-green-50 text-green-700 px-4 py-2 rounded-lg font-medium hover:bg-green-100 transition">Add Medication</button>
        </div>
      </div>
    </div>
  );
}
