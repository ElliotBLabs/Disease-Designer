import os
import json
from datetime import datetime

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, password_strength
import logic

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
con = sqlite3.connect('sim.db', check_same_thread=False)
cur = con.cursor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simulator", methods=["GET", "POST"])
@login_required
def simulator():
    if request.method == "POST":
        #updates params
        logic.SimData.Array_Length = int(request.form["param1"])
        logic.SimData.Population = (logic.SimData.Array_Length ** 2 ) / 4
        logic.SimData.Prob_move = int(request.form["param2"])
        logic.SimData.Prob_init_infected = int(request.form["param3"])
        logic.SimData.Ani_Speed = int(request.form["param4"])
        logic.SimData.Prob_death = int(request.form["param5"])
        logic.SimData.Prob_spread = int(request.form["param6"])
        logic.SimData.Resistance_mod = int(request.form["param7"])
        logic.SimData.Prob_recovery = int(request.form["param8"])
        logic.SimData.Disease_name = request.form["param9"]

        logic.SimData.Gen_Data = {}
        logic.SimData.Generation = 0

        data = logic.main()
        return render_template("simulator.html", data=data, param1=logic.SimData.Array_Length, param2=logic.SimData.Prob_move, param3 = logic.SimData.Prob_init_infected, param4=logic.SimData.Ani_Speed , param5=logic.SimData.Prob_death, param6=logic.SimData.Prob_spread, param7=logic.SimData.Resistance_mod, param8=logic.SimData.Prob_recovery, param9=logic.SimData.Disease_name)
    else:
        print(logic.SimData.Prob_move)
        data = logic.main()
        return render_template("simulator.html", data=data, param1=logic.SimData.Array_Length, param2=logic.SimData.Prob_move, param3 = logic.SimData.Prob_init_infected, param4=logic.SimData.Ani_Speed, param5=logic.SimData.Prob_death, param6=logic.SimData.Prob_spread, param7=logic.SimData.Resistance_mod, param8=logic.SimData.Prob_recovery, param9=logic.SimData.Disease_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        cur.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        rows = cur.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/simulator")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username to register", 400)

        cur.execute("SELECT username FROM users WHERE username=?", request.form.get("username"))
        usernames = cur.fetchall()
        if len(usernames) == 1:
            return apology("That user already exists", 400)


        # Ensure password was submitted
        if not request.form.get("password") or request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide valid passwords that match", 400)

        # Ensures password is of high strength from a helper function
        """
        if password_strength(request.form.get("password")):
            return apology("password not strong", 1)
        """

        # Adds user to the database with a hashed password stored
        cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        return redirect("/login")

    else:
        return render_template("register.html")

#background process happening without any refreshing
@app.route('/background_process_update')
def background_process_test():
    new_image = logic.update_sim()
    return ('{"image" : "%s", "healthy_pop": %i , "recovered_pop": %i , "infected_pop": %i, "dead_pop": %i,"total_pop": %i, "generation": %i, "area": %i}' % (new_image, logic.SimData.Healthy_Population, logic.SimData.Recovered_Population, logic.SimData.Infected_Population, logic.SimData.Dead_Population, logic.SimData.Population, logic.SimData.Generation,logic.SimData.Array_Length ** 2))

@app.route('/report')
def report():
    generation = logic.SimData.Generation
    area = logic.SimData.Array_Length ** 2
    total = logic.SimData.Population

    healthy = logic.SimData.Gen_Data["{}".format(generation)][0]
    dead = logic.SimData.Gen_Data["{}".format(generation)][2]
    recovered = logic.SimData.Gen_Data["{}".format(generation)][3]

    healthy_p = round((healthy / total)*100, 2)
    dead_p = round((dead / total)*100, 2)
    recovered_p = round((recovered / total)*100, 2)

    data1 = logic.show_sim()

    data2 = logic.sim_chart()

    return render_template("report.html", data1=data1, data2=data2, healthy_p=healthy_p, dead_p=dead_p, recovered_p=recovered_p, healthy=healthy, recovered=recovered, dead=dead, generation=generation, area=area, total=total)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run()

con.close()