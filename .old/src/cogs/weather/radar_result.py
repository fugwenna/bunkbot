"""
Maintainable wrapper class
with dynamic properties that will parse
radar results for the weather cog
"""

class RadarResult:
    def __init__(self, location: any):
        self.id = ""
        self.location = location["results"]["locations"]["location"]

        if self.location_found:
            self.id = self.location[0]["id"]


    """
    No locations found from the radar result
    """
    @property
    def location_found(self):
        return len(self.location) > 0