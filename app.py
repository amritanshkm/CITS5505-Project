from flask import Flask, render_template

app = Flask(__name__)

EVENTS = [
    {
        "title": "Tech Networking Night",
        "date": "12 Apr",
        "time": "6:00 PM",
        "location": "Perth CBD",
        "description": "Meet developers, designers, and founders for an evening of networking and startup conversations.",
        "category": "Tech",
        "price_label": "Free",
        "price_type": "free",
        "coords": [-31.9523, 115.8613],
    },
    {
        "title": "Beginner Yoga in the Park",
        "date": "13 Apr",
        "time": "8:00 AM",
        "location": "Kings Park",
        "description": "A relaxed outdoor yoga session for beginners. Bring a mat, water bottle, and a friend.",
        "category": "Wellness",
        "price_label": "$10",
        "price_type": "paid",
        "coords": [-31.9617, 115.8327],
    },
    {
        "title": "Startup Pitch Evening",
        "date": "15 Apr",
        "time": "7:00 PM",
        "location": "Subiaco",
        "description": "Watch early-stage founders pitch ideas, connect with mentors, and explore local startup opportunities.",
        "category": "Business",
        "price_label": "$15",
        "price_type": "paid",
        "coords": [-31.9478, 115.8233],
    },
    {
        "title": "Sunset Beach Meetup",
        "date": "16 Apr",
        "time": "5:30 PM",
        "location": "Cottesloe Beach",
        "description": "Casual beach meetup with games, snacks, and a chance to make new friends while watching the sunset.",
        "category": "Social",
        "price_label": "Free",
        "price_type": "free",
        "coords": [-31.9937, 115.7528],
    },
]

@app.route("/")
def home():
    return render_template("index.html", events=EVENTS)

if __name__ == "__main__":
    app.run(debug=True)