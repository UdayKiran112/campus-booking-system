import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Profile</h1>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'profile'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Profile Information
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'stats'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Booking Statistics
          </button>
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input type="text" value={user?.username || ''} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" value={user?.email || ''} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
              <input type="text" value={user?.first_name || ''} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
              <input type="text" value={user?.last_name || ''} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <input type="text" value={user?.role || ''} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <input type="text" value={user?.department || 'N/A'} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
              <input type="text" value={user?.phone_number || 'N/A'} disabled className="input-field bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Verified</label>
              <span className={`inline-block px-3 py-2 rounded-lg ${user?.verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {user?.verified ? 'Verified' : 'Pending Verification'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-6">Booking Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-primary-600">{user?.profile?.total_bookings || 0}</p>
                <p className="text-gray-600 mt-1">Total Bookings</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">{user?.profile?.successful_bookings || 0}</p>
                <p className="text-gray-600 mt-1">Successful</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-red-600">{user?.profile?.no_show_count || 0}</p>
                <p className="text-gray-600 mt-1">No Shows</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Reliability Score</h2>
            <div className="flex items-center gap-4">
              <div className="flex-1 bg-gray-200 rounded-full h-4">
                <div 
                  className="bg-primary-600 h-4 rounded-full" 
                  style={{ width: `${user?.profile?.reliability_score || 100}%` }}
                ></div>
              </div>
              <span className="text-2xl font-bold text-primary-600">{user?.profile?.reliability_score || 100}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
