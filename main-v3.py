# Zach Cartnick
# July 2024 - Version 3.0
# Lacey Township EMS

import random

# setup array for schedule and initialize other variables
sche = [["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""]]

employees = ['SM', 'JB', 'ZC', 'BS', 'MD', 'ML', 'JC']

# create all possible two-member crew combinations
crew_combos = []
for i in range(len(employees)):
    for j in range(len(employees))[i + 1:]:
        crew_combos += [employees[i] + "/" + employees[j]]

# create all possible three-member crew combinations
crew_choose_three = []

# create all possible four-member crew combinations
crew_choose_four = []

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

# default set each employee days off to two random days - manually adjust below
days_off = {}
for name in employees:
    day = random.randint(0, 5)
    days_off[name] = [day, day + 1]
days_off["SM"] = [3, 6]

def main():
    best_sche = []
    best_score = 10000
    tries = 100
    sche_attempts = 0
    while sche_attempts < tries:
        print("-------------------------------")
        current_score = least_conflicts(15)
        if current_score < best_score:
            best_sche = sche.copy()
            best_score = current_score
        count_conflicts(sche)
        make_shift_dict()
        view(sche)
        sche_attempts += 1
        print(str(sche_attempts) + " of " + str(tries) + " iterations complete. Current/Best Score: "
              + str(current_score) + "/" + str(best_score))
    print("********************BEST FOUND********************")
    view(best_sche)
    print("Score:", best_score)
    return best_score, best_sche


# boolean function for iterating through and looking for conflicts
def least_conflicts(repeat):
    # set up a loop that will check all shifts randomly
    reset_sche()
    test_sche = sche.copy()
    shift_options_copy = all_shifts.copy()
    shifts_assessed = 0
    while shifts_assessed < (len(all_shifts) * repeat):
        shift_coords = shift_options_copy[random.randint(0, len(shift_options_copy) - 1)]
        shift = shift_coords[0]
        day = shift_coords[1]
        best_crew = []
        if count_conflicts(test_sche) > 0 or test_sche[shift][day] == "":
            crews_assessed = 0
            crew_list_copy = crew_combos.copy()
            best_score = 10000
            while crews_assessed < len(crew_combos):
                test_crew = crew_list_copy[random.randint(0, len(crew_list_copy)-1)]
                test_sche[shift][day] = test_crew
                test_score = count_conflicts(test_sche)
                print(shifts_assessed, crews_assessed, test_score, best_score)
                if test_score < best_score:
                    best_crew = test_crew
                    best_score = test_score
                # now that crew was assessed, remove it from the list
                crew_list_copy.remove(test_crew)
                crews_assessed += 1
        sche[shift][day] = best_crew
        # remove shift now that it has been assessed, reset list if now empty
        shift_options_copy.remove(shift_coords)
        if len(shift_options_copy) == 0:
            shift_options_copy = all_shifts.copy()

        shifts_assessed += 1
    return best_score


# function for counting conflicts
def count_conflicts(check_sche):
    count = 0
    shift_dict = make_shift_dict()

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
        count += abs(temp_hour_count[person] - total_hours[person])

    # conflict if improper shift length (i.e cannot be longer than 18)
    for person in shift_dict:
        if person in shift_dict.keys():
            # initialize variables
            person_shifts = shift_dict[person]
            consec_shifts = []  # list of number of consecutive shifts
            consec_breaks = []  # list of number of consecutive breaks
            consec_on = 0  # temporary consecutive shift counter - resets to 0 at first break
            consec_off = 0  # temporary consecutive break counter - resets to 0 at first shift

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
            elif item == 3:
                count += 50
        for item in consec_breaks:
            if item < 2:
                count += 100

    # conflict if on the overnight and morning after
    for day in range(len(check_sche[0])):
        if check_sche[0][day] != "":
            overnight_crew = check_sche[0][day].split("/")
            for member in overnight_crew:
                if member in check_sche[1][day].split("/"):
                    count += 100

    # conflict if working on day off or time off
    for person in shift_dict:
        if person in shift_dict.keys():
            # initialize variables
            person_shifts = shift_dict[person]
            for shift in person_shifts:
                if shift[1] in days_off[person]:
                    count += 100

    # conflict if empty
    for shift in sche:
        for day in shift:
            if day == "":
                count += 100
    return count

# function for drawing results
def view(check_sche):
    for row in check_sche:
        print(row)

def make_shift_dict():
    shift_dict = {}
    for name in employees:
        shift_dict[name] = []

    for shift in chron_shifts:
        for name in sche[shift[0]][shift[1]].split("/"):
            if name in shift_dict.keys():
                shift_dict[name] += [shift]

    return shift_dict

def reset_sche():
    for shift in all_shifts:
        sche[shift[0]][shift[1]] = ""

main()