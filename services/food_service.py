def remove_food(food_to_remove, food_list):
    for food in food_to_remove:
        if food in food_list:
            food_list.remove(food)

