import re
import itertools as IT
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
                    if rule.connective == 'and':
                        min_mf = min(tremble_mf, distance_mf)
                    else:
                        min_mf = max(tremble_mf, distance_mf)
                    sickenss_mf_name = rule.result['sickness']
                    sickness_mfs.append({sickenss_mf_name: min_mf})

        # we apply centroid method on all sickness mf that are in sickness_mfs
        return self.centroid_method(sickness_mfs)

    def get_rule(self, tremble_name, distance_name):
        """
        Search the rule that has tremble tremble_name
        and distance distance_name
        """
        for rule in self.rules:
            if (rule.verify_rule('tremble', tremble_name) and
                    rule.verify_rule('distance', distance_name)):
                return rule
        return None

    def centroid_method(self, mfs):
        """
        Apply centroid method on the mfs of sickness
        """
        sickness_lv = self.linguistic_variables['sickness']

        # if there is more than one mfs with the same name, choose the MAX
        mfs_values = []
        for mf in mfs:
            mf_2 = [m for m in mfs_values if m.keys()[0] == mf.keys()[0]]
            if mf_2:
                value_2 = mf_2[0][mf_2[0].keys()[0]]
                value = mf[mf.keys()[0]]
                if value_2 < value:
                    mf_2[0][mf_2[0].keys()[0]] = value
            else:
                mfs_values.append(mf)

        s = []
        # order the sickness mfs by the x coordinates
        sickness_mfs = self._order_by_first_point(
            sickness_lv.membership_functions.values())
        for sickness_mf in sickness_mfs:
            for mf in mfs_values:
                if sickness_mf.name == mf.keys()[0]:
                    s.append({sickness_mf: mf[mf.keys()[0]]})

        return self.centroid_of_polygon(self.get_polygon_vertices(s))[0]

    def get_polygon_vertices(self, min_mfs):
        """
        Input: min_mfs - a list of dictionaries containing the mf and
                         the point where it will be clipped
        """
        # build the clipped trapeziums
        trapeziums = []
        for min_mf in min_mfs:
            mf, mf_clip = min_mf.keys()[0], min_mf[min_mf.keys()[0]]
            # we will always have 4 points in a trapezoid
            point1 = (mf.range[0], 0)

            try:
                a, b = mf.get_ascending_slope()
                x = (mf_clip - b)/a
            except:
                x = mf.range[0]
            point2 = (x, mf_clip)

            try:
                a, b = mf.get_descending_slope()
                x = (mf_clip - b)/a
            except:
                x = mf.range[3]
            point3 = (x, mf_clip)

            point4 = (mf.range[3], 0)
            trapeziums.append([point1, point2, point3, point4])

        if not trapeziums:
            return []

        if len(trapeziums) == 1:
            return trapeziums[0]

        intersection_points = []
        for i in range(len(trapeziums)-1):
            for j in range(len(trapeziums[i])-1):
                line1 = [trapeziums[i][j], trapeziums[i][j+1]]
                for k in range(len(trapeziums[i+1])-1):
                    line2 = [trapeziums[i+1][k], trapeziums[i+1][k+1]]
                    intersection_point = self.line_intersection(line1, line2)
                    if intersection_point:
                        intersection_points.append(intersection_point)
                        break

        points = []
        # treat differently the first trapezium, the last one
        # and the ones in the middle

        # first trapezium
        first_trapezium = trapeziums[0]
        for point in first_trapezium:
            if point[0] < intersection_points[0][0]:
                points.append(point)
        if (intersection_points[0][0] > points[-1][0]):
            points.append(intersection_points[0])

        # trapeziums in the middle
        for i in range(1, len(trapeziums)-1):
            point = intersection_points[i]
            first_trapezium = trapeziums[i]
            for j in range(len(first_trapezium)):
                if (first_trapezium[j][0] < point[0] and
                        first_trapezium[j][0] > points[-1][0]):
                    points.append(first_trapezium[j])
            if (point[0] > points[-1][0]):
                points.append(point)

        # last trapezium
        last_trapezium = trapeziums[len(trapeziums)-1]
        len_int_points = len(intersection_points) - 1
        for point in last_trapezium:
            if point[0] > intersection_points[len_int_points][0]:
                points.append(point)

        return points

    def line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return float(a[0]) * b[1] - float(a[1]) * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        if (x < min(line1[0][0], line1[1][0]) or
                x > max(line1[0][0], line1[1][0]) or
                x < min(line2[0][0], line2[1][0]) or
                x > max(line2[0][0], line2[1][0])):
            return None
        if (y < min(line1[0][1], line1[1][1]) or
                y > max(line1[0][1], line1[1][1]) or
                y < min(line2[0][1], line2[1][1]) or
                y > max(line2[0][1], line2[1][1])):
            return None
        return x, y

    def _order_by_first_point(self, functions):
        """
        Order the functions by the first point in the trapezoid
        """
        for i in range(len(functions)):
            for j in range(i+1, len(functions)):
                if functions[i].range[0] >= functions[j].range[0]:
                    functions[i], functions[j] = functions[j], functions[i]
        return functions

    def area_of_polygon(self, x, y):
        """
        Calculates the signed area of an arbitrary polygon given its verticies
        """
        area = 0.0
        for i in xrange(-1, len(x) - 1):
            area += x[i] * (y[i + 1] - y[i - 1])
        return area / 2.0

    def centroid_of_polygon(self, points):
        if not points:
            return (0, 0)
        area = self.area_of_polygon(*zip(*points))
        result_x = 0
        result_y = 0
        N = len(points)
        points = IT.cycle(points)
        x1, y1 = next(points)
        for i in range(N):
            x0, y0 = x1, y1
            x1, y1 = next(points)
            cross = (x0 * y1) - (x1 * y0)
            result_x += (x0 + x1) * cross
            result_y += (y0 + y1) * cross
        result_x /= (area * 6.0)
        result_y /= (area * 6.0)
        return (result_x, result_y)
