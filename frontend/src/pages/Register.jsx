import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '', email: '', password: '', password_confirm: '',
    first_name: '', last_name: '', role: 'STUDENT', department: '',
    phone_number: '', student_id: '', employee_id: '', organization_name: '',
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.password_confirm) {
      toast.error('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await authService.register(formData);
      toast.success('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-2xl w-full">
        <h2 className="text-center text-3xl font-extrabold text-gray-900 mb-8">
          Create your account
        </h2>
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input name="username" placeholder="Username" required className="input-field" value={formData.username} onChange={handleChange} />
            <input name="email" type="email" placeholder="Email" required className="input-field" value={formData.email} onChange={handleChange} />
            <input name="first_name" placeholder="First Name" required className="input-field" value={formData.first_name} onChange={handleChange} />
            <input name="last_name" placeholder="Last Name" required className="input-field" value={formData.last_name} onChange={handleChange} />
            <input name="password" type="password" placeholder="Password" required className="input-field" value={formData.password} onChange={handleChange} />
            <input name="password_confirm" type="password" placeholder="Confirm Password" required className="input-field" value={formData.password_confirm} onChange={handleChange} />
            <select name="role" className="input-field" value={formData.role} onChange={handleChange}>
              <option value="STUDENT">Student</option>
              <option value="CLUB">Club Representative</option>
              <option value="FACULTY">Faculty</option>
              <option value="EXTERNAL">External Organization</option>
            </select>
            <input name="phone_number" type="tel" placeholder="Phone Number" className="input-field" value={formData.phone_number} onChange={handleChange} />
            {formData.role === 'STUDENT' && <input name="student_id" placeholder="Student ID" required className="input-field" value={formData.student_id} onChange={handleChange} />}
            {formData.role === 'FACULTY' && <input name="employee_id" placeholder="Employee ID" required className="input-field" value={formData.employee_id} onChange={handleChange} />}
            {(formData.role === 'STUDENT' || formData.role === 'FACULTY') && <input name="department" placeholder="Department" className="input-field" value={formData.department} onChange={handleChange} />}
            {formData.role === 'EXTERNAL' && <input name="organization_name" placeholder="Organization Name" required className="input-field md:col-span-2" value={formData.organization_name} onChange={handleChange} />}
          </div>
          <button type="submit" disabled={loading} className="w-full btn-primary disabled:opacity-50">
            {loading ? 'Creating account...' : 'Create account'}
          </button>
          <div className="text-center">
            <Link to="/login" className="text-primary-600 hover:text-primary-500">Already have an account? Sign in</Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
