import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { MapPin, Calendar, Users, Thermometer, Cloud, DollarSign, Star, Wifi, Car, Coffee, Utensils } from 'lucide-react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { toast } from 'sonner';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TripPlanner = () => {
  const [searchData, setSearchData] = useState({
    destination: '',
    checkin_date: '',
    checkout_date: '',
    guests: 2,
    budget_range: 'mid'
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [popularDestinations, setPopularDestinations] = useState([]);

  useEffect(() => {
    fetchPopularDestinations();
  }, []);

  const fetchPopularDestinations = async () => {
    try {
      const response = await axios.get(`${API}/popular-destinations`);
      setPopularDestinations(response.data.destinations);
    } catch (error) {
      console.error('Error fetching destinations:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchData.destination || !searchData.checkin_date || !searchData.checkout_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/search-trip`, searchData);
      setResults(response.data);
      toast.success('Trip recommendations found!');
    } catch (error) {
      console.error('Search error:', error);
      toast.error(error.response?.data?.detail || 'Failed to search trips');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setSearchData(prev => ({ ...prev, [field]: value }));
  };

  const getAmenityIcon = (amenity) => {
    const icons = {
      'WiFi': <Wifi className="w-4 h-4" />,
      'Restaurant': <Utensils className="w-4 h-4" />,
      'Bar': <Coffee className="w-4 h-4" />,
      'Parking': <Car className="w-4 h-4" />,
      'Spa': <Star className="w-4 h-4" />,
      'Pool': <Cloud className="w-4 h-4" />,
      'Fitness Center': <Star className="w-4 h-4" />,
      'Business Center': <Wifi className="w-4 h-4" />,
    };
    return icons[amenity] || <Star className="w-4 h-4" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-emerald-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-cyan-600 rounded-lg flex items-center justify-center">
                <MapPin className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-700 to-cyan-700 bg-clip-text text-transparent">
                Trip Planner
              </h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Plan Your Perfect Trip
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get AI-powered recommendations, compare hotel prices, and check weather forecasts all in one place
          </p>
        </div>

        {/* Search Form */}
        <Card className="mb-8 shadow-xl border-0 bg-white/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-emerald-800">Search Your Dream Destination</CardTitle>
            <CardDescription>Find the best hotels and get personalized recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Destination</label>
                <Input
                  placeholder="Where to?"
                  value={searchData.destination}
                  onChange={(e) => handleInputChange('destination', e.target.value)}
                  className="border-emerald-200 focus:border-emerald-500"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Check-in</label>
                <Input
                  type="date"
                  value={searchData.checkin_date}
                  onChange={(e) => handleInputChange('checkin_date', e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="border-emerald-200 focus:border-emerald-500"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Check-out</label>
                <Input
                  type="date"
                  value={searchData.checkout_date}
                  onChange={(e) => handleInputChange('checkout_date', e.target.value)}
                  min={searchData.checkin_date || new Date().toISOString().split('T')[0]}
                  className="border-emerald-200 focus:border-emerald-500"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Guests</label>
                <Select value={searchData.guests.toString()} onValueChange={(value) => handleInputChange('guests', parseInt(value))}>
                  <SelectTrigger className="border-emerald-200 focus:border-emerald-500">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[1,2,3,4,5,6].map(num => (
                      <SelectItem key={num} value={num.toString()}>{num} Guest{num > 1 ? 's' : ''}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Budget</label>
                <Select value={searchData.budget_range} onValueChange={(value) => handleInputChange('budget_range', value)}>
                  <SelectTrigger className="border-emerald-200 focus:border-emerald-500">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Budget ($50-200)</SelectItem>
                    <SelectItem value="mid">Mid-range ($200-400)</SelectItem>
                    <SelectItem value="high">Luxury ($400+)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="lg:col-span-5 pt-4">
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transform transition hover:scale-105"
                >
                  {loading ? 'Searching...' : 'Search Trips'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Popular Destinations */}
        {!results && popularDestinations.length > 0 && (
          <div className="mb-12">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Popular Destinations</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {popularDestinations.map((dest) => (
                <Card 
                  key={dest.name} 
                  className="cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-lg border-0 bg-white/60 backdrop-blur-sm"
                  onClick={() => handleInputChange('destination', dest.name)}
                >
                  <div className="aspect-square relative overflow-hidden rounded-t-lg">
                    <img 
                      src={dest.image} 
                      alt={dest.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <CardContent className="p-3">
                    <h4 className="font-semibold text-gray-800">{dest.name}</h4>
                    <p className="text-sm text-gray-600">{dest.country}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Search Results */}
        {results && (
          <div className="space-y-8">
            {/* Weather & Cost Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="shadow-xl border-0 bg-gradient-to-br from-blue-50 to-cyan-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-blue-800">
                    <Thermometer className="w-5 h-5" />
                    <span>Weather in {results.destination}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-2xl font-bold text-blue-800">{results.weather_info.temperature}°C</p>
                        <p className="text-blue-600">{results.weather_info.condition}</p>
                      </div>
                      <Cloud className="w-12 h-12 text-blue-400" />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Humidity</p>
                        <p className="font-semibold">{results.weather_info.humidity}%</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Wind Speed</p>
                        <p className="font-semibold">{results.weather_info.wind_speed} km/h</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-xl border-0 bg-gradient-to-br from-emerald-50 to-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-emerald-800">
                    <DollarSign className="w-5 h-5" />
                    <span>Trip Cost Estimate</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-3xl font-bold text-emerald-800">${results.estimated_total_cost}</p>
                      <p className="text-emerald-600">Total estimated cost</p>
                    </div>
                    <div className="text-sm space-y-1">
                      <p><span className="font-semibold">Guests:</span> {searchData.guests}</p>
                      <p><span className="font-semibold">Duration:</span> {(new Date(searchData.checkout_date) - new Date(searchData.checkin_date)) / (1000 * 60 * 60 * 24)} nights</p>
                      <p><span className="font-semibold">Budget Range:</span> {searchData.budget_range.charAt(0).toUpperCase() + searchData.budget_range.slice(1)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Hotels */}
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Best Hotels for You</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.best_hotels.map((hotel) => (
                  <Card key={hotel.id} className="shadow-xl border-0 bg-white/70 backdrop-blur-sm hover:scale-105 transition-all duration-300">
                    <div className="aspect-video relative overflow-hidden rounded-t-lg">
                      <img 
                        src={hotel.image_url} 
                        alt={hotel.name}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute top-3 right-3">
                        <Badge className="bg-emerald-600 text-white">
                          {hotel.rating} <Star className="w-3 h-3 ml-1 fill-current" />
                        </Badge>
                      </div>
                    </div>
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-lg font-bold text-gray-800">{hotel.name}</h4>
                          <p className="text-gray-600">{hotel.location}</p>
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="text-2xl font-bold text-emerald-700">${hotel.price_per_night}</p>
                            <p className="text-sm text-gray-600">per night</p>
                          </div>
                          <Badge variant="outline" className="border-emerald-200 text-emerald-700">
                            {hotel.availability ? 'Available' : 'Sold Out'}
                          </Badge>
                        </div>
                        
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-2">Amenities:</p>
                          <div className="flex flex-wrap gap-2">
                            {hotel.amenities.slice(0, 4).map((amenity) => (
                              <div key={amenity} className="flex items-center space-x-1 text-xs bg-gray-100 px-2 py-1 rounded-full">
                                {getAmenityIcon(amenity)}
                                <span>{amenity}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        <Button className="w-full bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-700 hover:to-cyan-700 text-white">
                          Book Now
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* AI Recommendations */}
            <Card className="shadow-xl border-0 bg-gradient-to-br from-purple-50 to-indigo-50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-purple-800">
                  <Star className="w-5 h-5" />
                  <span>AI Travel Recommendations</span>
                </CardTitle>
                <CardDescription>Personalized suggestions powered by AI</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-purple max-w-none">
                  <p className="text-gray-700 whitespace-pre-line leading-relaxed">
                    {results.ai_suggestions}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Weather Forecast */}
            {results.weather_info.forecast_days.length > 0 && (
              <Card className="shadow-xl border-0 bg-gradient-to-br from-sky-50 to-blue-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-sky-800">
                    <Cloud className="w-5 h-5" />
                    <span>5-Day Weather Forecast</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {results.weather_info.forecast_days.map((day, index) => (
                      <div key={index} className="text-center p-4 bg-white/50 rounded-lg">
                        <p className="text-sm font-medium text-gray-600 mb-2">
                          {format(new Date(day.date), 'MMM dd')}
                        </p>
                        <p className="text-xl font-bold text-sky-800">{day.temp}°C</p>
                        <p className="text-sm text-sky-600 capitalize">{day.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default TripPlanner;