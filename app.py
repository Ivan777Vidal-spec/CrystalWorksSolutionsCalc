from flask import Flask, render_template, request

app = Flask(__name__)

# ----------------------------
# PRICING SETTINGS
# ----------------------------

RESIDENTIAL_RATE_PER_HOUR = 70
COMMERCIAL_RATE_PER_HOUR = 63
MINIMUM_SERVICE_PRICE = 150
OPEN_HOUSE_MINIMUM = 150

RECURRING_DISCOUNTS = {
    "one_time": 0.00,
    "weekly": 0.20,
    "biweekly": 0.15,
    "monthly": 0.10,
}

SERVICE_MULTIPLIERS = {
    "basic": 1.00,
    "first_time": 1.18,
    "deep": 1.30,
}

REALTOR_MULTIPLIERS = {
    "listing_prep": 1.00,
    "vacant_move_out": 1.15,
    "post_renovation": 1.30,
    "open_house_touchup": 1.00,
}

RUSH_FEES = {
    "none": 0.00,
    "next_day": 0.15,
    "same_day": 0.25,
}

CONDITION_MULTIPLIERS = {
    "normal": 1.00,
    "dirty": 1.10,
    "very_dirty": 1.20,
}

CONDITION_RANGE = {
    "normal": (0.97, 1.05),
    "dirty": (0.98, 1.08),
    "very_dirty": (1.00, 1.12),
}


# ----------------------------
# HELPERS
# ----------------------------

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


def money(value):
    return round(float(value), 2)


def get_sqft_adjustment(square_feet: int) -> float:
    if square_feet > 5000:
        return 0.30
    elif square_feet > 4000:
        return 0.20
    elif square_feet > 3000:
        return 0.15
    elif square_feet > 2000:
        return 0.10
    return 0.00


def estimate_base_hours(square_feet: int) -> float:
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


def estimate_detail_hours(bedrooms: int, bathrooms: int, half_baths: int, stories: int) -> float:
    extra = 0.0
    extra += bedrooms * 0.20
    extra += bathrooms * 0.30
    extra += half_baths * 0.15
    if stories > 1:
        extra += (stories - 1) * 0.25
    return extra


def build_range(total_price: float, condition_key: str):
    low_mult, high_mult = CONDITION_RANGE.get(condition_key, (0.97, 1.05))
    low = max(MINIMUM_SERVICE_PRICE, total_price * low_mult)
    high = max(MINIMUM_SERVICE_PRICE, total_price * high_mult)
    return money(low), money(high)


def add_residential_addons(square_feet: int, oven: bool, fridge: bool, windows: bool,
                           carpet: bool, pressure: bool, bins: bool):
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
        carpet_price = square_feet * 0.35
        add_ons_total += carpet_price
        add_on_details.append(("Carpet Cleaning", money(carpet_price)))
    if pressure:
        pressure_price = square_feet * 0.37
        add_ons_total += pressure_price
        add_on_details.append(("Pressure Washing", money(pressure_price)))
    if bins:
        bin_price = 17 if (oven or fridge or windows or carpet or pressure) else 20
        add_ons_total += bin_price
        add_on_details.append(("Trash Bin Cleaning", bin_price))

    return money(add_ons_total), add_on_details


def calculate_residential(square_feet: int, bedrooms: int, bathrooms: int, half_baths: int,
                          stories: int, condition: str, oven: bool, fridge: bool,
                          windows: bool, carpet: bool, pressure: bool, bins: bool):

    base_hours = estimate_base_hours(square_feet)
    detail_hours = estimate_detail_hours(bedrooms, bathrooms, half_baths, stories)
    total_hours = base_hours + detail_hours

    base_price = total_hours * RESIDENTIAL_RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    after_sqft = base_price * (1 + sqft_adjustment)

    condition_mult = CONDITION_MULTIPLIERS.get(condition, 1.00)
    conditioned_subtotal = after_sqft * condition_mult

    add_ons_total, add_on_details = add_residential_addons(
        square_feet, oven, fridge, windows, carpet, pressure, bins
    )

    service_rows = []

    for service_key, service_mult in SERVICE_MULTIPLIERS.items():
        one_time_total = conditioned_subtotal * service_mult + add_ons_total
        one_time_total = max(one_time_total, MINIMUM_SERVICE_PRICE)

        weekly_total = max(one_time_total * (1 - RECURRING_DISCOUNTS["weekly"]), MINIMUM_SERVICE_PRICE)
        biweekly_total = max(one_time_total * (1 - RECURRING_DISCOUNTS["biweekly"]), MINIMUM_SERVICE_PRICE)
        monthly_total = max(one_time_total * (1 - RECURRING_DISCOUNTS["monthly"]), MINIMUM_SERVICE_PRICE)

        low_range, high_range = build_range(one_time_total, condition)

        service_rows.append({
            "key": service_key,
            "label": {
                "basic": "Basic Cleaning",
                "first_time": "First-Time Cleaning",
                "deep": "Deep Cleaning",
            }[service_key],
            "multiplier": service_mult,
            "one_time": money(one_time_total),
            "weekly": money(weekly_total),
            "biweekly": money(biweekly_total),
            "monthly": money(monthly_total),
            "range_low": low_range,
            "range_high": high_range,
        })

    return {
        "square_feet": square_feet,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "half_baths": half_baths,
        "stories": stories,
        "condition": condition,
        "base_hours": money(base_hours),
        "detail_hours": money(detail_hours),
        "total_hours": money(total_hours),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "condition_pct": int((condition_mult - 1) * 100),
        "add_ons_total": money(add_ons_total),
        "add_on_details": add_on_details,
        "rows": service_rows,
    }


def calculate_realtor(square_feet: int, service_type: str, rush_type: str, condition: str):
    base_hours = estimate_base_hours(square_feet)
    base_price = base_hours * RESIDENTIAL_RATE_PER_HOUR

    sqft_adjustment = get_sqft_adjustment(square_feet)
    after_sqft = base_price * (1 + sqft_adjustment)

    condition_mult = CONDITION_MULTIPLIERS.get(condition, 1.00)
    after_condition = after_sqft * condition_mult

    service_mult = REALTOR_MULTIPLIERS.get(service_type, 1.00)
    subtotal = after_condition * service_mult

    rush_pct = RUSH_FEES.get(rush_type, 0.00)
    total = subtotal * (1 + rush_pct)

    if service_type == "open_house_touchup":
        total = max(total, OPEN_HOUSE_MINIMUM)
    else:
        total = max(total, MINIMUM_SERVICE_PRICE)

    range_low, range_high = build_range(total, condition)

    return {
        "square_feet": square_feet,
        "service_type": service_type,
        "service_label": {
            "listing_prep": "Listing Preparation",
            "vacant_move_out": "Vacant / Move-Out",
            "post_renovation": "Post-Renovation Cleaning",
            "open_house_touchup": "Open House Touch-Up",
        }[service_type],
        "rush_type": rush_type,
        "rush_label": {
            "none": "None",
            "next_day": "Next-Day",
            "same_day": "Same-Day",
        }[rush_type],
        "condition": condition,
        "base_hours": money(base_hours),
        "base_price": money(base_price),
        "sqft_adjustment_pct": int(sqft_adjustment * 100),
        "condition_pct": int((condition_mult - 1) * 100),
        "service_multiplier": service_mult,
        "rush_pct": int(rush_pct * 100),
        "total": money(total),
        "range_low": range_low,
        "range_high": range_high,
    }


def calculate_exterior(pressure_sqft: float, carpet_sqft: float, trash_bins: int, bins_with_service: bool):
    pressure_total = pressure_sqft * 0.37
    carpet_total = carpet_sqft * 0.35
    bin_price = 17 if bins_with_service else 20
    bins_total = trash_bins * bin_price if trash_bins > 0 else 0
    total = pressure_total + carpet_total + bins_total

    return {
        "pressure_sqft": pressure_sqft,
        "carpet_sqft": carpet_sqft,
        "trash_bins": trash_bins,
        "bins_with_service": bins_with_service,
        "pressure_total": money(pressure_total),
        "carpet_total": money(carpet_total),
        "bins_total": money(bins_total),
        "total": money(total),
    }


# ----------------------------
# ROUTE
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    active_tab = "residential"
    residential_result = None
    realtor_result = None
    exterior_result = None

    if request.method == "POST":
        form_type = request.form.get("form_type", "residential")
        active_tab = form_type

        if form_type == "residential":
            square_feet = safe_int(request.form.get("square_feet"))
            bedrooms = safe_int(request.form.get("bedrooms"))
            bathrooms = safe_int(request.form.get("bathrooms"))
            half_baths = safe_int(request.form.get("half_baths"))
            stories = safe_int(request.form.get("stories"), 1)

            condition = request.form.get("condition", "normal")

            oven = "oven" in request.form
            fridge = "fridge" in request.form
            windows = "windows" in request.form
            carpet = "carpet" in request.form
            pressure = "pressure" in request.form
            bins = "bins" in request.form

            residential_result = calculate_residential(
                square_feet=square_feet,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                half_baths=half_baths,
                stories=stories,
                condition=condition,
                oven=oven,
                fridge=fridge,
                windows=windows,
                carpet=carpet,
                pressure=pressure,
                bins=bins
            )

        elif form_type == "realtor":
            square_feet = safe_int(request.form.get("realtor_square_feet"))
            service_type = request.form.get("service_type", "listing_prep")
            rush_type = request.form.get("rush_type", "none")
            condition = request.form.get("realtor_condition", "normal")

            realtor_result = calculate_realtor(
                square_feet=square_feet,
                service_type=service_type,
                rush_type=rush_type,
                condition=condition
            )

        elif form_type == "exterior":
            pressure_sqft = safe_float(request.form.get("pressure_sqft"))
            carpet_sqft = safe_float(request.form.get("carpet_sqft"))
            trash_bins = safe_int(request.form.get("trash_bins"), 0)
            bins_with_service = request.form.get("bins_with_service") == "yes"

            exterior_result = calculate_exterior(
                pressure_sqft=pressure_sqft,
                carpet_sqft=carpet_sqft,
                trash_bins=trash_bins,
                bins_with_service=bins_with_service
            )

    return render_template(
        "index.html",
        active_tab=active_tab,
        residential_result=residential_result,
        realtor_result=realtor_result,
        exterior_result=exterior_result
    )


if __name__ == "__main__":
    app.run(debug=True)
