from flask import Flask, render_template, request
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)

# ----------------------------
# SETTINGS
# ----------------------------

RESIDENTIAL_RATE_PER_HOUR = 70
COMMERCIAL_JANITORIAL_RATE_PER_HOUR = 63
MINIMUM_SERVICE_PRICE = 150
OPEN_HOUSE_MINIMUM = 150

CARPET_RATES = {
    "residential": 0.37,
    "commercial": 0.30,
}

PRESSURE_WASHING_RATES = {
    "standard": 0.40,
    "dirty": 0.45,
}
PRESSURE_WASHING_MINIMUM = 130
PRESSURE_WASHING_STAIN_ADDONS = {
    "none": ("No stain add-on", 0),
    "oil_stain_light": ("Oil stain treatment (light)", 40),
    "oil_stain_heavy": ("Oil stain treatment (heavy)", 80),
    "rust_stain_light": ("Rust stain removal (light)", 50),
    "rust_stain_heavy": ("Rust stain removal (heavy)", 120),
    "heavy_buildup": ("Heavy buildup treatment", 60),
}

FLOOR_CARE_RATES = {
    "standard": 0.28,
    "heavy": 0.35,
}
FLOOR_CARE_MINIMUM = 120
COUCH_CLEANING_PRICE = 75

RECURRING_DISCOUNTS = {
    "weekly": 0.20,
    "biweekly": 0.15,
    "monthly": 0.10,
}

ECO_MULTIPLIER = Decimal("1.10")

RESIDENTIAL_PACKAGE_TIME_CONFIG = {
    "basic": {
        "bedroom": Decimal("20"),
        "bathroom": Decimal("35"),
        "kitchen": Decimal("45"),
        "living_room": Decimal("30"),
        "hallway": Decimal("15"),
        "detail_load_hours": Decimal("0.00"),
    },
    "plus": {
        "bedroom": Decimal("30"),
        "bathroom": Decimal("47.5"),
        "kitchen": Decimal("65"),
        "living_room": Decimal("45"),
        "hallway": Decimal("20"),
        "detail_load_hours": Decimal("0.75"),
    },
    "deep": {
        "bedroom": Decimal("42.5"),
        "bathroom": Decimal("65"),
        "kitchen": Decimal("95"),
        "living_room": Decimal("60"),
        "hallway": Decimal("25"),
        "detail_load_hours": Decimal("1.00"),
    },
}

USE_RESIDENTIAL_PACKAGE_TIME_FORMULAS = True

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

CONDITION_ADJUSTMENTS = {
    "normal": 0.00,
    "dirty": 0.10,
    "very_dirty": 0.20,
}

RESIDENTIAL_AUTO_BUNDLES = [
    {
        "key": "full_property_reset",
        "name": "Full Property Reset",
        "discount": Decimal("0.12"),
        "required": ["is_deep", "has_carpet", "has_floor_care", "has_pressure"],
        "eligible_parts": ["residential", "carpet", "floor_care", "pressure"],
    },
    {
        "key": "home_refresh",
        "name": "Home Refresh",
        "discount": Decimal("0.09"),
        "required": ["is_deep", "has_carpet"],
        "eligible_parts": ["residential", "carpet"],
    },
]

RESIDENTIAL_SERVICE_DETAILS = {
    "basic": {
        "label": "Basic Cleaning",
        "purpose": "Maintenance/upkeep cleaning for homes already in good condition.",
        "includes": [
            "Dusting all reachable surfaces + light wipe-down",
            "Cobweb removal and trash removal",
            "Floors vacuumed and mopped",
            "Reachable vent covers dusted/wiped",
            "Kitchen: countertops, sink, appliance exteriors, light wipe-down",
            "Bathrooms: toilet, sink/counters, mirrors, light shower/tub clean",
            "Living areas/bedrooms: dusting, light wipe-down, reset appearance",
        ],
        "not_included": [
            "No heavy scrubbing or buildup removal",
            "No inside oven or inside fridge",
            "No heavy degreasing",
        ],
    },
    "plus": {
        "label": "Plus Cleaning",
        "purpose": "Detailed premium maintenance cleaning. Most popular and best value.",
        "includes": [
            "Everything in Basic",
            "Full dusting with more detailed wipe-down",
            "Baseboards spot cleaned",
            "Light switches and door handles sanitized",
            "Reachable vent covers detailed wiped",
            "Rotational detail focus (baseboards, doors, or window sills)",
            "Kitchen: inside microwave, cabinet fronts, stovetop light/moderate degreasing, backsplash",
            "Bathrooms: soap scum/mineral buildup removal, scrubbed shower/tub, polished fixtures",
            "Living areas/bedrooms: detailed dusting + light organizing/reset",
        ],
        "not_included": [
            "No heavy restoration or unlimited buildup labor",
            "No moving appliances/furniture",
        ],
    },
    "deep": {
        "label": "Deep Cleaning",
        "purpose": "First-time, reset, or heavy-attention clean with the deepest detail level.",
        "includes": [
            "Everything in Plus",
            "Full baseboard cleaning",
            "Doors and door frames detailed",
            "Window sills and tracks cleaned",
            "Heavy dust removal and detailed wipe-down throughout",
            "Reachable vent covers thoroughly cleaned",
            "Kitchen: inside microwave + inside oven/fridge (standard condition)",
            "Heavy kitchen degreasing and cabinet fronts deep cleaned",
            "Bathrooms: full soap scum/mineral removal, grout focus (light/moderate)",
            "Living areas/bedrooms: lower-detail focus and intensive vacuuming/detailing",
        ],
        "not_included": [
            "Extreme buildup may require additional labor/pricing",
            "Inside oven/fridge included for standard condition only",
            "No moving appliances or heavy furniture by default",
        ],
    },
}

REALTOR_SERVICE_DETAILS = {
    "listing_prep": {
        "label": "Listing Prep Cleaning",
        "purpose": "Prepare a home for listing photos and showings.",
        "includes": [
            "Counters wiped",
            "Bathrooms cleaned",
            "Dusting",
            "Floors vacuumed and mopped",
            "General detail cleaning",
        ],
        "not_included": [
            "Inside appliances unless added",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "vacant_move_out": {
        "label": "Vacant / Move-Out Cleaning",
        "purpose": "Cleaning for empty homes before listing or after move-out.",
        "includes": [
            "Kitchen cleaning",
            "Bathroom detail cleaning",
            "Closets dusted",
            "Floors vacuumed and mopped",
            "Trash removal",
        ],
        "not_included": [
            "Heavy stain removal",
            "Carpet cleaning unless added",
            "Pressure washing unless added",
        ],
    },
    "post_renovation": {
        "label": "Post-Renovation Cleaning",
        "purpose": "Cleaning after remodeling or repair work.",
        "includes": [
            "Dust removal from surfaces",
            "Counters and fixtures cleaned",
            "Floors vacuumed",
            "Floors swept and mopped",
            "Bathroom wipe-down",
        ],
        "not_included": [
            "Paint removal",
            "Adhesive removal",
            "Heavy debris hauling",
        ],
    },
    "open_house_touchup": {
        "label": "Open House Touch-Up",
        "purpose": "Quick refresh before an open house or showing.",
        "includes": [
            "Quick countertop wipe-down",
            "Bathroom touch-up",
            "Mirror cleaning",
            "Quick vacuum or sweep",
            "Quick dusting",
        ],
        "not_included": [
            "Deep cleaning",
            "Appliance interior cleaning",
            "Detailed buildup removal",
        ],
    },
}

COMMERCIAL_SERVICE_DETAILS = {
    "janitorial": {
        "label": "Commercial Janitorial",
        "description": "General office and facility cleaning for one-time or recurring needs.",
    },
    "carpet": {
        "label": "Commercial Carpet Cleaning",
        "description": "Low-moisture commercial carpet refresh by square footage.",
    },
    "floor_care": {
        "label": "Floor Cleaning & Shine",
        "description": "Broad floor care for scrubbing and shine-focused maintenance.",
    },
}

# helpers + existing functions

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


def round_to_one_decimal(value):
    return float(Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def round_to_clean_price(value, increment=5):
    if value <= 0:
        return 0
    return int(round(float(value) / increment) * increment)


def calculate_floor_care_total(floor_care_sqft, floor_care_condition, apply_rounding=True):
    if floor_care_sqft <= 0:
        return 0.0, []

    floor_rate = FLOOR_CARE_RATES.get(floor_care_condition, FLOOR_CARE_RATES["standard"])
    base_total = floor_care_sqft * floor_rate
    floor_total = max(base_total, FLOOR_CARE_MINIMUM)

    value = money(base_total) if apply_rounding else base_total
    details = [(f"Floor Cleaning & Shine ({floor_care_condition.title()}) ({floor_care_sqft:g} sq ft × ${floor_rate:.2f})", value)]

    if base_total < FLOOR_CARE_MINIMUM:
        minimum_delta = money(FLOOR_CARE_MINIMUM - base_total) if apply_rounding else (FLOOR_CARE_MINIMUM - base_total)
        details.append(("Floor Care Minimum Applied", minimum_delta))

    return money(floor_total) if apply_rounding else floor_total, details


def select_best_bundle(base_total, selections):
    bundle_candidates = []
    if selections.get("deep_cleaning") and selections.get("carpet_cleaning"):
        bundle_candidates.append(("Home Refresh", 0.09))
    if selections.get("vacant_cleaning") and selections.get("carpet_cleaning"):
        bundle_candidates.append(("Move-Out Reset", 0.10))
    if all(selections.get(key) for key in ["deep_cleaning", "carpet_cleaning", "floor_care", "pressure_washing"]):
        bundle_candidates.append(("Full Property Reset", 0.12))
    if not bundle_candidates:
        return None
    best_bundle = None
    for bundle_name, discount_pct in bundle_candidates:
        discounted_total = round_to_clean_price(base_total * (1 - discount_pct))
        savings = round_to_clean_price(max(base_total - discounted_total, 0))
        bundle_data = {"name": bundle_name, "discount_pct": int(discount_pct * 100), "bundle_price": discounted_total, "savings": savings}
        if best_bundle is None or bundle_data["savings"] > best_bundle["savings"]:
            best_bundle = bundle_data
    return best_bundle


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


def to_decimal(value) -> Decimal:
    return Decimal(str(value))


def residential_formula_minutes(service_key, bedrooms, bathrooms, kitchens, living_rooms, hallways):
    package_minutes = RESIDENTIAL_PACKAGE_TIME_CONFIG.get(service_key, RESIDENTIAL_PACKAGE_TIME_CONFIG["basic"])
    return (
        (bedrooms * package_minutes["bedroom"]) +
        (bathrooms * package_minutes["bathroom"]) +
        (kitchens * package_minutes["kitchen"]) +
        (living_rooms * package_minutes["living_room"]) +
        (hallways * package_minutes["hallway"])
    )


def calculate_residential_package_totals(labor_price, addon_total, eco_selected):
    eco_adjustment = (labor_price * (ECO_MULTIPLIER - Decimal("1.00"))) if eco_selected else Decimal("0.00")
    normal_price = max(labor_price + addon_total + eco_adjustment, to_decimal(MINIMUM_SERVICE_PRICE))
    weekly_price = max(normal_price * (Decimal(1) - to_decimal(RECURRING_DISCOUNTS["weekly"])), to_decimal(MINIMUM_SERVICE_PRICE))
    biweekly_price = max(normal_price * (Decimal(1) - to_decimal(RECURRING_DISCOUNTS["biweekly"])), to_decimal(MINIMUM_SERVICE_PRICE))
    monthly_price = max(normal_price * (Decimal(1) - to_decimal(RECURRING_DISCOUNTS["monthly"])), to_decimal(MINIMUM_SERVICE_PRICE))

    return {
        "normal": normal_price,
        "weekly": weekly_price,
        "biweekly": biweekly_price,
        "monthly": monthly_price,
        "eco_adjustment": eco_adjustment,
    }


def realtor_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways):
    return ((bedrooms * 0.6) + (bathrooms * 1.0) + (kitchens * 1.25) + (living_rooms * 0.5) + (dining_rooms * 0.5) + (hallways * 0.25))


def calculate_addons(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft=0, floor_care_condition="standard", service_context="residential", pressure_condition="standard", pressure_stain_addon="none", couch_cleaning=False, apply_rounding=True):
    addon_details = []
    addon_total = 0.0
    if window_count > 0:
        total = window_count * 5
        addon_total += total
        addon_details.append(("Window Cleaning", money(total) if apply_rounding else total))
    if oven:
        addon_total += 25
        addon_details.append(("Inside Oven Cleaning", 25))
    if fridge:
        addon_total += 20
        addon_details.append(("Inside Refrigerator Cleaning", 20))
    if carpet_sqft > 0:
        carpet_rate = CARPET_RATES["residential"] if service_context == "residential" else CARPET_RATES["commercial"]
        total = carpet_sqft * carpet_rate
        addon_total += total
        addon_details.append((f"Carpet Cleaning ({carpet_sqft:g} sq ft × ${carpet_rate:.2f})", money(total) if apply_rounding else total))
    if pressure_sqft > 0:
        pressure_rate = PRESSURE_WASHING_RATES.get(pressure_condition, PRESSURE_WASHING_RATES["standard"])
        base_total = pressure_sqft * pressure_rate
        pressure_base_after_minimum = max(base_total, PRESSURE_WASHING_MINIMUM)
        addon_total += pressure_base_after_minimum
        addon_details.append((f"Pressure Washing ({pressure_condition.title()}) ({pressure_sqft:g} sq ft × ${pressure_rate:.2f})", money(base_total) if apply_rounding else base_total))
        if base_total < PRESSURE_WASHING_MINIMUM:
            addon_details.append(("Pressure Washing Minimum Applied", money(PRESSURE_WASHING_MINIMUM - base_total) if apply_rounding else (PRESSURE_WASHING_MINIMUM - base_total)))
        stain_label, stain_amount = PRESSURE_WASHING_STAIN_ADDONS.get(pressure_stain_addon, PRESSURE_WASHING_STAIN_ADDONS["none"])
        if stain_amount > 0:
            addon_total += stain_amount
            addon_details.append((stain_label, stain_amount))
    floor_care_total, floor_care_details = calculate_floor_care_total(floor_care_sqft, floor_care_condition, apply_rounding=apply_rounding)
    if floor_care_total > 0:
        addon_total += floor_care_total
        addon_details.extend(floor_care_details)
    if bins > 0:
        has_other_service = (window_count > 0 or oven or fridge or carpet_sqft > 0 or pressure_sqft > 0 or floor_care_sqft > 0)
        bin_rate = 17 if has_other_service else 20
        total = bins * bin_rate
        addon_total += total
        addon_details.append(("Trash Bin Cleaning", money(total) if apply_rounding else total))
    if couch_cleaning:
        addon_total += COUCH_CLEANING_PRICE
        addon_details.append(("Couch Cleaning", COUCH_CLEANING_PRICE))
    return (money(addon_total) if apply_rounding else addon_total), addon_details


def build_residential_rows(square_feet, bedrooms, bathrooms, kitchens, living_rooms, hallways, addon_total, eco_selected, use_package_time_formulas=True):
    rows = []
    hourly_rate = to_decimal(RESIDENTIAL_RATE_PER_HOUR)
    addon_total_dec = to_decimal(addon_total)
    for key in RESIDENTIAL_PACKAGE_TIME_CONFIG:
        label = RESIDENTIAL_SERVICE_DETAILS[key]["label"]
        formula_service_key = key if use_package_time_formulas else "basic"
        base_minutes = residential_formula_minutes(formula_service_key, bedrooms, bathrooms, kitchens, living_rooms, hallways)
        detail_load_hours = RESIDENTIAL_PACKAGE_TIME_CONFIG[key]["detail_load_hours"]
        base_hours = Decimal(base_minutes) / Decimal(60)
        total_labor_hours = base_hours + detail_load_hours
        labor_price = total_labor_hours * hourly_rate
        package_totals = calculate_residential_package_totals(
            labor_price=labor_price,
            addon_total=addon_total_dec,
            eco_selected=eco_selected,
        )
        rows.append({
            "key": key,
            "label": label,
            "minutes": base_minutes,
            "base_hours": base_hours,
            "detail_load_hours": detail_load_hours,
            "hours": total_labor_hours,
            "base_price": labor_price,
            "uses_package_time_formulas": use_package_time_formulas,
            "normal": package_totals["normal"],
            "weekly": package_totals["weekly"],
            "biweekly": package_totals["biweekly"],
            "monthly": package_totals["monthly"],
            "eco_adjustment": package_totals["eco_adjustment"],
            "purpose": RESIDENTIAL_SERVICE_DETAILS[key]["purpose"],
            "includes": RESIDENTIAL_SERVICE_DETAILS[key]["includes"],
            "not_included": RESIDENTIAL_SERVICE_DETAILS[key]["not_included"],
        })
    return rows


def calculate_residential_service_totals(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft, floor_care_condition="standard", pressure_condition="standard", pressure_stain_addon="none", couch_cleaning=False):
    additional_services = []
    add_ons = []
    carpet_total = Decimal("0")
    pressure_total = Decimal("0")
    floor_care_total = Decimal("0")

    if carpet_sqft > 0:
        carpet_rate = to_decimal(CARPET_RATES["residential"])
        carpet_total = to_decimal(carpet_sqft) * carpet_rate
        additional_services.append({
            "name": f"Carpet Cleaning ({carpet_sqft:g} sq ft × ${CARPET_RATES['residential']:.2f})",
            "amount": carpet_total,
            "key": "carpet",
        })

    if pressure_sqft > 0:
        pressure_rate = to_decimal(PRESSURE_WASHING_RATES.get(pressure_condition, PRESSURE_WASHING_RATES["standard"]))
        pressure_base = to_decimal(pressure_sqft) * pressure_rate
        pressure_total = max(pressure_base, to_decimal(PRESSURE_WASHING_MINIMUM))
        stain_label, stain_amount = PRESSURE_WASHING_STAIN_ADDONS.get(pressure_stain_addon, PRESSURE_WASHING_STAIN_ADDONS["none"])
        pressure_total += to_decimal(stain_amount)
        pressure_name = f"Pressure Washing ({pressure_condition.title()}) ({pressure_sqft:g} sq ft × ${float(pressure_rate):.2f})"
        if stain_amount > 0:
            pressure_name += f" + {stain_label}"
        additional_services.append({"name": pressure_name, "amount": pressure_total, "key": "pressure"})

    if floor_care_sqft > 0:
        floor_care_rate = to_decimal(FLOOR_CARE_RATES.get(floor_care_condition, FLOOR_CARE_RATES["standard"]))
        floor_base = to_decimal(floor_care_sqft) * floor_care_rate
        floor_care_total = max(floor_base, to_decimal(FLOOR_CARE_MINIMUM))
        add_ons.append({
            "name": f"Floor Cleaning & Shine ({floor_care_condition.title()}) ({floor_care_sqft:g} sq ft × ${float(floor_care_rate):.2f})",
            "amount": floor_care_total,
            "key": "floor_care",
        })

    if window_count > 0:
        add_ons.append({"name": "Window Cleaning", "amount": to_decimal(window_count * 5), "key": "window"})
    if oven:
        add_ons.append({"name": "Inside Oven Cleaning", "amount": to_decimal(25), "key": "oven"})
    if fridge:
        add_ons.append({"name": "Inside Refrigerator Cleaning", "amount": to_decimal(20), "key": "fridge"})
    if couch_cleaning:
        add_ons.append({"name": "Couch Cleaning", "amount": to_decimal(COUCH_CLEANING_PRICE), "key": "couch"})

    if bins > 0:
        has_other_service = any([window_count > 0, oven, fridge, carpet_sqft > 0, pressure_sqft > 0, floor_care_sqft > 0, couch_cleaning])
        bin_rate = 17 if has_other_service else 20
        add_ons.append({"name": "Trash Bin Cleaning", "amount": to_decimal(bins * bin_rate), "key": "bins"})

    return {
        "additional_services": additional_services,
        "add_ons": add_ons,
        "carpet_total": carpet_total,
        "pressure_total": pressure_total,
        "floor_care_total": floor_care_total,
        "additional_services_total": sum(item["amount"] for item in additional_services),
        "add_ons_total": sum(item["amount"] for item in add_ons),
    }


def detect_residential_bundle(chosen_service, carpet_total, pressure_total, floor_care_total, residential_price):
    flags = {
        "is_deep": chosen_service == "deep",
        "has_carpet": carpet_total > 0,
        "has_pressure": pressure_total > 0,
        "has_floor_care": floor_care_total > 0,
    }
    part_prices = {
        "residential": residential_price,
        "carpet": carpet_total,
        "pressure": pressure_total,
        "floor_care": floor_care_total,
    }

    for bundle in RESIDENTIAL_AUTO_BUNDLES:
        if all(flags.get(flag) for flag in bundle["required"]):
            eligible_subtotal = sum(part_prices[part] for part in bundle["eligible_parts"])
            discount_amount = eligible_subtotal * bundle["discount"]
            return {
                "key": bundle["key"],
                "name": bundle["name"],
                "discount_pct": int(bundle["discount"] * 100),
                "eligible_subtotal": eligible_subtotal,
                "amount": discount_amount,
            }
    return None


def calculate_residential(square_feet, bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways, window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft, floor_care_condition="standard", pressure_condition="standard", pressure_stain_addon="none", couch_cleaning=False, chosen_service="", selected_frequency="one_time", eco_friendly=False):
    valid_service = chosen_service if chosen_service in RESIDENTIAL_PACKAGE_TIME_CONFIG else ""

    rows = build_residential_rows(
        square_feet=square_feet,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        kitchens=kitchens,
        living_rooms=living_rooms,
        hallways=hallways,
        addon_total=Decimal("0"),
        eco_selected=False,
        use_package_time_formulas=USE_RESIDENTIAL_PACKAGE_TIME_FORMULAS,
    )

    chosen_row = next((row for row in rows if row["key"] == valid_service), None)
    selected_minutes = chosen_row["minutes"] if chosen_row else 0
    selected_base_hours = chosen_row["base_hours"] if chosen_row else Decimal(0)
    selected_detail_load_hours = chosen_row["detail_load_hours"] if chosen_row else Decimal(0)
    selected_hours = chosen_row["hours"] if chosen_row else Decimal(0)
    selected_base_price = chosen_row["base_price"] if chosen_row else Decimal(0)

    service_totals = calculate_residential_service_totals(
        window_count=window_count,
        oven=oven,
        fridge=fridge,
        carpet_sqft=carpet_sqft,
        pressure_sqft=pressure_sqft,
        bins=bins,
        floor_care_sqft=floor_care_sqft,
        floor_care_condition=floor_care_condition,
        pressure_condition=pressure_condition,
        pressure_stain_addon=pressure_stain_addon,
        couch_cleaning=couch_cleaning,
    )

    residential_price = selected_base_price
    eco_adjustment = residential_price * (ECO_MULTIPLIER - Decimal("1.00")) if eco_friendly else Decimal("0")

    subtotal_before_bundle = residential_price + service_totals["additional_services_total"] + service_totals["add_ons_total"]
    applied_bundle = detect_residential_bundle(
        chosen_service=valid_service,
        carpet_total=service_totals["carpet_total"],
        pressure_total=service_totals["pressure_total"],
        floor_care_total=service_totals["floor_care_total"],
        residential_price=residential_price,
    )
    bundle_discount_amount = applied_bundle["amount"] if applied_bundle else Decimal("0")

    total_before_recurring = subtotal_before_bundle - bundle_discount_amount + eco_adjustment
    total_with_minimum = max(total_before_recurring, to_decimal(MINIMUM_SERVICE_PRICE))

    recurring_map = {"weekly": RECURRING_DISCOUNTS["weekly"], "biweekly": RECURRING_DISCOUNTS["biweekly"], "monthly": RECURRING_DISCOUNTS["monthly"], "one_time": 0}
    recurring_pct = to_decimal(recurring_map.get(selected_frequency, 0))
    recurring_discount_amount = total_with_minimum * recurring_pct
    final_quote = total_with_minimum - recurring_discount_amount

    selected_frequency_label = {
        "weekly": "Weekly",
        "biweekly": "Biweekly",
        "monthly": "Monthly",
        "one_time": "One-Time",
    }.get(selected_frequency, "One-Time")

    return {
        "square_feet": square_feet,
        "formula_units": selected_hours,
        "base_minutes": selected_minutes,
        "room_time_hours": selected_base_hours,
        "detail_load_hours": selected_detail_load_hours,
        "base_hours": selected_hours,
        "base_price": residential_price,
        "eco_selected": eco_friendly,
        "eco_adjustment": eco_adjustment,
        "rows": rows,
        "chosen_service": valid_service,
        "chosen_service_label": RESIDENTIAL_SERVICE_DETAILS[valid_service]["label"] if valid_service else "No package selected",
        "uses_package_time_formulas": USE_RESIDENTIAL_PACKAGE_TIME_FORMULAS,
        "chosen_frequency": selected_frequency,
        "chosen_frequency_label": selected_frequency_label,
        "additional_services": service_totals["additional_services"],
        "additional_services_total": service_totals["additional_services_total"],
        "add_ons": service_totals["add_ons"],
        "add_ons_total": service_totals["add_ons_total"],
        "subtotal_before_bundle": subtotal_before_bundle,
        "applied_bundle": applied_bundle,
        "bundle_discount_amount": bundle_discount_amount,
        "total_before_recurring": total_with_minimum,
        "recurring_discount_pct": int(recurring_pct * 100),
        "recurring_discount_amount": recurring_discount_amount,
        "final_quote": final_quote,
        "final_quote_display": round_to_one_decimal(final_quote),
    }


def calculate_realtor(square_feet, bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways, service_type, rush_type, condition, window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft, floor_care_condition="standard", pressure_condition="standard", pressure_stain_addon="none"):
    formula_units = realtor_formula_units(bedrooms, bathrooms, kitchens, living_rooms, dining_rooms, hallways)
    base_price = formula_units * COMMERCIAL_JANITORIAL_RATE_PER_HOUR
    sqft_adjustment = get_sqft_adjustment(square_feet)
    subtotal = base_price * (1 + sqft_adjustment)
    subtotal *= (1 + CONDITION_ADJUSTMENTS.get(condition, 0.00))
    service_multiplier = REALTOR_MULTIPLIERS.get(service_type, 1.00)
    subtotal *= service_multiplier
    addon_total, addon_details = calculate_addons(window_count, oven, fridge, carpet_sqft, pressure_sqft, bins, floor_care_sqft=floor_care_sqft, floor_care_condition=floor_care_condition, service_context="commercial", pressure_condition=pressure_condition, pressure_stain_addon=pressure_stain_addon)
    subtotal += addon_total
    rush_pct = RUSH_FEES.get(rush_type, 0.00)
    total = subtotal * (1 + rush_pct)
    total = max(total, OPEN_HOUSE_MINIMUM if service_type == "open_house_touchup" else MINIMUM_SERVICE_PRICE)
    details = REALTOR_SERVICE_DETAILS[service_type]
    individual_total = round_to_clean_price(total)
    bundle_selection = {"deep_cleaning": service_type == "post_renovation", "vacant_cleaning": service_type == "vacant_move_out", "carpet_cleaning": carpet_sqft > 0, "floor_care": floor_care_sqft > 0, "pressure_washing": pressure_sqft > 0}
    best_bundle = select_best_bundle(individual_total, bundle_selection)
    return {"formula_units": money(formula_units), "base_price": money(base_price), "sqft_adjustment_pct": int(sqft_adjustment * 100), "condition_label": {"normal": "Normal", "dirty": "Dirty", "very_dirty": "Very Dirty"}[condition], "service_label": details["label"], "purpose": details["purpose"], "includes": details["includes"], "not_included": details["not_included"], "rush_label": {"none": "None", "next_day": "Next-Day", "same_day": "Same-Day"}[rush_type], "addon_total": addon_total, "addon_details": addon_details, "service_multiplier": service_multiplier, "rush_pct": int(rush_pct * 100), "total": individual_total, "bundle_offer": best_bundle, "individual_service_total": individual_total}


def calculate_commercial(square_feet, service_type, recurring, carpet_sqft, floor_care_sqft, floor_care_condition="standard"):
    details = COMMERCIAL_SERVICE_DETAILS.get(service_type, COMMERCIAL_SERVICE_DETAILS["janitorial"])
    base_price = 0.0
    line_item = ""
    if service_type == "carpet":
        base_price = max(carpet_sqft * CARPET_RATES["commercial"], MINIMUM_SERVICE_PRICE)
        line_item = f"Commercial Carpet Cleaning ({carpet_sqft:g} sq ft × ${CARPET_RATES['commercial']:.2f})"
    elif service_type == "floor_care":
        base_price, floor_details = calculate_floor_care_total(floor_care_sqft, floor_care_condition)
        line_item = floor_details[0][0] if floor_details else "Floor Cleaning & Shine"
    else:
        units = max((square_feet / 1000) * 1.25, 1.5)
        raw = units * COMMERCIAL_JANITORIAL_RATE_PER_HOUR
        base_price = max(raw, MINIMUM_SERVICE_PRICE)
        line_item = f"Commercial Janitorial ({units:.2f} labor units × ${COMMERCIAL_JANITORIAL_RATE_PER_HOUR}/hr)"
    recurring_total = base_price
    if recurring in RECURRING_DISCOUNTS:
        recurring_total = base_price * (1 - RECURRING_DISCOUNTS[recurring])
    return {
        "service_label": details["label"],
        "description": details["description"],
        "line_item": line_item,
        "base_total": round_to_clean_price(base_price),
        "recurring_label": {"none": "One-Time", "weekly": "Weekly", "biweekly": "Every 2 Weeks", "monthly": "Every 4 Weeks"}.get(recurring, "One-Time"),
        "recurring_pct": int(RECURRING_DISCOUNTS.get(recurring, 0) * 100),
        "final_total": round_to_clean_price(recurring_total),
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    active_tab = 'residential'
    residential_result = None
    realtor_result = None
    commercial_result = None

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'residential')
        active_tab = form_type
        if form_type == 'residential':
            carpet_selected = request.form.get('include_carpet') == 'on'
            pressure_selected = request.form.get('include_pressure') == 'on'
            floor_selected = request.form.get('include_floor_care') == 'on'
            bin_selected = request.form.get('include_bins') == 'on'
            residential_result = calculate_residential(
                square_feet=safe_int(request.form.get('square_feet')),
                bedrooms=safe_int(request.form.get('bedrooms')),
                bathrooms=safe_int(request.form.get('bathrooms')),
                kitchens=safe_int(request.form.get('kitchens'), 1),
                living_rooms=safe_int(request.form.get('living_rooms'), 1),
                dining_rooms=safe_int(request.form.get('dining_rooms'), 1),
                hallways=safe_int(request.form.get('hallways'), 1),
                window_count=safe_int(request.form.get('window_count')),
                oven=('oven' in request.form),
                fridge=('fridge' in request.form),
                carpet_sqft=safe_float(request.form.get('carpet_sqft')) if carpet_selected else 0,
                pressure_sqft=safe_float(request.form.get('pressure_sqft')) if pressure_selected else 0,
                bins=safe_int(request.form.get('bins')) if bin_selected else 0,
                floor_care_sqft=safe_float(request.form.get('floor_care_sqft')) if floor_selected else 0,
                floor_care_condition=request.form.get('floor_care_condition', 'standard'),
                pressure_condition=request.form.get('pressure_condition', 'standard'),
                pressure_stain_addon=request.form.get('pressure_stain_addon', 'none'),
                couch_cleaning=(request.form.get('include_couch_cleaning') == 'on'),
                chosen_service=request.form.get('chosen_service', ''),
                selected_frequency=request.form.get('display_frequency', 'one_time'),
                eco_friendly=(request.form.get('eco_friendly') == 'on'),
            )
        elif form_type == 'realtor':
            realtor_result = calculate_realtor(
                square_feet=safe_int(request.form.get('realtor_square_feet')),
                bedrooms=safe_int(request.form.get('realtor_bedrooms')),
                bathrooms=safe_int(request.form.get('realtor_bathrooms')),
                kitchens=safe_int(request.form.get('realtor_kitchens'), 1),
                living_rooms=safe_int(request.form.get('realtor_living_rooms'), 1),
                dining_rooms=safe_int(request.form.get('realtor_dining_rooms'), 1),
                hallways=safe_int(request.form.get('realtor_hallways'), 1),
                service_type=request.form.get('service_type', 'listing_prep'),
                rush_type=request.form.get('rush_type', 'none'),
                condition=request.form.get('realtor_condition', 'normal'),
                window_count=safe_int(request.form.get('realtor_window_count')),
                oven=('realtor_oven' in request.form),
                fridge=('realtor_fridge' in request.form),
                carpet_sqft=safe_float(request.form.get('realtor_carpet_sqft')),
                pressure_sqft=safe_float(request.form.get('realtor_pressure_sqft')),
                bins=safe_int(request.form.get('realtor_bins')),
                floor_care_sqft=safe_float(request.form.get('realtor_floor_care_sqft')),
                floor_care_condition=request.form.get('realtor_floor_care_condition', 'standard'),
                pressure_condition=request.form.get('realtor_pressure_condition', 'standard'),
                pressure_stain_addon=request.form.get('realtor_pressure_stain_addon', 'none'),
            )
        elif form_type == 'commercial':
            commercial_result = calculate_commercial(
                square_feet=safe_int(request.form.get('commercial_square_feet')),
                service_type=request.form.get('commercial_service_type', 'janitorial'),
                recurring=request.form.get('commercial_recurring', 'none'),
                carpet_sqft=safe_float(request.form.get('commercial_carpet_sqft')),
                floor_care_sqft=safe_float(request.form.get('commercial_floor_care_sqft')),
                floor_care_condition=request.form.get('commercial_floor_care_condition', 'standard'),
            )

    pricing_snapshot = {
        'rate_per_hour': RESIDENTIAL_RATE_PER_HOUR,
        'commercial_janitorial_rate_per_hour': COMMERCIAL_JANITORIAL_RATE_PER_HOUR,
        'minimum_service_price': MINIMUM_SERVICE_PRICE,
        'weekly_discount': int(RECURRING_DISCOUNTS['weekly'] * 100),
        'biweekly_discount': int(RECURRING_DISCOUNTS['biweekly'] * 100),
        'monthly_discount': int(RECURRING_DISCOUNTS['monthly'] * 100),
        'couch_cleaning_price': COUCH_CLEANING_PRICE,
    }

    return render_template(
        'index.html',
        active_tab=active_tab,
        residential_result=residential_result,
        realtor_result=realtor_result,
        commercial_result=commercial_result,
        pricing_snapshot=pricing_snapshot,
        residential_service_details=RESIDENTIAL_SERVICE_DETAILS,
        realtor_service_details=REALTOR_SERVICE_DETAILS,
        commercial_service_details=COMMERCIAL_SERVICE_DETAILS,
    )


if __name__ == '__main__':
    app.run(debug=True)
