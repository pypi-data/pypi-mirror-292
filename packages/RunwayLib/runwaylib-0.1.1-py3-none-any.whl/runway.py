# runway.py

def Run(Test):
    return(f"said {Test}")
def takeoff():
    return "The plane is taking off!"

def land():
    return "The plane has landed safely."

class Airplane:
    def __init__(self, model):
        self.model = model

    def fly(self):
        return f"The {self.model} is flying."

if __name__ == "__main__":
    print(takeoff())
    print(land())
    plane = Airplane("Boeing 747")
    print(plane.fly())
