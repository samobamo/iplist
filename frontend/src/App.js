import React, { useState } from "react";
import "./App.css";
import Dashboard from "./components/Dashboard";
import Calendar from "./components/Calendar";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Time Management Hub
          </h1>
          <p className="text-gray-600">Organize your tasks and manage your time efficiently</p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-xl p-1 shadow-lg">
            <div className="flex space-x-1">
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`nav-item ${
                  activeTab === "dashboard" ? "nav-item-active" : "nav-item-inactive"
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H10a2 2 0 01-2-2V5z" />
                </svg>
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab("calendar")}
                className={`nav-item ${
                  activeTab === "calendar" ? "nav-item-active" : "nav-item-inactive"
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2v16a2 2 0 002 2z" />
                </svg>
                Calendar
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto">
          {activeTab === "dashboard" && <Dashboard />}
          {activeTab === "calendar" && <Calendar />}
        </div>
      </div>
    </div>
  );
}

export default App;