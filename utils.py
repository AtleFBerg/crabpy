def calculate_average_preferences(crabs):
    from collections import defaultdict

    totals = defaultdict(float)
    counts = defaultdict(int)

    for crab in crabs:
        for food_type, score in crab.preferred_foods.items():
            totals[food_type] += score
            counts[food_type] += 1

    averages = {}
    for food_type in totals:
        averages[food_type] = totals[food_type] / counts[food_type]

    return averages