from MembershipFunction import MembershipFunction


class LinguisticVariable(object):
    def __init__(self, name):
        self.name = name
        self.membership_functions = {}

    def add(self, name, start, left_top, right_top, finish):
        """
        Add a membership function to this linguistic variable,
        by its name and the corners of the trapezoid
        """
        range_in = [start, left_top, right_top, finish]
        membership_function = MembershipFunction(name, range_in)
        self.membership_functions[name] = membership_function

    def get_membership_function(self, name):
        return self.membership_functions[name]

    def defuziffy(self, value, mf_name):
        return self.membership_functions[mf_name].fuzzify(value)
