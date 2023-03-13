from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import gurobipy as gb
import pandas as pd
import math

app = Flask(__name__)
CORS(app)


BUDGET = 50000
CAPTAIN_REQ = 1
CAPTAIN_BOOST = 1.5
UTIL_REQ = 5
TEAM_REQ = 6
# Figure this out....
RED_ASTERIK = "*"
RESULTS_PER_PAGE = 1


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return jsonify({"Error": "No File Uploaded"}), 400

        db = optimize(file)

        page = request.args.get("page", default=1, type=int)

        page_start = (page - 1) * RESULTS_PER_PAGE
        page_end = page_start + RESULTS_PER_PAGE

        # page_data = db[page_start:page_end]
        return jsonify(db)

        # work on getting obj val in the front end client side....

    else:
        return render_template("index.html")

    # s = "Projected Score: {}\n\n".format(m.objVal)
    # s += "<img src='/static/crown.png' height='20px' style='vertical-align: middle'>  {} (Captain) :  {} Projected Score\n".format(...)


def optimize(f):
    if not f:
        return "Please select a file"
    df = pd.read_excel(f)

    players = df.index.tolist()

    m = gb.Model()

    m.setParam("PoolSearchMode", 2)
    m.setParam("PoolSolutions", 10)

    captain = m.addVars(players, vtype=gb.GRB.BINARY, name="captain")
    team = m.addVars(players, vtype=gb.GRB.BINARY, name="team")

    # Objective function
    m.setObjective(gb.quicksum((captain[p] * CAPTAIN_BOOST * df.loc[p, "FPPG"]) + (
        team[p] * df.loc[p, "FPPG"]) for p in players), gb.GRB.MAXIMIZE)

    # Constraint on team cost
    m.addConstr(gb.quicksum((captain[p] * df.loc[p, "Salary"] * CAPTAIN_BOOST) + (
        team[p] * df.loc[p, "Salary"]) for p in players) <= BUDGET, "Budget")

    # Constraint on team size
    m.addConstr(gb.quicksum(team[p] for p in players) == UTIL_REQ, "Utility")

    # Constraint on captain selection
    m.addConstr(gb.quicksum(captain[p]
                for p in players) == CAPTAIN_REQ, "Captain")

    m.addConstr(captain.sum() == CAPTAIN_REQ, "CaptainCount")
    m.addConstr(team.sum() == UTIL_REQ, "UtilityCount")
    m.addConstr(gb.quicksum(team[p] + captain[p] for p in players) == TEAM_REQ, "TeamSize")
    m.addConstrs((team[p] + captain[p] <= 1 for p in players), "TeamComp")

    # Optimize the model
    m.optimize()

    # print("\n\nJSON SOLUTION: ", m.getJSONSolution(), "\n\n")

    db = {}

    for sol in range(m.SolCount):

        m.setParam("SolutionNumber", sol)

        page_data = []
        for p in players:
            if m.getVarByName("captain[{}]".format(p)).Xn == 1:
                page_data.append(
                    {
                        "Status": "Captain",
                        "Name": df.loc[p, "Player"],
                        "Projected Points": float(df.loc[p, 'FPPG'])*CAPTAIN_BOOST,
                        "Cost": f"{df.loc[p, 'Salary']*CAPTAIN_BOOST}{RED_ASTERIK}"
                    }
                )

            elif m.getVarByName("team[{}]".format(p)).Xn == 1:
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
        print("\n\nPAGE DATA", page_data, "\n\n")

        db[m.PoolObjVal] = sorted(sorted(
            page_data, key=lambda x: x["Status"]), key=lambda x: x["Projected Points"], reverse=True)
        # m.setParam("PoolGap", 0.001)

    return db

    # To work on, find multiple solutions (PoolSearch Parameter?) and store them...
    # ... in s in a table (or at least on the front end)

    # possibly clickable pages of the best solutions?

    # create a dropdown menu of every player in the dataset, select multiple
    # selected are removed from optimal solution consideration before optimization


if __name__ == "__main__":
    app.run(debug=True)
