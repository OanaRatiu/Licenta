from FuzzyEngine import FuzzyEngine
from LinguisticVariable import LinguisticVariable


class SicknessManager(object):
    def compute_sickness(self, tremble_value, distance_value):
        # define tremble
        tremble = LinguisticVariable('tremble')
        tremble.add('low', 0, 0, 2, 3)
        tremble.add('moderate', 2, 3, 7, 8)
        tremble.add('high', 7, 8, 10, 10)

        # define distance between fingers
        # distance = the variation between fingers distance
        distance = LinguisticVariable('distance')
        distance.add('small', 0, 0, 3, 4)
        distance.add('medium', 3, 5, 7, 9)
        distance.add('high', 8, 9, 10, 10)

        # define sickness
        sickness = LinguisticVariable('sickness')
        sickness.add('low', 0, 0, 4, 5)
        sickness.add('medium', 3, 5, 6, 7)
        sickness.add('high', 6, 7, 10, 10)

        f = FuzzyEngine()

        # register the linguistic variables
        f.register(tremble)
        f.register(distance)
        f.register(sickness)

        rules = [
            'if tremble is low and distance is small then sickness is low',
            'if tremble is low and distance is medium then sickness is low',
            'if tremble is low and distance is high then sickness is medium',

            'if tremble is moderate and distance is medium then sickness is medium',
            'if tremble is moderate and distance is high then sickness is high',
            'if tremble is moderate and distance is small then sickness is medium',

            'if tremble is high and distance is small then sickness is high',
            'if tremble is high and distance is medium then sickness is high',
            'if tremble is high and distance is high then sickness is high'
        ]

        # define the rules
        for rule in rules:
            f.evaluate_rule(rule)


        print "tremble", tremble_value
        print "distance", distance_value

        return f.defuzzify(tremble_value, distance_value)
