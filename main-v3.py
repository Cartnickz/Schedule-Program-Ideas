# Zach Cartnick
# July 2024 - Version 3.0
# Lacey Township EMS

import random
import copy
import math
from itertools import combinations

# setup array for schedule and initialize other variables
sche = [["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""]]

employees = ['SM', 'JB', 'ZC', 'BS', 'MD', 'ML', 'JC', 'JP', 'KT']
supervisors = ['SM', 'JB']

# create all possible two/three/four-member crew combinations
crew_combos = []
for i in range(len(employees)):
    for j in range(len(employees))[i + 1:]:
        crew_combos += [employees[i] + "/" + employees[j]]
crew_choose_three = list(combinations(employees, 3))
crew_choose_four = list(combinations(employees, 4))
expanded_crew_combos = crew_combos.copy()
for element in crew_choose_three + crew_choose_four:
    if len(element) == 3:
        expanded_crew_combos += [element[0] + "/" + element[1] + "/" + element[2]]
    elif len(element) == 4:
        expanded_crew_combos += [element[0] + "/" + element[1] + "/" + element[2] + "/" + element[3]]

# create coordinates to navigate each shift on the schedule
all_shifts = []
for i in range(len(sche)):
    for j in range(len(sche[0])):
        all_shifts += [(i, j)]
# create coordinates to navigate shifts in chronological order
chron_shifts = []
for day in range(len(sche[0])):
    for shift in range(len(sche)):
        chron_shifts += [(shift, day)]

# default set hours to 42; adjust specific employees below
total_hours = {}
for name in employees:
    total_hours[name] = 42
total_hours['SM'] = 60
total_hours['JB'] = 60
total_hours['MD'] = 48
total_hours['BS'] = 48
total_hours['JP'] = 24

all_assigned_hours = 0
for name in total_hours:
    all_assigned_hours += total_hours[name]

print("All assigned hours:", all_assigned_hours, "Available hours:", "336-420 hours")


# default set each employee days off to two random days - manually adjust below
days_off = {}

def generate_days_off():
    day_range = [0, 1, 2, 3, 4, 5]
    for person in employees:
        day_off = day_range[random.randint(0, len(day_range)-1)]
        days_off[person] = [day_off, day_off + 1]
        day_range.remove(day_off)
        if len(day_range) == 0:
            day_range = [0, 1, 2, 3, 4, 5]
    days_off["SM"] = [3, 6]


def main():
    best_sche = []
    best_score = 10000
    best_days_off = {}
    tries = 200
    sche_attempts = 0
    print(count_conflicts(sche)[0])
    while sche_attempts < tries:
        if sche_attempts % 5 == 0:
            generate_days_off()
        print("-------------------------------")
        # print(days_off)
        current_score, current_report = least_conflicts(10)
        if current_score < best_score:
            best_sche = copy.deepcopy(sche)
            best_score = current_score
            best_report = current_report
            best_days_off = days_off
        make_shift_dict(sche)
        view(sche)
        sche_attempts += 1
        print(str(sche_attempts) + " of " + str(tries) + " iterations complete. Current/Best Score: "
              + str(current_score) + "/" + str(best_score))
    print("********************BEST FOUND********************")
    print(best_days_off)
    view(best_sche)
    print("Score:", best_score, best_report)
    return best_score, best_sche


# boolean function for iterating through and looking for conflicts
def least_conflicts(repeat):
    # set up a loop that will check all shifts randomly
    reset_sche()
    test_sche = copy.deepcopy(sche)
    shift_options_copy = all_shifts.copy()
    shifts_assessed = 0
    while shifts_assessed < (len(all_shifts) * repeat):
        temp = 500 * 0.99 ** shifts_assessed
        shift_coords = shift_options_copy[random.randint(0, len(shift_options_copy) - 1)]
        x = shift_coords[0]
        y = shift_coords[1]
        best_crew = ''
        best_crew_score = 10000
        # print(best_crew_score, best_crew_report)
        crew_list_copy = []
        if x == 2:
            crew_list_copy = expanded_crew_combos.copy()
        else:
            crew_list_copy = crew_combos.copy()
        if best_crew_score > 0 or test_sche[x][y] == "":
            crews_remaining = True
            while crews_remaining:
                test_crew = crew_list_copy[random.randint(0, len(crew_list_copy)-1)]
                test_sche[x][y] = test_crew
                test_score, test_report = count_conflicts(test_sche)
                if test_score <= best_crew_score:
                    best_crew = test_crew
                    best_crew_score = test_score
                # now that crew was assessed, remove it from the list
                crew_list_copy.remove(test_crew)
                crews_remaining = len(crew_list_copy) != 0
        energy = best_crew_score - count_conflicts(sche)[0]
        if energy == 0:
            probabilty = .05
        else:
            probabilty = math.e**(-energy/temp)
        random_num = random.random()
        if (random_num < probabilty) or sche[x][y] == "":
            sche[x][y] = best_crew
            test_sche = copy.deepcopy(sche)
        else:
            test_sche = copy.deepcopy(sche)
        # remove shift now that it has been assessed, reset list if now empty
        shift_options_copy.remove(shift_coords)
        if len(shift_options_copy) == 0:
            shift_options_copy = all_shifts.copy()

        shifts_assessed += 1
    return count_conflicts(sche)


# function for counting conflicts
def count_conflicts(check_sche):
    count_log = []
    count = 0
    shift_dict = make_shift_dict(check_sche)

    temp_hour_count = {}
    for person in employees:
        temp_hour_count[person] = 0

    # conflict if crew under/over hours
    for shift in all_shifts:
        crew = check_sche[shift[0]][shift[1]].strip().split("/")
        for person in crew:
            if person in temp_hour_count.keys():
                temp_hour_count[person] += 6
    for person in temp_hour_count:
        count += abs(temp_hour_count[person] - total_hours[person]) * 5
        count_log += [(person, "hours", abs(temp_hour_count[person] - total_hours[person]))]

    # conflict if improper shift lengths (i.e cannot be longer than 18)
    for person in shift_dict:
        consec_shifts = []  # list of number of consecutive shifts
        consec_breaks = []  # list of number of consecutive breaks
        consec_on = 0  # temporary consecutive shift counter - resets to 0 at first break
        consec_off = 0  # temporary consecutive break counter - resets to 0 at first shift
        if person in shift_dict.keys():
            # initialize variables
            person_shifts = shift_dict[person]
            # penalize if more than 2 shifts in a day
            shifts_per_day = [0] * 7
            for item in person_shifts:
                shifts_per_day[item[1]] += 1
            for shift_count in shifts_per_day:
                if shift_count > 2:
                    count += 100
                    count_log += [(person, "shifts per day")]
            # iterate through each shift in chronological order for each person - track back-to-back shifts and breaks
            for shift in chron_shifts:
                if shift in person_shifts:
                    consec_on += 1
                    if consec_off != 0:
                        consec_breaks += [consec_off]
                    consec_off = 0
                else:
                    if shift == (0, 0):
                        continue
                    consec_off += 1
                    if consec_on != 0:
                        consec_shifts += [consec_on]
                    consec_on = 0
        # apply conflict score for 24 hours shifts and less than 12 hour break
        for item in consec_shifts:
            if item > 3:
                count += 100
                count_log += [(person, "24s")]
            elif item == 3:
                count += 50
                count_log += [(person, "18s")]
            elif item == 1:
                count += 15
                count_log += [(person, "6s")]
        for item in consec_breaks:
            if item < 2:
                count += 100
                count_log += [(person, "6 hour break")]

    # conflict if on the overnight and morning after
    for day in range(len(check_sche[0])):
        if check_sche[0][day] != "":
            overnight_crew = check_sche[0][day].split("/")
            for member in overnight_crew:
                if member in check_sche[1][day].split("/"):
                    count += 120
                    count_log += [(overnight_crew, "overnight_morn")]

    # conflict if working on day off or time off
    for person in shift_dict:
        if person in shift_dict.keys():
            # initialize variables
            person_shifts = shift_dict[person]
            for shift in person_shifts:
                if shift[1] in days_off[person]:
                    count += 100
                    count_log += [(person, "day off", shift[1])]

    # prioritize supervisors on day shifts
    day_shifts = sche[1] + sche[2]
    for shift in day_shifts:
        shift_split = shift.split("/")
        if not(supervisors[0] in shift_split or supervisors[1] in shift_split):
            count += 20
            count_log += ["supervisor"]

    # no too many overnights
    person_overnight = {}
    for person in shift_dict:
        if person not in person_overnight.keys():
            person_overnight[person] = 0
        for shift in shift_dict[person]:
            if shift[0] == 0:
                person_overnight[person] += 1
    for person in person_overnight:
        if person_overnight[person] > 2:
            count += 50
            count_log += [(person, "overnight", person_overnight[person])]

    # conflict if empty
    for shift in check_sche:
        for day in shift:
            if day == "":
                count += 200
                count_log += ["empty"]
    return count, count_log


# function for drawing results
def view(check_sche):
    for row in check_sche:
        print(row)


def make_shift_dict(check_sche):
    shift_dict = {}
    for person in employees:
        shift_dict[person] = []
    for on_shift in chron_shifts:
        for person in check_sche[on_shift[0]][on_shift[1]].split("/"):
            if person in shift_dict.keys():
                shift_dict[person] += [on_shift]
    return shift_dict


def reset_sche():
    for on_shift in all_shifts:
        sche[on_shift[0]][on_shift[1]] = ""


main()

