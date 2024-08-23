# runwaylib/config.py

class Configuration:
    def __init__(self):
        self.setting = "default"

    def update_setting(self, value):
        self.setting = value
        print(f"Setting updated to {value}")
