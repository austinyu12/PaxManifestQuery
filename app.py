from flask import Flask, jsonify, request, render_template
from db import get_connection

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")

@app.get("/passenger")
def search_passenger():
    return render_template("passenger.html")

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404


@app.get("/flights")
def list_flights():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM flights ORDER BY flight_date, flight_no"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.get("/flights/<flight_no>/<flight_date>/<origin>/<destination>/passengers")
def flight_passengers(flight_no, flight_date, origin, destination):
    # flight_date must be YYYY-MM-DD; spaces in flight_no are URL-decoded automatically
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM passengers
               WHERE flight_no = ? AND flight_date = ? AND origin = ? AND destination = ?
               ORDER BY seat""",
            (flight_no, flight_date, origin, destination),
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.get("/passengers/search")
def search_passengers():
    last_name = request.args.get("last_name", "").strip()
    cabin_class = request.args.get("cabin_class", "").strip()
    ssr_code = request.args.get("ssr_code", "").strip()
    seat_num = request.args.get("seat_num", "").strip()
    flight_num = request.args.get("flight_num", "").strip()
    departure_date = request.args.get("departure_date", "").strip()

    conn = get_connection()
    try:
        if last_name:
            # Escape LIKE wildcards in user input so they are treated as literals
            safe = last_name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            rows = conn.execute(
                """SELECT * FROM passengers
                   WHERE last_name LIKE ? ESCAPE '\\'
                   ORDER BY last_name, first_name""",
                (f"%{safe}%",),
            ).fetchall()
        elif cabin_class:
            rows = conn.execute(
                """SELECT * FROM passengers
                   WHERE UPPER(cabin_class) = UPPER(?)
                   ORDER BY seat""",
                (cabin_class,),
            ).fetchall()
        elif ssr_code:
            rows = conn.execute(
                """SELECT * FROM passengers
                   WHERE UPPER(ssr_codes) = UPPER(?)
                   ORDER BY last_name, first_name""",
                (ssr_code,),
            ).fetchall()
        elif seat_num and flight_num and departure_date:
            rows = conn.execute(
                """SELECT * FROM passengers
                   WHERE seat = ? AND flight_no = ? AND flight_date = ?""",
                (seat_num, flight_num, departure_date)
            ).fetchall()
        else:
            return jsonify({"error": "provide one of: last_name, cabin_class, ssr_code, or seat_num+flight_num+departure_date"}), 400

        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.get("/ssr_codes")
def list_ssr_codes():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM ssr_codes ORDER BY code").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
