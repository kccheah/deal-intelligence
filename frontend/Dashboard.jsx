/**
 * Dashboard Component
 * Main page showing deals and properties feed
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { FiSearch, FiFilter, FiBell, FiTrendingUp } from 'react-icons/fi';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [deals, setDeals] = useState([]);
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all | deals | properties
  const [searchTerm, setSearchTerm] = useState('');
  const [minScore, setMinScore] = useState(0);

  useEffect(() => {
    fetchData();
  }, [filter, minScore]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      if (filter === 'all' || filter === 'deals') {
        const dealsRes = await axios.get(`${API_BASE}/deals?limit=20&skip=0`, { headers });
        setDeals(dealsRes.data);
      }

      if (filter === 'all' || filter === 'properties') {
        const propsRes = await axios.get(`${API_BASE}/properties?limit=20&skip=0`, { headers });
        setProperties(propsRes.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterBySearch = (items) => {
    if (!searchTerm) return items;
    return items.filter(
      (item) =>
        (item.company_name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (item.address?.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  const filterByScore = (items) => {
    const scoreKey = items[0]?.score ? 'score' : 'investment_score';
    return items.filter((item) => (item[scoreKey] || 0) >= minScore);
  };

  const filteredDeals = filterByScore(filterBySearch(deals));
  const filteredProperties = filterByScore(filterBySearch(properties));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Deal Intelligence</h1>
        <p className="text-slate-600">AI-powered cross-border deal sourcing & property analysis</p>
      </div>

      {/* Controls */}
      <div className="max-w-7xl mx-auto mb-8 bg-white rounded-lg shadow-sm p-6">
        {/* Search Bar */}
        <div className="flex gap-4 mb-4">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search deals or properties..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
            <FiBell size={18} />
            Create Alert
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 items-center">
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('deals')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'deals'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              Deals
            </button>
            <button
              onClick={() => setFilter('properties')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === 'properties'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              Properties
            </button>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <FiFilter size={18} className="text-slate-600" />
            <label className="text-slate-700 font-medium">Min Score:</label>
            <input
              type="range"
              min="0"
              max="100"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              className="w-24"
            />
            <span className="text-slate-600 font-bold">{minScore}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-slate-600 mt-4">Loading deals and properties...</p>
          </div>
        ) : (
          <>
            {/* Deals Section */}
            {(filter === 'all' || filter === 'deals') && (
              <div className="mb-12">
                <div className="flex items-center gap-2 mb-6">
                  <FiTrendingUp className="text-blue-600" size={24} />
                  <h2 className="text-2xl font-bold text-slate-900">Recent Deals</h2>
                  <span className="ml-auto text-slate-600 text-sm">{filteredDeals.length} deals</span>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {filteredDeals.length > 0 ? (
                    filteredDeals.map((deal) => (
                      <Link
                        key={deal.id}
                        to={`/deals/${deal.id}`}
                        className="bg-white rounded-lg shadow hover:shadow-md transition p-6 border-l-4 border-blue-600"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-xl font-bold text-slate-900">{deal.company_name}</h3>
                            <p className="text-slate-600 text-sm">{deal.industry}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-3xl font-bold text-blue-600">{deal.score}/100</div>
                            <span className="text-xs text-slate-500">{deal.deal_type?.toUpperCase()}</span>
                          </div>
                        </div>

                        <p className="text-slate-600 text-sm mb-3 line-clamp-2">{deal.deal_description}</p>

                        <div className="flex justify-between items-center">
                          <div className="flex gap-4 text-sm">
                            <span className="text-slate-600">
                              💰 ${(deal.deal_value_usd || 0).toLocaleString()}
                            </span>
                            <span className="text-slate-600">📍 {deal.target_geography}</span>
                            <span className="text-slate-600">📅 {deal.announced_date}</span>
                          </div>
                          <button className="px-3 py-1 bg-blue-100 text-blue-600 rounded hover:bg-blue-200 text-sm font-medium">
                            View Details
                          </button>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <p className="text-center text-slate-500 py-8">No deals matching your criteria</p>
                  )}
                </div>
              </div>
            )}

            {/* Properties Section */}
            {(filter === 'all' || filter === 'properties') && (
              <div>
                <div className="flex items-center gap-2 mb-6">
                  <FiTrendingUp className="text-green-600" size={24} />
                  <h2 className="text-2xl font-bold text-slate-900">Investment Properties</h2>
                  <span className="ml-auto text-slate-600 text-sm">{filteredProperties.length} properties</span>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {filteredProperties.length > 0 ? (
                    filteredProperties.map((prop) => (
                      <Link
                        key={prop.id}
                        to={`/properties/${prop.id}`}
                        className="bg-white rounded-lg shadow hover:shadow-md transition p-6 border-l-4 border-green-600"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-xl font-bold text-slate-900">{prop.address}</h3>
                            <p className="text-slate-600 text-sm">
                              {prop.city}, {prop.country_code}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-3xl font-bold text-green-600">
                              {prop.investment_score}/100
                            </div>
                            <span className={`text-xs px-2 py-1 rounded ${
                              prop.risk_level === 'low'
                                ? 'bg-green-100 text-green-700'
                                : prop.risk_level === 'medium'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-red-100 text-red-700'
                            }`}>
                              {prop.risk_level?.toUpperCase()} RISK
                            </span>
                          </div>
                        </div>

                        <div className="flex justify-between items-center">
                          <div className="flex gap-4 text-sm">
                            <span className="text-slate-600">
                              💰 ${(prop.price_usd || 0).toLocaleString()}
                            </span>
                            <span className="text-slate-600">📐 {prop.size_sqm} sqm</span>
                            <span className="text-slate-600">🏠 {prop.property_type}</span>
                          </div>
                          <button className="px-3 py-1 bg-green-100 text-green-600 rounded hover:bg-green-200 text-sm font-medium">
                            View DD Report
                          </button>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <p className="text-center text-slate-500 py-8">No properties matching your criteria</p>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
