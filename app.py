from flask import Flask, render_template, request

app = Flask(__name__)

# ----------------------------
# PRICING SETTINGS
# ----------------------------

# Residential
RESIDENTIAL_RATE_PER_HOUR = 70
MINIMUM_SERVICE_PRICE = 150

# Recurring discounts
RECURRING_DISCOUNTS = {
    "one_time": 0.00,
    "weekly": 0.20,
    "biweekly": 0.15,
    "monthly": 0.10,
}

# Realtor rush fees
RUSH_FEES = {
    "none": 0.00,
    "next_day": 0.15,
    "same_day": 0.25,
}


# ----------------------------
# HELPER FUNCTIONS
# ----------------------------

def get_sqft_adjustment(square_feet: int) -> float:
    """Residential sqft increase."""
    if square_feet > 5000:
        return 0.30
    elif square_feet > 4000:
        return 0.20
    elif square_feet > 3000:
        return 0.15
    elif square_feet > 2000:
        return 0.10
    return 0.00


def estimate_cleaning_hours(square_feet: int) -> float:
    """
    Simple residential/realtor base time estimate.
    Adjust this anytime if you want tighter pricing.
    """
    if square_feet <= 1000:
        return 2.0
    elif square_feet <= 1500:
        return 2.5
    elif square_feet <= 2000:
        return 3.0
    elif square_feet <= 2500:
        return 3.5
    elif square_feet <= 3000:
        return 4.0
    elif square_feet <= 4000:
        return 5.0
    elif square_feet <= 5000:
        return 6.0
    return 7.5


def safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ----------------------------
# ROUTE
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    residential_result = None
    realtor_result = None
    exterior_result = None
    active_tab = "residential"

    if request.method == "POST":
        form_type = request.form.get("form_type", "residential")
        active_tab = form_type

        # ----------------------------
        # RESIDENTIAL ESTIMATOR
        # ----------------------------
        if form_type == "residential":
            square_feet = safe_int(request.form.get("square_feet"))
            cleaning_type = request.form.get("cleaning_type", "basic")
            frequency = request.form.get("frequency", "one_time")

            oven = "oven" in request.form
            fridge = "fridge" in request.form
            windows = "windows" in request.form
            carpet = "carpet" in request.form
            pressure = "pressure" in request.form
            bins = "bins" in request.form

            base_hours = estimate_cleaning_hours(square_feet)
            base_price = base_hours * RESIDENTIAL_RATE_PER_HOUR

            sqft_adjustment = get_sqft_adjustment(square_feet)
            price_after_sqft = base_price * (1 + sqft_adjustment)

            service_multiplier = 1.00
            if cleaning_type == "first_time":
                service_multiplier = 1.18
            elif cleaning_type == "deep":
                service_multiplier = 1.30

            subtotal = price_after_sqft * service_multiplier

            add_ons_total = 0.0
            add_on_details = []

            if oven:
                add_ons_total += 25
                add_on_details.append(("Oven Cleaning", 25))
            if fridge:
                add_ons_total += 25
                add_on_details.append(("Fridge Cleaning", 25))
            if windows:
                add_ons_total += 40
                add_on_details.append(("Interior Windows", 40))
            if carpet:
                carpet_sqft = square_feet
                carpet_price = carpet_sqft * 0.35
                add_ons_total += carpet_price
                add_on_details.append(("Carpet Cleaning", carpet_price))
            if pressure:
                pressure_sqft = square_feet
                pressure_price = pressure_sqft * 0.37
                add_ons_total += pressure_price
                add_on_details.append(("Pressure Washing", pressure_price))
            if bins:
                bin_price = 17 if (oven or fridge or windows or carpet or pressure or subtotal > 0) else 20
                add_ons_total += bin_price
                add_on_details.append(("Trash Bin Cleaning", bin_price))

            subtotal_with_addons = subtotal + add_ons_total

            discount_rate = RECURRING_DISCOUNTS.get(frequency, 0.00)
            total = subtotal_with_addons * (1 - discount_rate)

            if total < MINIMUM_SERVICE_PRICE:
                total = MINIMUM_SERVICE_PRICE

            residential_result = {
                "square_feet": square_feet,
                "cleaning_type": cleaning_type,
                "frequency": frequency,
                "base_hours": round(base_hours, 2),
                "base_price": round(base_price, 2),
                "sqft_adjustment_pct": int(sqft_adjustment * 100),
                "service_multiplier": service_multiplier,
                "discount_pct": int(discount_rate * 100),
                "add_on_details": add_on_details,
                "total": round(total, 2),
            }

        # ----------------------------
        # REALTOR ESTIMATOR
        # ----------------------------
        elif form_type == "realtor":
            square_feet = safe_int(request.form.get("realtor_square_feet"))
            service_type = request.form.get("service_type", "listing_prep")
            rush_type = request.form.get("rush_type", "none")

            base_hours = estimate_cleaning_hours(square_feet)
            base_price = base_hours * RESIDENTIAL_RATE_PER_HOUR

            sqft_adjustment = get_sqft_adjustment(square_feet)
            price_after_sqft = base_price * (1 + sqft_adjustment)

            service_multiplier = 1.00
            if service_type == "vacant_move_out":
                service_multiplier = 1.15
            elif service_type == "post_renovation":
                service_multiplier = 1.30
            elif service_type == "open_house_touchup":
                service_multiplier = 1.00

            subtotal = price_after_sqft * service_multiplier

            rush_fee_rate = RUSH_FEES.get(rush_type, 0.00)
            total = subtotal * (1 + rush_fee_rate)

            if service_type == "open_house_touchup" and total < 150:
                total = 150

            if total < MINIMUM_SERVICE_PRICE and service_type != "open_house_touchup":
                total = MINIMUM_SERVICE_PRICE

            realtor_result = {
                "square_feet": square_feet,
                "service_type": service_type,
                "rush_type": rush_type,
                "base_hours": round(base_hours, 2),
                "base_price": round(base_price, 2),
                "sqft_adjustment_pct": int(sqft_adjustment * 100),
                "service_multiplier": service_multiplier,
                "rush_pct": int(rush_fee_rate * 100),
                "total": round(total, 2),
            }

        # ----------------------------
        # EXTERIOR ESTIMATOR
        # ----------------------------
        elif form_type == "exterior":
            pressure_sqft = safe_float(request.form.get("pressure_sqft"))
            carpet_sqft = safe_float(request.form.get("carpet_sqft"))
            trash_bins = safe_int(request.form.get("trash_bins"), 0)
            bins_with_service = request.form.get("bins_with_service") == "yes"

            pressure_total = pressure_sqft * 0.37
            carpet_total = carpet_sqft * 0.35

            if trash_bins > 0:
                per_bin_price = 17 if bins_with_service else 20
                bins_total = trash_bins * per_bin_price
            else:
                bins_total = 0

            total = pressure_total + carpet_total + bins_total

            exterior_result = {
                "pressure_sqft": pressure_sqft,
                "carpet_sqft": carpet_sqft,
                "trash_bins": trash_bins,
                "bins_with_service": bins_with_service,
                "pressure_total": round(pressure_total, 2),
                "carpet_total": round(carpet_total, 2),
                "bins_total": round(bins_total, 2),
                "total": round(total, 2),
            }

    return render_template(
        "index.html",
        residential_result=residential_result,
        realtor_result=realtor_result,
        exterior_result=exterior_result,
        active_tab=active_tab,
    )


if __name__ == "__main__":
    app.run(debug=True)
