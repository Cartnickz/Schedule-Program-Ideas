#  Zach Cartnick

import numpy as np

sche = [["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""]]

max_hours = 42
employees = ['SM', 'JB', 'ZC', 'BS', 'MD', 'ML', 'JC']
total_hours = {}

#  begin filling shifts in chronological order
for day in range(7):
    for shift in range(4):

        # we want to base the first overnight off the last evening shift; skip it for now
        if day == 0 and shift == 0:
            continue

        # pick first crew
        elif day == 0 and shift == 1:
            person_1 = employees[np.random.randint(len(employees))]
            person_2 = employees[np.random.randint(len(employees))]
            while person_1 == person_2:
                person_2 = employees[np.random.randint(len(employees))]

            sche[1][0] = person_1 + "/" + person_2

        # create crews for the rest of the schedule
        else:
            person_1 = employees[np.random.randint(len(employees))]
            person_2 = employees[np.random.randint(len(employees))]
            while person_1 == person_2:
                person_2 = employees[np.random.randint(len(employees))]

            sche[shift][day] = person_1 + "/" + person_2

        # manage

for row in sche:
    print(row)