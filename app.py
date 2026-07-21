from flask import Flask, render_template


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """Render the commercial estimator shell without pricing logic."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
