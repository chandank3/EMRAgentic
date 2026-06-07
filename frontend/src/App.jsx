import React, { useState, useEffect } from 'react';
import { Menu, X, LogOut, Bell, User, Settings, Home, Calendar, FileText, Pill, ClipboardList, Shield, ClipboardCheck } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Appointments from './pages/Appointments';
import CarePlans from './pages/CarePlans';
import Medications from './pages/Medications';
import Documents from './pages/Documents';
import Approvals from './pages/Approvals';
import AuditLog from './pages/AuditLog';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';
const DEMO_PATIENT_ID = '11111111-1111-1111-1111-111111111111';

function App() {
  const [currentUser, setCurrentUser] = useState({
    name: 'Dr. Sarah Johnson',
    role: 'care_coordinator',
    department: 'Cardiology'
  });
  
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notifications, setNotifications] = useState(3);
  const [healthStatus, setHealthStatus] = useState('checking');

  useEffect(() => {
    // Check API health
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(data => setHealthStatus('healthy'))
      .catch(() => setHealthStatus('offline'));
  }, []);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'appointments', label: 'Appointments', icon: Calendar },
    { id: 'care-plans', label: 'Care Plans', icon: ClipboardList },
    { id: 'medications', label: 'Medications', icon: Pill },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'approvals', label: 'Approvals', icon: ClipboardCheck },
    { id: 'audit', label: 'Audit Log', icon: Shield },
  ];

  const roleColors = {
    admin: 'bg-red-100 text-red-800',
    care_coordinator: 'bg-blue-100 text-blue-800',
    physician: 'bg-green-100 text-green-800',
    nurse: 'bg-purple-100 text-purple-800',
    approver: 'bg-yellow-100 text-yellow-800',
    patient: 'bg-gray-100 text-gray-800'
  };

  const renderPage = () => {
    switch(currentPage) {
      case 'dashboard':
        return <Dashboard apiBase={API_BASE} patientId={DEMO_PATIENT_ID} />;
      case 'appointments':
        return <Appointments apiBase={API_BASE} patientId={DEMO_PATIENT_ID} />;
      case 'care-plans':
        return <CarePlans apiBase={API_BASE} patientId={DEMO_PATIENT_ID} />;
      case 'medications':
        return <Medications apiBase={API_BASE} patientId={DEMO_PATIENT_ID} />;
      case 'documents':
        return <Documents apiBase={API_BASE} patientId={DEMO_PATIENT_ID} />;
      case 'approvals':
        return <Approvals apiBase={API_BASE} />;
      case 'audit':
        return <AuditLog apiBase={API_BASE} />;
      default:
        return <Dashboard apiBase={API_BASE} patientId={DEMO_PATIENT_ID} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gradient-to-b from-blue-900 to-blue-800 text-white transition-all duration-300 flex flex-col shadow-xl`}>
        {/* Logo */}
        <div className="p-4 border-b border-blue-700 flex items-center justify-between">
          {sidebarOpen && <h1 className="font-bold text-lg">HC Agent</h1>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-blue-700 rounded-lg transition"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg transition ${
                  currentPage === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-blue-100 hover:bg-blue-700'
                }`}
              >
                <Icon size={20} />
                {sidebarOpen && <span>{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {/* Status Footer */}
        <div className="p-4 border-t border-blue-700 space-y-3">
          <div className="text-sm space-y-1">
            {sidebarOpen && (
              <>
                <p className="font-semibold truncate">{currentUser.name}</p>
                <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${roleColors[currentUser.role]}`}>
                  {currentUser.role.replace('_', ' ')}
                </span>
              </>
            )}
          </div>
          <div className="flex items-center space-x-2 text-xs">
            <div className={`w-2 h-2 rounded-full ${
              healthStatus === 'healthy' ? 'bg-green-400' : healthStatus === 'checking' ? 'bg-yellow-400' : 'bg-red-400'
            }`} />
            {sidebarOpen && <span>{healthStatus}</span>}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900">Healthcare Care Coordinator</h2>
          <div className="flex items-center space-x-6">
            {/* Notifications */}
            <div className="relative">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition relative">
                <Bell size={20} className="text-gray-600" />
                {notifications > 0 && (
                  <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {notifications}
                  </span>
                )}
              </button>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4 pl-6 border-l border-gray-200">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition">
                <Settings size={20} className="text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition">
                <User size={20} className="text-gray-600" />
              </button>
              <button className="p-2 hover:bg-red-100 rounded-lg transition">
                <LogOut size={20} className="text-red-600" />
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-auto">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}

export default App;
