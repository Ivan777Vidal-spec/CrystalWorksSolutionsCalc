from flask import Flask, render_template


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """Choose between the commercial and property-turnover estimators."""
    return render_template("home.html")


@app.route("/commercial", methods=["GET"])
def commercial():
    """Render the commercial estimator with a persistent way back to the estimator menu."""
    return render_template("commercial_wrapper.html")


@app.route("/commercial-estimator", methods=["GET"])
def commercial_estimator():
    """Render the existing commercial estimator itself."""
    return render_template("index.html")


@app.route("/turnovers", methods=["GET"])
def turnovers():
    """Render the vacant property and multi-unit turnover estimator."""
    return render_template("turnovers.html")


if __name__ == "__main__":
    app.run(debug=True)
