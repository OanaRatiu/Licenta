from MembershipFunction import MembershipFunction
from NoRulesFiredException import NoRulesFiredException


class LinguisticVariable(object):
    def __init__(self, name):
        self.name = name
        self.storage = {}
        self.for_defuzzification = []

    def add_mf(self, membership_function):
        """
        Add a membership function to this linguistic variable
        """
        range_in = membership_function.range_in
        self.storage[membership_function.name] = membership_function
        if range_in[0] < self.minSupport:
            self.minSupport = range_in[0]
        if range_in[3] > self.maxSupport:
            self.maxSupport = range_in[3]

    def add(self, name, start, left_top, right_top, finish):
        """
        Add a membership function to this linguistic variable,
        by its name and the corners of the trapezoid
        """
        range_in = [start, left_top, right_top, finish]
        membership_function = MembershipFunction(name, range_in)
        self.storage[name] = membership_function
        if start < self.minSupport:
            self.minSupport = self.minSupport
        if finish > self.maxSupport:
            self.maxSupport = finish

    def add_label_weight_hash(self, label_hash):
        """
        Explicitly set this value
        """
        self.label_weight_hash = label_hash

    def defuziffy(self):
        """
        Defuzzify using Centroid method
        """
        fired = len(self.for_defuzzification)
        if fired == 0:
            return "No rules were fired for %s" % self.name
        step = abs((self.maxSupport - self.minSupport)/100)
        sum_of_scaled_mf = []
        for i in range(0, fired - 1, 3):
            membership_function = self.storage[self.for_defuzzification.index(i+1)]
            scaled = membership_function.plot(self.minSupport, self.maxSupport, 100);

            scale = self.for_defuzzification.index(i+2)
            weight = 1.0

            label = self.for_defuzzification.index(i)
            if label:
                temp = self.label_weight_hash.get(label)
                try:
                    if temp:
                        weight = temp.defuziffy()
                except NoRulesFiredException:
                    weight = 1.0

            for j in range(100):
                sum_of_scaled_mf[j] += scaled[j] * scale * weight

        nominator, denominator = 0.0, 0.0
        for i in range(100):
            nominator += (self.minSupport + step * i) * sum_of_scaled_mf[i]
            denominator += sum_of_scaled_mf[i]

        return nominator/denominator
