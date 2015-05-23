class MembershipFunction(object):
    """
    Trapezoidal MF
    """
    def __init__(self, name, range_in):
        """
        Input: name_in - string, range - the 4 points of the trapezoid
        """
        self.name = name
        self.range = range_in

    def fuzzify(self, X):
        """
        Input: X - the variable that needs fuzzification
        """
        # Check if input value is in range, if not, return 0
        if X < self.range[0] or X > self.range[3]:
            return 0

        # Determine which of 3 /-\ slopes works.
        # Middle part, return 1
        if X >= self.range[1] and X <= self.range[2]:
            return 1

        # Increasing slope
        if X >= self.range[0] and X < self.range[1]:
            return (X - self.range[0])/(self.range[1] - self.range[0])

        # Decreasing slope
        if X > self.range[2] and X <= self.range[3]:
            return (self.range[3] - X)/(self.range[3] - self.range[2])

        return 0

    def get_ascending_slope(self):
        a = float(1/(self.range[1] - self.range[0]))
        b = float(-self.range[0]/(self.range[1] - self.range[0]))
        return [a, b]

    def get_descending_slope(self):
        a = float(-1/(self.range[3] - self.range[2]))
        b = float(self.range[3]/(self.range[3] - self.range[2]))
        return [a, b]

    def get_0_slope(self):
        return [0, 0]

    def get_1_slope(self):
        return [0, 1]
