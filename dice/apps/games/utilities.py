import random


def roll_dices():
    dices = []
    for i in range(5):
        dices.append(random.randint(1, 6))
    return dices


"""
def calculate_points(dices, selected_field):
    if selected_field == 0:
        return dices.count(1) * 1
    elif selected_field == 1:
        return dices.count(2) * 2
    elif selected_field == 2:
        return dices.count(3) * 3
    elif selected_field == 3:
        return dices.count(4) * 4
    elif selected_field == 4:
        return dices.count(5) * 5
    elif selected_field == 5:
        return dices.count(6) * 6
    elif selected_field == 6:
        for i in range(1, 7):
            if dices.count(i) >= 3:
                return sum(dices)
    elif selected_field == 7:
        for i in range(1, 7):
            if dices.count(i) >= 4:
                return sum(dices)
    elif selected_field == 8: # 2 + 3
    elif selected_field == 9:  # mały strit
    elif selected_field == 10:  # duży strit
    elif selected_field == 11:  # generał

    elif selected_field == 12:
        return sum(dices)
        
"""