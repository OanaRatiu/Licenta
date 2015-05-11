class FuzzyRule(object):
    """
    A rule is given by its premise and result
    """
    def __init__(self):
        """
        premises is a list of dictionaries that look like:
        [{name_of_lv: name_of_mf}]
        """
        self.premises = []
        self.result = {}

    def add_premise(self, lv_name, mf_name):
        self.premises.append({lv_name: mf_name})

    def add_result(self, lv_name, mf_name):
        self.result[lv_name] = mf_name
