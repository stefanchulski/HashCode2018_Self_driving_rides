import time
import os
import numpy as np


def parse_ride_data(raw_data, ride_idx):
    # ride_from(x,y), ride_to(x,y), start_time, finish
    ride_data = {"ride_from": None, "ride_to": None, "start_time": 0, "finish_time": 0, "ride_idx": ride_idx,
                 "relevant": True}

    data_split = raw_data.split()

    ride_data["ride_from"] = (int(data_split[0]), int(data_split[1]))
    ride_data["ride_to"] = (int(data_split[2]), int(data_split[3]))
    ride_data["start_time"] = int(data_split[4])
    ride_data["finish_time"] = int(data_split[5])

    return ride_data


def parse_city_data(raw_data):
    # rows, columns, vehicles, rides, bonus, steps
    city_data = {"rows": 0, "columns": 0, "vehicles": 0, "rides": 0, "bonus": 0, "steps": 0}

    data_split = raw_data.split()

    city_data["rows"] = int(data_split[0])
    city_data["columns"] = int(data_split[1])
    city_data["vehicles"] = int(data_split[2])
    city_data["rides"] = int(data_split[3])
    city_data["bonus"] = int(data_split[4])
    city_data["steps"] = int(data_split[5])

    return city_data


def get_best_rides(rides, city_data, cost_to_next):
    vehicles = [{"curr_pos": [0,0], "av_time": 0, "rides": []} for i in range(city_data["vehicles"])]

    vehicle_ind = 0
    # for vehicle in vehicles:
    for time in xrange(city_data["steps"]):
        # print vehicle_ind
        # vehicle_ind += 1
        # for ride_idx, ride in enumerate(rides):
        #     ride["relevant"] = True

        print time

        # for time in xrange(city_data["steps"]):
        for vehicle in vehicles:
            best_ride = None
            best_score = 0
            best_ride_time = 0
            best_ride_price = 0

            if time < vehicle["av_time"]:
                continue

            for ride_idx, ride in enumerate(rides):
                if not ride["relevant"]:
                    continue

                if rides[ride_idx]["finish_time"] < (time + cal_distance(rides[ride_idx]["ride_to"], rides[ride_idx]["ride_from"])):
                    # print "time: {}, ride: {} not relevant".format(time, rides[ride_idx])
                    ride["relevant"] = False
                    continue

                ride_time = max(rides[ride_idx]["start_time"] - time, cal_distance(vehicle["curr_pos"], rides[ride_idx]["ride_from"]))

                # if vehicle_ind > 50:
                #     print ride_idx, time
                #     print ride
                #     print "start: ", rides[ride_idx]["start_time"] - time
                #
                #     print "ride time: ", ride_time, " dist: ", cal_distance(rides[ride_idx]["ride_from"], rides[ride_idx]["ride_to"])

                if ride_time + cal_distance(rides[ride_idx]["ride_from"], rides[ride_idx]["ride_to"]) + time > ride["finish_time"]:
                    # ride["relevant"] = False
                    continue

                ride_time += cal_distance(rides[ride_idx]["ride_from"], rides[ride_idx]["ride_to"])

                # if vehicle_ind > 50:
                #     print ride_idx, time

                ride_price = 0
                if time + cal_distance(vehicle["curr_pos"], rides[ride_idx]["ride_from"]) <= rides[ride_idx]["start_time"]:
                    ride_price = city_data["bonus"]

                ride_price += cal_distance(rides[ride_idx]["ride_from"], rides[ride_idx]["ride_to"])

                if cal_distance(rides[ride_idx]["ride_from"], rides[ride_idx]["ride_to"]) > (float(city_data["steps"] - time) * 0.87):
                    ride_price = ride_price * 5

                if not best_ride:
                    best_ride = rides[ride_idx]

                    best_score = float(ride_price) / float(ride_time)
                    best_ride_time = ride_time
                    best_ride_price = ride_price

                else:
                    best_score_candidate = float(ride_price) / float(ride_time)
                    # if best_score < best_score_candidate:
                    if 1:
                        # if float(best_score) < best_score_candidate:
                        # if best_score * 1.1 + max(cost_to_next[best_ride["ride_idx"]]) < best_score_candidate * 1.1 + max(cost_to_next[rides[ride_idx]["ride_idx"]]):
                        #if best_score + max(cost_to_next[best_ride["ride_idx"]]) < best_score_candidate + max(cost_to_next[rides[ride_idx]["ride_idx"]]):
                        if best_score + max_next_ride[best_ride["ride_idx"]][0] < best_score_candidate + max_next_ride[rides[ride_idx]["ride_idx"]][0]:

                            best_ride = rides[ride_idx]
                            best_ride_time = ride_time
                            best_ride_price = ride_price
                            best_score = best_score_candidate

            if best_ride:
                vehicle["rides"].append(best_ride)
                best_ride["relevant"] = False
                rides.pop(rides.index(best_ride))
                vehicle["curr_pos"] = best_ride["ride_to"]

                for ride_idx_in in range(city_data["rides"]):
                    cost_to_next[ride_idx_in][best_ride["ride_idx"]] = 0

                for ride_idx_in in range(city_data["rides"]):
                    if int(max_next_ride[ride_idx_in][1]) == int(best_ride["ride_idx"]):
                        max_next_ride[ride_idx_in][0] = max(cost_to_next[ride_idx_in])

                vehicle["av_time"] = best_ride_time + time

                print "time: {}, ride:{}, av_time:{}, best_score:{}, best_ride_price:{}, best_ride_time;{}".format(time, best_ride, vehicle["av_time"], best_score, best_ride_price, best_ride_time)

            else:
                print "No rides for vehicle:{}".format(vehicle)
                vehicle["av_time"] = city_data["steps"]

    return vehicles


def cal_distance(distance1, distance2):
    return abs(distance1[0] - distance2[0]) + abs(distance1[1] - distance2[1])


def rides_next_cost_dn_table():

    for ride_idx_out in range(len(rides)):
        print 'ride_idx_out: ' + str(ride_idx_out)

        earliest2fininsh = rides[ride_idx_out]["start_time"] + cal_distance(rides[ride_idx_out]["ride_from"],
                                                                           rides[ride_idx_out]["ride_to"])
        for ride_idx_in in range(len(rides)):

            if ride_idx_out == ride_idx_in:
                cost_to_next[ride_idx_out][ride_idx_in] = 0
                # cost_to_next_with_bonus[ride_idx_in][ride_idx_out] = 0

            elif earliest2fininsh + cal_distance(rides[ride_idx_out]["ride_to"], rides[ride_idx_in]["ride_from"]) \
                    + cal_distance(rides[ride_idx_in]["ride_from"], rides[ride_idx_in]["ride_to"]) > rides[ride_idx_in]["finish_time"]:
                cost_to_next[ride_idx_out][ride_idx_in] = 0
                # cost_to_next_with_bonus[ride_idx_in][ride_idx_out] = 0

            else:
                ride_time = cal_distance(rides[ride_idx_in]["ride_from"], rides[ride_idx_in]["ride_to"])
                cost_to_next[ride_idx_out][ride_idx_in] = float(ride_time) / float((cal_distance(rides[ride_idx_out]["ride_to"], rides[ride_idx_in]["ride_from"])
                                                                                    + max(ride_time, rides[ride_idx_in]["start_time"] - earliest2fininsh)))
                # cost_to_next_with_bonus[ride_idx_in][ride_idx_out] = float(ride_time + city_data["bonus"]) / float((cal_distance(rides[ride_idx_in]["ride_to"], rides[ride_idx_out]["ride_from"])
                #                                                                                                     + max(ride_time, rides[ride_idx_out]["start_time"] - earliest2fininsh)))

        max_next_ride[ride_idx_out][0] = max(cost_to_next[ride_idx_out])
        max_next_ride[ride_idx_out][1] = np.argmax(cost_to_next[ride_idx_out])

        print max_next_ride[ride_idx_out][0] , max_next_ride[ride_idx_out][1]


if "__main__" == __name__:

    for file_name in os.listdir("./"):
        if file_name.endswith("d_metropolis.in"):
            input_data = open(file_name, "rb")

            output_file = open(file_name.split(".")[0] + ".out", "wb")

            city_data = parse_city_data(input_data.readline())

            cost_to_next = np.zeros((city_data["rides"], city_data["rides"]))
            # cost_to_next_with_bonus = np.zeros((city_data["rides"], city_data["rides"]))
            max_next_ride = np.zeros((city_data["rides"], 2))

            rides = []
            for idx, raw_ride_data in enumerate(input_data.readlines()):
                rides.append(parse_ride_data(raw_ride_data, idx))

            rides_next_cost_dn_table()

            print cost_to_next

            start_time = time.time()
            vehicles = get_best_rides(rides, city_data, cost_to_next)

            delta = time.time() - start_time
            print "time took: {}".format(delta)

            for vec_num, vehicle in enumerate(vehicles):
                output_file.write(str(len(vehicle["rides"])) + " ")

                for ride in vehicle["rides"]:
                    output_file.write(str(ride["ride_idx"]) + " ")

                output_file.write("\n")