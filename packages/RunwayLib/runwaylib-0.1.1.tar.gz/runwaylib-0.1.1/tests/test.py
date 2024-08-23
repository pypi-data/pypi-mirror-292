import runway

print(runway.takeoff())  # Output: The plane is taking off!
print(runway.land())     # Output: The plane has landed safely.

plane = runway.Airplane("Boeing 747")
print(plane.fly())       # Output: The Boeing 747 is flying.
