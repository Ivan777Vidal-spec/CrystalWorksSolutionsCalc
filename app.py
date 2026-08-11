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
    """Render the turnover estimator and its customer-summary enhancements."""
    html = render_template("turnovers.html")
    scripts = (
        '<script src="/static/turnover-enhancements.js"></script>'
        '<script src="/static/turnover-mobile-fixes.js"></script>'
        '<script src="/static/turnover-crew-work-order.js"></script>'
        '<script src="/static/turnover-pricing-fixes.js"></script>'
    )
    return html.replace("</body>", f"{scripts}</body>")


if __name__ == "__main__":
    app.run(debug=True)
