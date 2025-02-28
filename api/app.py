from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
import pulp as pl
import pandas as pd
import json
from typing import Dict
import os

app = Flask(__name__)
CORS(app)

# Ensure the templates directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)

BUDGET = 50000
CAPTAIN_REQ = 1
CAPTAIN_BOOST = 1.5
UTIL_REQ = 5
TEAM_REQ = 6


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return jsonify({"Error": "No File Uploaded"})

        allowed_extensions = set(['csv', 'xls', 'xlsx'])
        extension = file.filename.split('.')[-1].lower()

        if extension not in allowed_extensions:
            return 'Invalid file extension'

        if extension == 'csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        db, players = optimize(df)

        return_json = jsonify({
            "db": db,
            "players": players,
            "download_template": '<a href="/download_template">Download Template</a>',
            "download_example": '<a href="/download_example">Download Example</a>'
        })

        return return_json

    else:
        return render_template("index.html")


@app.route("/download_template")
def download_template():
    return send_file("../data/template.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/download_example")
def download_example():
    return send_file("../data/example.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def optimize(df: pd.DataFrame) -> Dict:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "The file you uploaded can not be converted into a dataframe", 400)

    players = df.index.tolist()
    
    # Create a list to store multiple solutions
    all_solutions = []
    solution_objectives = []
    
    # We'll create multiple models to find different solutions
    for solution_count in range(10):  # Get up to 10 solutions
        # Create a new model for each solution
        m = pl.LpProblem(f"DraftKings_NBA_Showdown_{solution_count}", pl.LpMaximize)
        
        # Captain Decision Variable
        captain = pl.LpVariable.dicts("captain", players, cat=pl.LpBinary)
        
        # Utility Decision Variable
        team = pl.LpVariable.dicts("team", players, cat=pl.LpBinary)
        
        # Objective function
        m += pl.lpSum((captain[p] * CAPTAIN_BOOST * df.loc[p, "FPPG"]) + 
                      (team[p] * df.loc[p, "FPPG"]) for p in players)
        
        # Constraint on team cost
        m += pl.lpSum((captain[p] * df.loc[p, "Salary"] * CAPTAIN_BOOST) + 
                      (team[p] * df.loc[p, "Salary"]) for p in players) <= BUDGET, "Budget"
        
        # Constraint on utility candidates
        m += pl.lpSum(team[p] for p in players) == UTIL_REQ, "Utility"
        
        # Constraint on captain candidates
        m += pl.lpSum(captain[p] for p in players) == CAPTAIN_REQ, "Captain"
        
        # Constraint on team size
        m += pl.lpSum(team[p] for p in players) + pl.lpSum(captain[p] for p in players) == TEAM_REQ, "TeamSize"
        
        # Constraint on team composition. A captain can not also be a utility player in the same lineup, and vice versa.
        for p in players:
            m += team[p] + captain[p] <= 1, f"TeamComp_{p}"
        
        # Add constraints to exclude previous solutions
        for prev_sol in all_solutions:
            # For each previous solution, add a constraint that forces at least one change
            m += pl.lpSum(captain[p] for p in prev_sol['captain']) + \
                 pl.lpSum(team[p] for p in prev_sol['team']) <= len(prev_sol['captain']) + len(prev_sol['team']) - 1
        
        # Solve the model
        m.solve(pl.PULP_CBC_CMD(msg=False))
        
        # If no solution was found, break the loop
        if pl.LpStatus[m.status] != 'Optimal':
            break
            
        # Store the solution
        current_solution = {'captain': [], 'team': []}
        for p in players:
            if captain[p].value() > 0.5:
                current_solution['captain'].append(p)
            if team[p].value() > 0.5:
                current_solution['team'].append(p)
        
        all_solutions.append(current_solution)
        solution_objectives.append(pl.value(m.objective))
    
    # Create the result dictionary
    db = {}
    
    for sol_idx, solution in enumerate(all_solutions):
        page_data = []
        
        for p in solution['captain']:
            page_data.append(
                {
                    "Status": "Captain",
                    "Name": df.loc[p, "Player"],
                    "Projected Points": float(df.loc[p, 'FPPG'])*CAPTAIN_BOOST,
                    "Cost": float(df.loc[p, 'Salary'])*CAPTAIN_BOOST
                }
            )
            
        for p in solution['team']:
            page_data.append(
                {
                    "Status": "Utility",
                    "Name": df.loc[p, "Player"],
                    "Projected Points": float(df.loc[p, "FPPG"]),
                    "Cost": float(df.loc[p, "Salary"])
                }
            )
            
        db[solution_objectives[sol_idx]] = sorted(sorted(
            page_data, key=lambda x: x["Status"]), key=lambda x: x["Projected Points"], reverse=True)
    
    return db, json.dumps(df["Player"].tolist())


if __name__ == "__main__":
    app.run()
