from flask import Flask, request, jsonify
import numpy as np
import random
import json
import os


app = Flask(__name__)

GRID_SIZE = 100
POWER = 2


def idw_interpolation(sensor_data):
    """
    sensor_data = list of dicts:
    [
        {"x": float, "y": float, "aqi": float},
        ...
    ]
    """

    grid = np.zeros((GRID_SIZE, GRID_SIZE))

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):

            # Normalize grid coordinates (0 → 1)
            x = i / (GRID_SIZE - 1)
            y = j / (GRID_SIZE - 1)

            numerator = 0
            denominator = 0
            exact_match = False

            for sensor in sensor_data:
                sx = sensor["x"]
                sy = sensor["y"]
                aqi = sensor["aqi"]

                dx = x - sx
                dy = y - sy
                distance = np.sqrt(dx * dx + dy * dy)

                #If grid point exactly equals sensor location
                if distance == 0:
                    grid[i][j] = aqi
                    exact_match = True
                    break

                weight = 1 / (distance ** POWER)

                numerator += weight * aqi
                denominator += weight

            if not exact_match:
                grid[i][j] = numerator / denominator

    return grid


@app.route('/generate_aqi', methods=['POST'])
def generate_aqi():

    data = request.get_json()

    sensor_data = data.get("sensors")

    if not sensor_data or len(sensor_data) < 1:
        return jsonify({"error": "Provide at least one sensor"}), 400

    grid = idw_interpolation(sensor_data)

    response = {
        "grid_size": GRID_SIZE,
        "aqi_matrix": grid.tolist(),
        "min": float(np.min(grid)),
        "max": float(np.max(grid))
    }

    return jsonify(response)


@app.route('/generate_population', methods=['GET'])
def generate_population():

    files = [
        "population_data/population_matrix_1.json",
        "population_data/population_matrix_2.json",
        "population_data/population_matrix_3.json"
    ]

    selected_file = random.choice(files)

    try:
        with open(selected_file, "r") as f:
            data = json.load(f)

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate_priority', methods=['POST'])
def generate_priority():

    data = request.get_json()

    # Expecting:
    # {
    #   "aqi_matrix": [[...100x100...]],
    #   "population_matrix": [[...100x100...]],
    # }

    aqi_matrix = np.array(data.get("aqi_matrix"))
    population_matrix = np.array(data.get("population_matrix"))

    w_aqi = 0.6
    w_population = 0.4

    # Validate shape
    if aqi_matrix.shape != population_matrix.shape:
        return jsonify({"error": "Matrix sizes must match"}), 400

    # Normalize AQI
    aqi_min, aqi_max = aqi_matrix.min(), aqi_matrix.max()
    aqi_norm = (aqi_matrix - aqi_min) / (aqi_max - aqi_min + 1e-9)

    # Normalize Population
    pop_min, pop_max = population_matrix.min(), population_matrix.max()
    pop_norm = (population_matrix - pop_min) / (pop_max - pop_min + 1e-9)

    # Weighted Sum Model
    priority_matrix = (w_aqi * aqi_norm) + (w_population * pop_norm)

    # Flatten and sort
    priority_list = []

    rows, cols = priority_matrix.shape

    for i in range(rows):
        for j in range(cols):
            priority_list.append({
                "x": i,
                "y": j,
                "priority_score": float(priority_matrix[i][j])
            })

    # Sort descending
    priority_list.sort(key=lambda x: x["priority_score"], reverse=True)

    return jsonify({
        "top_5": priority_list[:5],
    })



if __name__ == '__main__':
    app.run(debug=True)