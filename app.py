from flask import Flask, request, render_template
import gurobipy as gb
import pandas as pd

app = Flask(__name__)

BUDGET = 50000
CAPTAIN_REQ = 1
CAPTAIN_BOOST = 1.5
UTIL_REQ = 5
TEAM_REQ = 6
    # names = df.Player
    # cost = df.Salary
    # fppg = df["FPPG"]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        result = optimize(file)
        return result
    else:
        return render_template('index.html')


def optimize(f) -> str:
    if not f:
        return "Please select a file"
    df = pd.read_excel(f)

    players = df.index.tolist()

    m = gb.Model()

    captain = m.addVars(players, vtype=gb.GRB.BINARY, name="captain")
    team = m.addVars(players, vtype=gb.GRB.BINARY, name="team")

    # Objective function
    m.setObjective(gb.quicksum((captain[p] * CAPTAIN_BOOST * df.loc[p, 'FPPG']) + (
        team[p] * df.loc[p, 'FPPG']) for p in players), gb.GRB.MAXIMIZE)

    # Constraint on team cost
    m.addConstr(gb.quicksum((captain[p] * df.loc[p, 'Salary'] * CAPTAIN_BOOST) + (
        team[p] * df.loc[p, 'Salary']) for p in players) <= BUDGET, "Budget")

    # Constraint on team size
    m.addConstr(gb.quicksum(team[p] for p in players) == UTIL_REQ, "Utility")

    # Constraint on captain selection
    m.addConstr(gb.quicksum(captain[p]
                for p in players) == CAPTAIN_REQ, "Captain")

    m.addConstr(captain.sum() == CAPTAIN_REQ, "CaptainCount")
    m.addConstr(team.sum() == UTIL_REQ, "UtilityCount")
    m.addConstrs((team[p] + captain[p] <= 1 for p in players), "TeamComp")

    # Optimize the model
    m.optimize()

    
    s = "Projected Score: {}\n\n".format(m.objVal)
    for p in players:
        if captain[p].X == 1:
            s += "<img src='/static/crown.png' height='20px' style='vertical-align: middle'>  {} (Captain) :  {} Projected Score\n".format(df.loc[p, "Player"], df.loc[p, "FPPG"]*CAPTAIN_BOOST) 
        elif team[p].X == 1:
            s += ">>  {} (Utility) : {} Projected Score \n".format(df.loc[p, "Player"], df.loc[p, "FPPG"])
        else:
            continue
        
    #To work on, find multiple solutions (PoolSearch Parameter?) and store them...
    #... in s in a table (or at least on the front end)
    
    #possibly clickable pages of the best solutions?
    
    #create a dropdown menu of every player in the dataset, select multiple
    #selected are removed from optimal solution consideration before optimization
    
    
    return s


if __name__ == "__main__":
    app.run(debug=True)
