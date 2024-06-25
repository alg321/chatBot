from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from weather import get_forecast_weather, api_key
from weather import mainFunc



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/alexandergoodwin/PycharmProjects/chatBot/instance/weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create tables
with app.app_context():
    db.create_all()

def update_weather_on_startup():
    print("Updating weather data on app startup...")
    mainFunc()  # Fetch data for all cities on startup

# Register the update function to run when the app starts
with app.app_context():
    update_weather_on_startup()

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route('/chatbot', methods=['POST'])
def chatbot():
    from bot import dynamic_weather_response
    data = request.get_json()
    user_query = data['query']
    response = dynamic_weather_response(user_query)
    return jsonify({'response': response})

@app.route("/weather", methods=["GET", "POST"])
def weather():
    from weather import mainFunc  # Import the main function from weather module
    print("Inside /weather route")
    if request.method == "POST":
        selected_city = request.form.get("city")  # Get the selected city from the form

        # Fetch weather data only for the selected city
        weather_data_list = mainFunc(selected_city)

        # Process weather data
        processed_weather_data_list = []
        for city, country, current_weather, _ in weather_data_list:
            city = city.capitalize() if city else None
            country = country.capitalize() if country else None
            forecast_weather = get_forecast_weather(current_weather.latitude, current_weather.longitude, api_key)
            processed_weather_data_list.append((city, country, current_weather, forecast_weather))

        return render_template("weather.html", weather_data_list=processed_weather_data_list)

    return render_template("weather.html")


if __name__ == '__main__':
    app.run(debug=True)
