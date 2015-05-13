import re
from FuzzyRule import FuzzyRule


class FuzzyEngine(object):
    """
    Evaluate rules given by string variables
    """
    def __init__(self):
        self.linguistic_variables = {}
        self.rules = []

    def register(self, linguistic_var):
        """
        function - Linguistic Variable
        """
        self.linguistic_variables[linguistic_var.name] = linguistic_var

    def evaluate_rule(self, rule):
        """
        Parse and evaluate a fuzzy rule.
        A rule must always be of form:
            if a is A then b is B
            if a is A and/or b is B then c in C
        """
        rule = re.match(
            (r'if (?P<value_1>\w+) is (?P<fuzzy_set_1>\w+) '
             '((?P<connective>\w+) (?P<value_2>\w+) is (?P<fuzzy_set_2>\w+)).*'
             'then (?P<value>\w+) is (?P<fuzzy_set>\w+)'),
            rule)
        rule = rule.groupdict()

        r = FuzzyRule()
        lv = self.linguistic_variables[rule['value_1']]
        r.add_premise(lv.name,
                      lv.get_membership_function(rule['fuzzy_set_1']).name)

        lv = self.linguistic_variables[rule['value_2']]
        r.add_premise(lv.name,
                      lv.get_membership_function(rule['fuzzy_set_2']).name)

        lv = self.linguistic_variables[rule['value']]
        r.add_result(lv.name,
                     lv.get_membership_function(rule['fuzzy_set']).name)

        r.add_connective(rule['connective'])

        self.rules.append(r)

    def defuzzify(self, tremble, distance):
        """
        Given tremble and distance as crisp inputs, compute how much the
        mf for sickness
        """
        # compute mfs for the crisp inputs
        tremble_lv = self.linguistic_variables['tremble']
        tremble_mfs = {}
        for name, mf in tremble_lv.membership_functions.items():
            mf_value = mf.fuzzify(tremble)
            if mf_value != 0:
                tremble_mfs[name] = mf_value

        distance_lv = self.linguistic_variables['distance']
        distance_mfs = {}
        for name, mf in distance_lv.membership_functions.items():
            mf_value = mf.fuzzify(distance)
            if mf_value != 0:
                distance_mfs[name] = mf_value

        # if mf values are different form 0, then we search for rules that
        # have the lv and mf names in them
        sickness_mfs = []
        for tremble_name, tremble_mf in tremble_mfs.items():
            for distance_name, distance_mf in distance_mfs.items():
                rule = self.get_rule(tremble_name, distance_name)
                if rule:
                    print rule.premises, rule.result
                    if rule.connective == 'and':
                        min_mf = min(tremble_mf, distance_mf)
                    else:
                        min_mf = max(tremble_mf, distance_mf)
                    sickenss_mf_name = rule.result['sickness']
                    sickness_mfs.append({sickenss_mf_name: min_mf})

        # we apply centroid method on all sickness mf that are in sickness_mfs
        print sickness_mfs

    def get_rule(self, tremble_name, distance_name):
        """
        Search the rule that has tremble tremble_name
        and distance distance_name
        """
        for rule in self.rules:
            if (rule.verify_rule('tremble', tremble_name) and
                    rule.verify_rule('distance', distance_name)):
                return rule
        return False

    def max_mf(self, value):
        """
        Compute the values of each mf of the linguistic variable sickness
        and return the MAX value
        """
        sickness_lv = self.linguistic_variables['sickness']
        max_mf = {}
        for mf_name, mf in sickness_lv.membership_functions.items():
            fuzzy_value = mf.fuzzify(value)
            if not max_mf:
                max_mf = {mf_name: fuzzy_value}
            elif max_mf.values()[0] < fuzzy_value:
                max_mf = {mf_name: fuzzy_value}
        return max_mf
