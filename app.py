import os
import requests
from flask import Flask, request, jsonify

from langchain import PromptTemplate, LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
from flask_cors import CORS
from langchain.memory import ConversationBufferMemory

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Initialize Flask App
app = Flask(__name__)


# Enable CORS for the Flask app

CORS(app) 

# API Keys
os.environ['GOOGLE_API_KEY'] = 'GOOGLE_API_KEY'  #  Gemini API Key
API_KEY = 'GOOGLE_MAPS_API_KEY'  #Google Maps API Key

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/saiva/Downloads/travel-agent-444918-b38b4ac7783d.json"

# API Endpoints
API_BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Helper function: Get coordinates for a given place name
def get_coordinates(place_name):
    params = {"address": place_name, "key": API_KEY}
    response = requests.get(GEOCODE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None

# Helper function: Recommend nearby tourist attractions
def recommend_nearby_places(coords, radius=5000):
    payload = {
        "location": f"{coords[0]},{coords[1]}",
        "radius": radius,
        "type": "tourist_attraction",
        "key": API_KEY
    }
    response = requests.get(API_BASE_URL, params=payload)
    places_data = response.json()

    if places_data.get("status") != "OK":
        return []

    recommendations = [
        {"name": place['name'], "address": place.get('vicinity'), "rating": place.get('rating', 'N/A')}
        for place in places_data['results']
    ]
    return recommendations

# Core function: Create a travel plan
def create_travel_plan(days, source_name, destination_name):
    # Get coordinates for source and destination
    source_coords = get_coordinates(source_name)
    destination_coords = get_coordinates(destination_name)

    if not source_coords or not destination_coords:
        return {"error": "Invalid source or destination name."}

    # Get route details using Directions API
    payload = {
        "origin": f"{source_coords[0]},{source_coords[1]}",
        "destination": f"{destination_coords[0]},{destination_coords[1]}",
        "key": API_KEY
    }
    response = requests.get(DIRECTIONS_API_URL, params=payload)
    directions_data = response.json()

    if directions_data.get("status") != "OK":
        return {"error": "Unable to fetch route details."}

    # Extract route summary and steps
    route_summary = directions_data["routes"][0]["summary"] if directions_data["routes"] else "No route found"
    steps = [step["html_instructions"] for step in directions_data["routes"][0]["legs"][0]["steps"]]

    # Recommend nearby places
    attractions = recommend_nearby_places(destination_coords)

    # Create travel plan details
    travel_plan = {
        "days": days,
        "source": source_name,
        "destination": destination_name,
        "route_summary": route_summary,
        "steps": steps,
        "places_to_visit": attractions
    }
    return travel_plan

# Define LangChain tools
tools = [
    Tool(
        name="Create Travel Plan",
        func=lambda query: create_travel_plan(
            query.get("days"),
            query.get("source_name"),
            query.get("destination_name")
        ),
        description="Generate a travel plan based on days, source, and destination."
    )
]

# Initialize LangChain Agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=False)

# Flask route: Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        print(data)
        
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid data format. Expected JSON."}), 400        
        user_query = data['query']
        days = data['days']
        source_name = data['source_name']
        destination_name = data['destination_name']

        # Call the LangChain tool
        travel_plan = create_travel_plan(days, source_name, destination_name)

        if 'error' in travel_plan:
            return jsonify({"error": travel_plan['error']}), 400
        
        return jsonify({"message": travel_plan})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)


