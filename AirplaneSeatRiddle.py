import random

## Riddle
# 100 passengers get onto a plane with 100 seats:
#  The first passenger takes a random seat
#  Each passenger after that takes their assigned seat
#   (Unless that seat is taken, where they take a random empty seat)
# What is the probability that the last passenger gets their assigned seat?

## Answer
# 50:50 since whenever someone is taking a random open seat,
# there is an equal chance they take seat 1 or 100 which determines the outcome

class Passenger:
    def __init__(self, seat):
        self.assigned = seat

    def take_seat(self, seat):
        self.actual = seat

def run():
    seats = [x for x in range(1, 101)]
    passengers = [Passenger(seat) for seat in seats]

    def sit_in(passenger, seat):
        seats.remove(seat)
        passenger.take_seat(seat)

    # first passenger takes random seat
    sit_in(passengers[0], random.choice(seats))

    # rest follow rules
    for passenger in passengers[1:]:
        seat = passenger.assigned # take assigned seat
        if seat not in seats:     # or random if that was taken
            seat = random.choice(seats) 
        sit_in(passenger, seat)

    # last passenger in correct seat?
    return passengers[-1].assigned == passengers[-1].actual

def run_n_times(n):
    trues = 0
    for i in range(n):
        if run():
            trues += 1
    return trues / n

print(run_n_times(1000))