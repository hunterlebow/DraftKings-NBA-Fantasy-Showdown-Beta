from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
import gurobipy as gb
import pandas as pd
import json
import math
from typing import Dict

app = Flask(__name__)
CORS(app)

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

        # Read the data from the file using pandas
        if extension == 'csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        db, players = optimize(df)

        return jsonify({"db":db, "players":players})        

    else:
        return render_template("index.html")


def optimize(df: pd.DataFrame) -> Dict:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "The file you uploaded can not be converted into a dataframe", 400)

    players = df.index.tolist()

    m = gb.Model()

    m.setParam("PoolSearchMode", 2)
    m.setParam("PoolSolutions", 10)

    # Captain Decision Variable
    captain = m.addVars(players, vtype=gb.GRB.BINARY, name="captain")

    # Utility Decision Variable
    team = m.addVars(players, vtype=gb.GRB.BINARY, name="team")

    # Objective function
    m.setObjective(gb.quicksum((captain[p] * CAPTAIN_BOOST * df.loc[p, "FPPG"]) + (
        team[p] * df.loc[p, "FPPG"]) for p in players), gb.GRB.MAXIMIZE)

    # Constraint on team cost
    m.addConstr(gb.quicksum((captain[p] * df.loc[p, "Salary"] * CAPTAIN_BOOST) + (
        team[p] * df.loc[p, "Salary"]) for p in players) <= BUDGET, "Budget")

    # Constraint on utility candidates
    m.addConstr(gb.quicksum(team[p] for p in players) == UTIL_REQ, "Utility")

    # Constraint on captain candidates
    m.addConstr(gb.quicksum(captain[p]
                for p in players) == CAPTAIN_REQ, "Captain")

    # Constraint on team size
    m.addConstr(team.sum() + captain.sum() == TEAM_REQ, "TeamSize")

    # Constraint on team compisition.  A captain can not also be a utility player in the same lineup, and vice versa.
    m.addConstrs((team[p] + captain[p] <= 1 for p in players), "TeamComp")

    # Optimize the model
    m.optimize()

    db = {}

    for sol in range(m.SolCount):

        m.setParam("SolutionNumber", sol)

        page_data = []

        for p in players:
            if m.getVarByName("captain[{}]".format(p)).Xn > 0.5:
                page_data.append(
                    {
                        "Status": "Captain",
                        "Name": df.loc[p, "Player"],
                        "Projected Points": float(df.loc[p, 'FPPG'])*CAPTAIN_BOOST,
                        "Cost": float(df.loc[p, 'Salary'])*CAPTAIN_BOOST
                    }
                )

            elif m.getVarByName("team[{}]".format(p)).Xn > 0.5:
                page_data.append(
                    {
                        "Status": "Utility",
                        "Name": df.loc[p, "Player"],
                        "Projected Points": float(df.loc[p, "FPPG"]),
                        "Cost": float(df.loc[p, "Salary"])
                    }
                )

            else:
                continue

        db[m.PoolObjVal] = sorted(sorted(
            page_data, key=lambda x: x["Status"]), key=lambda x: x["Projected Points"], reverse=True)

    return db, json.dumps(df["Player"].tolist())

    # create a dropdown menu of every player in the dataset, select multiple
    # selected are removed from optimal solution consideration before optimization


if __name__ == "__main__":
    app.run(debug=True)
