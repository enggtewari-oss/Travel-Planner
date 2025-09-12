from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import httpx
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class TripSearchRequest(BaseModel):
    destination: str
    checkin_date: str
    checkout_date: str
    guests: int = 2
    budget_range: str = "mid"  # low, mid, high

class Hotel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: str
    price_per_night: float
    rating: float
    amenities: List[str]
    image_url: str
    availability: bool = True

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    forecast_days: List[dict]

class TripRecommendation(BaseModel):
    destination: str
    best_hotels: List[Hotel]
    weather_info: WeatherInfo
    ai_suggestions: str
    estimated_total_cost: float

# Mock hotel data with realistic prices and details
MOCK_HOTELS = {
    "paris": [
        Hotel(name="Hotel des Grands Boulevards", location="Central Paris", price_per_night=280, rating=4.5, 
              amenities=["WiFi", "Restaurant", "Bar", "24h Reception"], 
              image_url="https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400"),
        Hotel(name="Le Meurice", location="Tuileries", price_per_night=850, rating=4.9, 
              amenities=["Spa", "Michelin Restaurant", "Concierge", "Fitness Center"], 
              image_url="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400"),
        Hotel(name="Hotel Malte Opera", location="Opera District", price_per_night=195, rating=4.2, 
              amenities=["WiFi", "Business Center", "Pet Friendly"], 
              image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"),
    ],
    "tokyo": [
        Hotel(name="Aman Tokyo", location="Otemachi", price_per_night=1200, rating=4.8, 
              amenities=["Spa", "Pool", "Traditional Tea Service", "City Views"], 
              image_url="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400"),
        Hotel(name="Shibuya Excel Hotel Tokyu", location="Shibuya", price_per_night=320, rating=4.3, 
              amenities=["WiFi", "Restaurant", "Shopping Mall Access"], 
              image_url="https://images.unsplash.com/photo-1549294413-26f195200c16?w=400"),
        Hotel(name="Hotel Gracery Shinjuku", location="Shinjuku", price_per_night=180, rating=4.1, 
              amenities=["Godzilla Views", "WiFi", "Restaurant"], 
              image_url="https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400"),
    ],
    "new york": [
        Hotel(name="The Plaza", location="Fifth Avenue", price_per_night=750, rating=4.7, 
              amenities=["Spa", "Shopping", "Fine Dining", "Central Park Views"], 
              image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"),
        Hotel(name="Pod Hotels Times Square", location="Times Square", price_per_night=220, rating=4.2, 
              amenities=["Modern Pods", "Rooftop Bar", "Fitness Center"], 
              image_url="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400"),
        Hotel(name="1 Hotels Brooklyn Bridge", location="Brooklyn", price_per_night=385, rating=4.6, 
              amenities=["Eco-Friendly", "Bridge Views", "Farm-to-Table Restaurant"], 
              image_url="https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400"),
    ]
}

async def get_weather_data(location: str) -> WeatherInfo:
    """Get mock weather data for demo purposes"""
    # Mock weather data for popular destinations
    weather_data = {
        "paris": {
            "temp": 18, "condition": "Clear", "humidity": 65, "wind": 12,
            "forecast": [
                {"date": "2024-12-13", "temp": 18, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-14", "temp": 16, "condition": "Clouds", "description": "few clouds"},
                {"date": "2024-12-15", "temp": 14, "condition": "Rain", "description": "light rain"},
                {"date": "2024-12-16", "temp": 12, "condition": "Clouds", "description": "overcast clouds"},
                {"date": "2024-12-17", "temp": 15, "condition": "Clear", "description": "clear sky"},
            ]
        },
        "tokyo": {
            "temp": 8, "condition": "Clear", "humidity": 45, "wind": 8,
            "forecast": [
                {"date": "2024-12-13", "temp": 8, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-14", "temp": 10, "condition": "Clouds", "description": "few clouds"},
                {"date": "2024-12-15", "temp": 12, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-16", "temp": 9, "condition": "Clouds", "description": "scattered clouds"},
                {"date": "2024-12-17", "temp": 11, "condition": "Clear", "description": "clear sky"},
            ]
        },
        "new york": {
            "temp": 5, "condition": "Snow", "humidity": 78, "wind": 15,
            "forecast": [
                {"date": "2024-12-13", "temp": 5, "condition": "Snow", "description": "light snow"},
                {"date": "2024-12-14", "temp": 3, "condition": "Clouds", "description": "overcast clouds"},
                {"date": "2024-12-15", "temp": 7, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-16", "temp": 4, "condition": "Clouds", "description": "broken clouds"},
                {"date": "2024-12-17", "temp": 6, "condition": "Clear", "description": "clear sky"},
            ]
        },
        "london": {
            "temp": 12, "condition": "Rain", "humidity": 85, "wind": 18,
            "forecast": [
                {"date": "2024-12-13", "temp": 12, "condition": "Rain", "description": "light rain"},
                {"date": "2024-12-14", "temp": 11, "condition": "Clouds", "description": "overcast clouds"},
                {"date": "2024-12-15", "temp": 13, "condition": "Rain", "description": "moderate rain"},
                {"date": "2024-12-16", "temp": 10, "condition": "Clouds", "description": "broken clouds"},
                {"date": "2024-12-17", "temp": 14, "condition": "Clouds", "description": "few clouds"},
            ]
        },
        "barcelona": {
            "temp": 22, "condition": "Clear", "humidity": 58, "wind": 10,
            "forecast": [
                {"date": "2024-12-13", "temp": 22, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-14", "temp": 24, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-15", "temp": 21, "condition": "Clouds", "description": "few clouds"},
                {"date": "2024-12-16", "temp": 20, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-17", "temp": 23, "condition": "Clear", "description": "clear sky"},
            ]
        },
        "rome": {
            "temp": 19, "condition": "Clouds", "humidity": 72, "wind": 14,
            "forecast": [
                {"date": "2024-12-13", "temp": 19, "condition": "Clouds", "description": "scattered clouds"},
                {"date": "2024-12-14", "temp": 17, "condition": "Rain", "description": "light rain"},
                {"date": "2024-12-15", "temp": 20, "condition": "Clear", "description": "clear sky"},
                {"date": "2024-12-16", "temp": 18, "condition": "Clouds", "description": "broken clouds"},
                {"date": "2024-12-17", "temp": 21, "condition": "Clear", "description": "clear sky"},
            ]
        }
    }
    
    # Default weather for unknown locations
    default_weather = {
        "temp": 20, "condition": "Clear", "humidity": 60, "wind": 10,
        "forecast": [
            {"date": "2024-12-13", "temp": 20, "condition": "Clear", "description": "clear sky"},
            {"date": "2024-12-14", "temp": 22, "condition": "Clouds", "description": "few clouds"},
            {"date": "2024-12-15", "temp": 18, "condition": "Rain", "description": "light rain"},
            {"date": "2024-12-16", "temp": 19, "condition": "Clouds", "description": "scattered clouds"},
            {"date": "2024-12-17", "temp": 21, "condition": "Clear", "description": "clear sky"},
        ]
    }
    
    # Get weather data for location (case insensitive)
    location_key = location.lower().strip()
    weather = weather_data.get(location_key, default_weather)
    
    # Calculate today's date and adjust forecast dates
    from datetime import datetime, timedelta
    today = datetime.now()
    adjusted_forecast = []
    
    for i, day in enumerate(weather["forecast"]):
        forecast_date = today + timedelta(days=i)
        adjusted_forecast.append({
            "date": forecast_date.strftime("%Y-%m-%d"),
            "temp": day["temp"],
            "condition": day["condition"],
            "description": day["description"]
        })
    
    return WeatherInfo(
        location=location.title(),
        temperature=weather["temp"],
        condition=weather["condition"],
        humidity=weather["humidity"],
        wind_speed=weather["wind"],
        forecast_days=adjusted_forecast
    )

async def get_ai_recommendations(destination: str, hotels: List[Hotel], weather: WeatherInfo, budget: str) -> str:
    """Get AI-powered travel recommendations using OpenAI GPT-5"""
    try:
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"trip-{uuid.uuid4()}",
            system_message="You are a professional travel advisor. Provide personalized, detailed travel recommendations."
        ).with_model("openai", "gpt-5")
        
        hotel_info = "\n".join([f"- {h.name}: ${h.price_per_night}/night, {h.rating}★ ({', '.join(h.amenities[:3])})" for h in hotels[:3]])
        
        user_message = UserMessage(
            text=f"""Create a personalized travel recommendation for {destination}. 
            
Budget: {budget}-range
Weather: {weather.temperature}°C, {weather.condition}
Available Hotels:
{hotel_info}

Provide:
1. Best hotel choice for this budget and weather
2. 3 must-visit attractions
3. Local food recommendations  
4. Weather-appropriate activities
5. Money-saving tips

Keep it concise but helpful (max 300 words)."""
        )
        
        response = await chat.send_message(user_message)
        return response
        
    except Exception as e:
        logging.error(f"AI recommendation error: {str(e)}")
        return f"Welcome to {destination}! Based on the current weather ({weather.temperature}°C, {weather.condition}), it's a great time to explore. Consider the top-rated hotels in your budget range and don't miss the local cuisine!"

@api_router.post("/search-trip", response_model=TripRecommendation)
async def search_trip(request: TripSearchRequest):
    """Search for trip recommendations with hotels, weather, and AI suggestions"""
    destination_key = request.destination.lower().replace(" ", "")
    
    # Get hotels (mock data for now)
    hotels = MOCK_HOTELS.get(destination_key, [
        Hotel(name="Grand Hotel", location="City Center", price_per_night=250, rating=4.3, 
              amenities=["WiFi", "Restaurant", "Pool"], 
              image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"),
        Hotel(name="Budget Inn", location="Downtown", price_per_night=120, rating=3.8, 
              amenities=["WiFi", "Breakfast"], 
              image_url="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400"),
    ])
    
    # Filter hotels by budget
    if request.budget_range == "low":
        filtered_hotels = [h for h in hotels if h.price_per_night < 200]
    elif request.budget_range == "high":
        filtered_hotels = [h for h in hotels if h.price_per_night > 400]
    else:
        filtered_hotels = hotels
    
    # Sort by rating and price
    best_hotels = sorted(filtered_hotels, key=lambda x: (-x.rating, x.price_per_night))[:3]
    
    # Get weather data
    weather_info = await get_weather_data(request.destination)
    
    # Get AI recommendations
    ai_suggestions = await get_ai_recommendations(request.destination, best_hotels, weather_info, request.budget_range)
    
    # Calculate estimated cost
    avg_price = sum(h.price_per_night for h in best_hotels) / len(best_hotels) if best_hotels else 200
    nights = (datetime.fromisoformat(request.checkout_date) - datetime.fromisoformat(request.checkin_date)).days
    estimated_cost = avg_price * nights * request.guests
    
    return TripRecommendation(
        destination=request.destination,
        best_hotels=best_hotels,
        weather_info=weather_info,
        ai_suggestions=ai_suggestions,
        estimated_total_cost=round(estimated_cost, 2)
    )

@api_router.get("/weather/{location}")
async def get_weather(location: str):
    """Get weather information for a location"""
    return await get_weather_data(location)

@api_router.get("/popular-destinations")
async def get_popular_destinations():
    """Get list of popular travel destinations"""
    return {
        "destinations": [
            {"name": "Paris", "country": "France", "image": "https://images.unsplash.com/photo-1502602898536-47ad22581b52?w=400"},
            {"name": "Tokyo", "country": "Japan", "image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400"},
            {"name": "New York", "country": "USA", "image": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=400"},
            {"name": "London", "country": "UK", "image": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400"},
            {"name": "Barcelona", "country": "Spain", "image": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=400"},
            {"name": "Rome", "country": "Italy", "image": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400"},
        ]
    }

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Trip Planner API is running!", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()