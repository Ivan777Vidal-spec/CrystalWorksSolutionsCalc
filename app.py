from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crystal Works Solutions Estimator</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background: #f4f7f8;
      color: #222;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    .card {
      background: white;
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 18px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    h1, h2, h3 {
      margin-top: 0;
    }
    label {
      display: block;
      margin-top: 12px;
      font-weight: bold;
    }
    input[type="number"], select {
      width: 100%;
      padding: 10px;
      margin-top: 6px;
      border: 1px solid #ccc;
      border-radius: 10px;
      box-sizing: border-box;
      font-size: 16px;
    }
    .checkbox-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 12px;
      padding: 8px 0;
    }
    .checkbox-row input {
      transform: scale(1.2);
    }
    button {
      width: 100%;
      background: #1f7a8c;
      color: white;
      border: none;
      padding: 14px;
      border-radius: 10px;
      font-size: 17px;
      font-weight: bold;
      cursor: pointer;
      margin-top: 18px;
    }
    button:hover {
      background: #175d6a;
    }
    .results p {
      margin: 8px 0;
      font-size: 17px;
    }
    .price {
      font-weight: bold;
      font-size: 18px;
    }
    .section-note {
      font-size: 14px;
      color: #555;
      margin-top: 8px;
    }
    .small {
      font-size: 14px;
      color: #666;
    }
    hr {
      border: none;
      border-top: 1px solid #e5e5e5;
      margin: 16px 0;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>Crystal Works Solutions</h1>
      <p>Residential Cleaning Estimator</p>
    </div>

    <form method="POST">
      <div class="card">
        <h2>Home Details</h2>

        <label>Bedrooms</label>
        <input type="number" name="bedrooms" min="0" step="1" value="{{ form.bedrooms }}">

        <label>Bathrooms</label>
        <input type="number" name="bathrooms" min="0" step="0.5" value="{{ form.bathrooms }}">

        <label>Kitchen(s)</label>
        <input type="number" name="kitchen" min="0" step="1" value="{{ form.kitchen }}">

        <label>Living Room(s)</label>
        <input type="number" name="living" min="0" step="1" value="{{ form.living }}">

        <label>Dining Room(s)</label>
        <input type="number" name="dining" min="0" step="1" value="{{ form.dining }}">

        <label>Hallway(s)</label>
        <input type="number" name="hallway" min="0" step="1" value="{{ form.hallway }}">

        <label>Home Square Footage</label>
        <input type="number" name="sqft" min="0" step="1" value="{{ form.sqft }}">

        <p class="section-note">
          Minimum service price: $150
        </p>
      </div>

      <div class="card">
        <h2>Add-Ons</h2>

        <div class="checkbox-row">
          <input type="checkbox" name="oven" id="oven" {% if form.oven %}checked{% endif %}>
          <label for="oven" style="margin:0;">Inside Oven Cleaning (+$25)</label>
        </div>

        <div class="checkbox-row">
          <input type="checkbox" name="fridge" id="fridge" {% if form.fridge %}checked{% endif %}>
          <label for="fridge" style="margin:0;">Inside Refrigerator Cleaning (+$20)</label>
        </div>

        <div class="checkbox-row">
          <input type="checkbox" name="trash_bin" id="trash_bin" {% if form.trash_bin %}checked{% endif %}>
          <label for="trash_bin" style="margin:0;">Trash Bin Cleaning (+$17 with service)</label>
        </div>

        <label>Number of Windows (+$5 each)</label>
        <input type="number" name="windows" min="0" step="1" value="{{ form.windows }}">

        <label>Carpet Cleaning Sq Ft (+$0.35/sq ft)</label>
        <input type="number" name="carpet_sqft" min="0" step="1" value="{{ form.carpet_sqft }}">

        <label>Pressure Washing Sq Ft (+$0.37/sq ft)</label>
        <input type="number" name="pressure_sqft" min="0" step="1" value="{{ form.pressure_sqft }}">
      </div>

      <div class="card">
        <button type="submit">Calculate Estimate</button>
      </div>
    </form>

    {% if results %}
    <div class="card results">
      <h2>Estimate Results</h2>

      <p><strong>Base Formula Price:</strong> ${{ results.base_formula_price }}</p>
      <p><strong>Square Footage Adjustment:</strong> {{ results.sqft_adjustment }}</p>
      <p><strong>Adjusted Base Price:</strong> ${{ results.adjusted_base_price }}</p>
      <p><strong>Add-On Total:</strong> ${{ results.addons_total }}</p>

      <hr>

      <h3>One-Time Service Prices</h3>
      <p class="price">Basic Cleaning: ${{ results.basic_total }}</p>
      <p class="price">First-Time Cleaning: ${{ results.first_time_total }}</p>
      <p class="price">Deep Cleaning: ${{ results.deep_total }}</p>

      <hr>

      <h3>Recurring Maintenance Prices</h3>
      <p class="price">Weekly (-20%): ${{ results.weekly_total }}</p>
      <p class="price">Biweekly (-15%): ${{ results.biweekly_total }}</p>
      <p class="price">Monthly (-10%): ${{ results.monthly_total }}</p>

      <p class="small">
        Recurring pricing starts after the initial first-time cleaning.
      </p>
    </div>
    {% endif %}
  </div>
</body>
</html>
"""

def to_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def money(value):
    return f"{value:,.2f}"

@app.route("/", methods=["GET", "POST"])
def home():
    form = {
        "bedrooms": 3,
        "bathrooms": 2,
        "kitchen": 1,
        "living": 1,
        "dining": 1,
        "hallway": 1,
        "sqft": 1400,
        "oven": False,
        "fridge": False,
        "trash_bin": False,
        "windows": 0,
        "carpet_sqft": 0,
        "pressure_sqft": 0
    }

    results = None

    if request.method == "POST":
        form["bedrooms"] = to_float(request.form.get("bedrooms"), 0)
        form["bathrooms"] = to_float(request.form.get("bathrooms"), 0)
        form["kitchen"] = to_float(request.form.get("kitchen"), 0)
        form["living"] = to_float(request.form.get("living"), 0)
        form["dining"] = to_float(request.form.get("dining"), 0)
        form["hallway"] = to_float(request.form.get("hallway"), 0)
        form["sqft"] = to_float(request.form.get("sqft"), 0)

        form["oven"] = request.form.get("oven") == "on"
        form["fridge"] = request.form.get("fridge") == "on"
        form["trash_bin"] = request.form.get("trash_bin") == "on"

        form["windows"] = to_float(request.form.get("windows"), 0)
        form["carpet_sqft"] = to_float(request.form.get("carpet_sqft"), 0)
        form["pressure_sqft"] = to_float(request.form.get("pressure_sqft"), 0)

        # Base residential formula
        base_formula_price = (
            (form["bedrooms"] * 0.75) +
            (form["bathrooms"] * 1.0) +
            (form["kitchen"] * 1.0) +
            (form["living"] * 0.5) +
            (form["dining"] * 0.5) +
            (form["hallway"] * 0.25)
        ) * 70

        # Minimum service price
        adjusted_base_price = max(base_formula_price, 150)

        # Square footage adjustment
        sqft_adjustment_text = "No adjustment"
        if form["sqft"] > 5000:
            adjusted_base_price *= 1.30
            sqft_adjustment_text = "+30% (over 5000 sq ft)"
        elif form["sqft"] > 4000:
            adjusted_base_price *= 1.20
            sqft_adjustment_text = "+20% (over 4000 sq ft)"
        elif form["sqft"] > 3000:
            adjusted_base_price *= 1.15
            sqft_adjustment_text = "+15% (over 3000 sq ft)"
        elif form["sqft"] > 2000:
            adjusted_base_price *= 1.10
            sqft_adjustment_text = "+10% (over 2000 sq ft)"

        # Add-ons
        addons_total = 0

        if form["oven"]:
            addons_total += 25

        if form["fridge"]:
            addons_total += 20

        if form["trash_bin"]:
            addons_total += 17

        addons_total += form["windows"] * 5
        addons_total += form["carpet_sqft"] * 0.35
        addons_total += form["pressure_sqft"] * 0.37

        # Main service prices
        basic_price = adjusted_base_price
        first_time_price = adjusted_base_price * 1.18
        deep_price = adjusted_base_price * 1.30

        # Recurring pricing based on basic maintenance price
        weekly_price = adjusted_base_price * 0.80
        biweekly_price = adjusted_base_price * 0.85
        monthly_price = adjusted_base_price * 0.90

        # Totals with add-ons
        basic_total = basic_price + addons_total
        first_time_total = first_time_price + addons_total
        deep_total = deep_price + addons_total
        weekly_total = weekly_price + addons_total
        biweekly_total = biweekly_price + addons_total
        monthly_total = monthly_price + addons_total

        results = {
            "base_formula_price": money(base_formula_price),
            "sqft_adjustment": sqft_adjustment_text,
            "adjusted_base_price": money(adjusted_base_price),
            "addons_total": money(addons_total),
            "basic_total": money(basic_total),
            "first_time_total": money(first_time_total),
            "deep_total": money(deep_total),
            "weekly_total": money(weekly_total),
            "biweekly_total": money(biweekly_total),
            "monthly_total": money(monthly_total),
        }

    return render_template_string(HTML, form=form, results=results)

if __name__ == "__main__":
    app.run(debug=True)
