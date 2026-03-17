import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { venueService } from '../services/venueService';
import toast from 'react-hot-toast';

const VenueSearch = () => {
  const [venues, setVenues] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    search: '',
    min_capacity: '',
    max_capacity: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategories();
    loadVenues();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await venueService.getVenueCategories();
      setCategories(data);
    } catch (error) {
      toast.error('Failed to load categories');
    }
  };

  const loadVenues = async (searchFilters = filters) => {
    setLoading(true);
    try {
      const cleanFilters = Object.fromEntries(
        Object.entries(searchFilters).filter(([_, v]) => v !== '')
      );
      const data = await venueService.getVenues(cleanFilters);
      setVenues(data.results || data);
    } catch (error) {
      toast.error('Failed to load venues');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const newFilters = { ...filters, [e.target.name]: e.target.value };
    setFilters(newFilters);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadVenues(filters);
  };

  const handleReset = () => {
    const resetFilters = { category: '', search: '', min_capacity: '', max_capacity: '' };
    setFilters(resetFilters);
    loadVenues(resetFilters);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Search Venues</h1>

      {/* Filters */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select name="category" className="input-field" value={filters.category} onChange={handleFilterChange}>
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                name="search"
                placeholder="Venue name or location"
                className="input-field"
                value={filters.search}
                onChange={handleFilterChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Capacity</label>
              <input
                type="number"
                name="min_capacity"
                placeholder="Min"
                className="input-field"
                value={filters.min_capacity}
                onChange={handleFilterChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Capacity</label>
              <input
                type="number"
                name="max_capacity"
                placeholder="Max"
                className="input-field"
                value={filters.max_capacity}
                onChange={handleFilterChange}
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button type="submit" className="btn-primary">Search</button>
            <button type="button" onClick={handleReset} className="btn-secondary">Reset</button>
          </div>
        </form>
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : venues.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No venues found. Try adjusting your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {venues.map((venue) => (
            <div key={venue.id} className="card hover:shadow-lg transition-shadow">
              <div className="mb-4">
                <span className="inline-block px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium">
                  {venue.category_display}
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2">{venue.name}</h3>
              <p className="text-gray-600 text-sm mb-4">{venue.location}</p>
              <div className="space-y-2 text-sm text-gray-700 mb-4">
                <p><span className="font-medium">Type:</span> {venue.venue_type_display}</p>
                <p><span className="font-medium">Capacity:</span> {venue.capacity} people</p>
                <p><span className="font-medium">Ownership:</span> {venue.ownership_display}</p>
              </div>
              <Link to={`/venues/${venue.id}`} className="btn-primary w-full text-center block">
                View Details & Book
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VenueSearch;
