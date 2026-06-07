import React, { useState, useEffect } from 'react';
import { Pill, Clock, Activity, Info } from 'lucide-react';

export default function Medications({ apiBase, patientId }) {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!patientId) return;
    
    setLoading(true);
    fetch(`${apiBase}/api/medications/${patientId}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch medications');
        return res.json();
      })
      .then(data => {
        setMedications(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [apiBase, patientId]);

  if (loading) return <div className="p-8 text-gray-500">Loading medications...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Medications</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          Add Medication
        </button>
      </div>

      {medications.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <Pill className="mx-auto h-12 w-12 text-gray-400 mb-3" />
          <p className="text-gray-500">No active medications.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {medications.map((med) => (
            <div key={med.id} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 hover:shadow-md transition">
              <div className="flex items-start gap-4 mb-4">
                <div className="bg-orange-100 p-3 rounded-lg">
                  <Pill className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{med.name}</h3>
                  <span className="text-sm font-medium text-orange-600 bg-orange-50 px-2 py-1 rounded-md">
                    {med.dosage}
                  </span>
                </div>
              </div>
              
              <div className="space-y-3 mt-4 border-t border-gray-100 pt-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span><span className="font-medium text-gray-700">Frequency:</span> {med.frequency}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Activity className="h-4 w-4 text-gray-400" />
                  <span><span className="font-medium text-gray-700">Route:</span> <span className="capitalize">{med.route}</span></span>
                </div>
                {med.instructions && (
                  <div className="flex items-start gap-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-md mt-2">
                    <Info className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                    <span>{med.instructions}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
