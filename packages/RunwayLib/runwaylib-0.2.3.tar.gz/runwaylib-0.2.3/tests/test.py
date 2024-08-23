import runwaylib.server as server

print(server.takeoff())  # Output: The plane is taking off!
print(server.land())     # Output: The plane has landed safely.

plane = server.Airplane("Boeing 747")
print(plane.fly())       # Output: The Boeing 747 is flying.
