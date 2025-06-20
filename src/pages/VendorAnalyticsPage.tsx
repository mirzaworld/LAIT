import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronLeft, Filter, Search, Loader2 } from 'lucide-react';
import VendorAnalysis from '../components/VendorAnalysis';
import { useVendors } from '../hooks/useApi';

const VendorAnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const { vendors, loading } = useVendors();
  
  const categories = [
    'All Categories',
    'Law Firms',
    'Expert Witnesses',
    'Court Reporters',
    'Document Management',
    'E-Discovery',
    'Legal Research'
  ];
  
  const filteredVendors = vendors?.filter(vendor => {
    const matchesSearch = vendor.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || selectedCategory === 'All Categories' || vendor.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });
  
  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category === 'All Categories' ? undefined : category);
  };
  
  const renderSelectedVendor = () => {
    if (!id) {
      return (
        <div className="bg-white rounded-lg p-8 shadow text-center">
          <h2 className="text-xl font-medium text-gray-900 mb-4">Select a vendor to view detailed analytics</h2>
          <p className="text-gray-600">Choose a vendor from the list to see performance metrics, spending trends, and insights.</p>
        </div>
      );
    }
    
    const selectedVendor = vendors?.find(v => v.id === id);
    
    return <VendorAnalysis vendorId={id} vendorName={selectedVendor?.name} />;
  };
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button 
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 hover:text-gray-900"
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          Back
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Vendor Analytics</h1>
        <div className="w-24"></div> {/* Placeholder for layout balance */}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 border-b">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search vendors..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="p-4 border-b">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900">Categories</h3>
                <Filter className="w-4 h-4 text-gray-500" />
              </div>
              <div className="space-y-2">
                {categories.map((category) => (
                  <label key={category} className="flex items-center">
                    <input
                      type="radio"
                      name="category"
                      checked={selectedCategory === category || (!selectedCategory && category === 'All Categories')}
                      onChange={() => handleCategorySelect(category)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{category}</span>
                  </label>
                ))}
              </div>
            </div>
            
            <div className="p-2">
              <h3 className="font-medium text-gray-900 px-2 py-1">Vendors</h3>
              {loading ? (
                <div className="flex justify-center items-center p-8">
                  <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
                </div>
              ) : filteredVendors?.length ? (
                <ul className="space-y-1">
                  {filteredVendors.map((vendor) => (
                    <li key={vendor.id}>
                      <button
                        onClick={() => navigate(`/vendor-analytics/${vendor.id}`)}
                        className={`w-full text-left px-2 py-2 rounded-md text-sm transition-colors ${
                          id === vendor.id
                            ? 'bg-blue-100 text-blue-900'
                            : 'hover:bg-gray-100 text-gray-800'
                        }`}
                      >
                        <div className="font-medium">{vendor.name}</div>
                        <div className="text-xs text-gray-500 flex items-center justify-between">
                          <span>{vendor.category}</span>
                          <span>${vendor.spend.toLocaleString()}</span>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-4 text-center text-gray-500">
                  No vendors match your search
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Main content */}
        <div className="lg:col-span-3">
          {renderSelectedVendor()}
        </div>
      </div>
    </div>
  );
};

export default VendorAnalyticsPage;
