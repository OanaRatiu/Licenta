class FuzzyEngine(object):
    """
    Evaluate rules given by string variables
    """
    def __init__(self):
        self.rule_fired = None
        self.lv_hash = {}
        self.label_weight_hash = {}
        self.control_hash = {
            'if': 1,
            'then': 2,
            'is': 3,
            'and': 5,
            'or': 6,
            ' ': 9,
            'rule': 12,
            'weight': 15,
            'set': 4
        }

    def register(self, function):
        """
        function - Linguistic Variable
        """
        self.lv_hash[function.name] = function
        function.add_label_weight_hash(self.label_weight_hash)

    def evaluate_rule(rule):
        """
        Parse and evaluate a fuzzy rule
        """
        self.rule_fired = False;
