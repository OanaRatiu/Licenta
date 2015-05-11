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

        self.rules.append(r)
