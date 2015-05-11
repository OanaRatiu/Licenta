class MembershipFunction(object):
    """
    Trapezoidal MF
    """
    def __init__(self, name_in, range_in):
        """
        Input: name_in - string, range_in - the 4 points of the trapezoid
        """
        self.name_in = name_in
        self.range_in = range_in

    def fuzzify(self, X):
        """
        Input: X - the variable that needs fuzzification
        """
        # Check if input value is in range, if not, return 0
        if X < self.range_in[0] or X > self.range_in[3]:
            return 0

        # Determine which of 3 /-\ slopes works.
        # Middle part, return 1
        if X >= self.range_in[1] and X <= self.range_in[2]:
            return 1

        # Increasing slope
        if X >= self.range_in[0] and X < self.range_in[1]:
            return (X - self.range_in[0])/(self.range_in[1] - self.range_in[0])

        # Decreasing slope
        if X > self.range_in[2] and X <= self.range_in[3]:
            return (self.range_in[3] - X)/(self.range_in[3] - self.range_in[2])

        return 0

    def plot(self, left_x_axis, right_x_axis, size):
        """
        Return an array with discrete representation of the membership function
        Input: left_x_axis, right_x_axis - where the trapezoid will start
               size - number of discrete steps
        """
        increment = abs((left_x_axis - right_x_axis)/size)
        return [self.fuzzify(right_x_axis + increment * i)
                for i in range(size)]
