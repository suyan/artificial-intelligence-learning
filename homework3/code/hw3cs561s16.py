import copy
import sys


class Node(object):
    def __init__(self, name='', parents=list(), cpt=list()):
        self.name = name
        self.parents = parents
        self.cpt = cpt
        self.type = ''

    def get_probability(self, sign, e):
        if self.type == 'decision':
            return 1.0

        for i in range(len(self.cpt)):
            flag = True
            for j in range(len(self.parents)):
                parent = self.parents[j]
                value = self.cpt[i][j + 1]
                if e[parent] != value:
                    flag = False
                    break
            if flag and sign == '+':
                return self.cpt[i][0]
            elif flag and sign == '-':
                return 1.0 - self.cpt[i][0]


class BayesNetwork(object):
    def __init__(self):
        self.utility = None
        self.names = list()
        self.nodes = list()

    def add(self, node=Node()):
        self.names.append(node.name)
        self.nodes.append(node)

    def get(self, name=''):
        return self.nodes[self.names.index(name)]

    def is_decision(self, name=''):
        node = self.get(name)
        if node.type == 'decision':
            return True
        else:
            return False


class Agent(object):
    def __init__(self):
        # file_name = 'samples/sample02.txt'
        file_name = sys.argv[2]
        self.input = open(file_name, 'r')
        self.output = open('output.txt', 'w')
        self.bayes_network = BayesNetwork()
        self.queries = list()

    def read_line(self):
        return self.input.readline().strip('\n')

    def write_line(self, function, value, meu_values=list()):
        if function == 'P':
            self.output.write("%.2f" % round(value, 2))
        elif function == 'EU':
            self.output.write(str(int(round(value))))
        elif function == 'MEU':
            meu = ''
            for v in meu_values:
                meu += v + ' '
            self.output.write(meu + str(int(round(value))))

    def build_bayes_network(self):
        # input queries
        query = self.read_line()
        while query != '******':
            self.queries.append(query)
            query = self.read_line()

        # add nodes in bayes network
        query = self.read_line()
        while query != '':
            names = query.split(' ')
            node_name = names[0]
            parents = names[2:]
            cpt = list()

            decision = False
            for i in range(2 ** len(parents)):
                tmp = self.read_line().split(' ')
                if tmp[0] == 'decision':
                    decision = True
                else:
                    tmp[0] = float(tmp[0])
                cpt.append(tmp)

            node = Node(node_name, parents, cpt)

            if decision:
                node.type = 'decision'

            self.bayes_network.add(node)

            query = self.read_line()
            if query != '***':
                break
            query = self.read_line()

        # add utility nodes in bayes network
        if query == '******':
            names = self.read_line().strip(' ').split(' ')
            node_name = 'utility'
            parents = names[2:]
            cpt = list()
            for i in range(2 ** len(parents)):
                names = self.read_line().split(' ')
                names[0] = float(names[0])
                cpt.append(names)

            node = Node(node_name, parents, cpt)
            node.type = 'utility'
            self.bayes_network.utility = node

    def __del__(self):
        self.input.close()
        self.output.close()

    def ask(self, query='', bn=BayesNetwork()):
        tmp = query.split('(')
        function = tmp[0]
        arguments = tmp[1].strip(')')

        if function == 'P':
            self.ask_p(function, arguments, bn)
        elif function == 'EU':
            self.ask_eu(function, arguments, bn)
        elif function == 'MEU':
            self.ask_meu(function, arguments, bn)

    def ask_p(self, function, arguments, bn=BayesNetwork()):
        if ' | ' in arguments:
            tmp = arguments.split(' | ')
            X = dict()
            for item in tmp[0].split(', '):
                t = item.split(' = ')
                X[t[0]] = t[1]

            e = dict()
            for item in tmp[1].split(', '):
                t = item.split(' = ')
                e[t[0]] = t[1]
            p = self.enumeration_ask(X, e, bn)

        else:
            e = {}
            for item in arguments.split(', '):
                t = item.split(' = ')
                e[t[0]] = t[1]
            p = self.enumerate_all(bn.names, e, bn)
        self.write_line(function, p)

    def enumeration_ask(self, X, e, bn=BayesNetwork()):
        for item in X.keys():
            if bn.is_decision(item) and e[item] != X[item]:
                return 0.0
            elif bn.is_decision(item):
                X.pop(item, None)

        enumerations = list()
        index = 0
        for i in range(2 ** len(X)):
            values = self.generate_boolean(i, len(X))
            ex = copy.deepcopy(e)
            flag = True
            for j in range(len(X)):
                item = X.keys()[j]
                ex[item] = values[j]
                if values[j] != X[item]:
                    flag = False
            if flag:
                index = i

            enu = self.enumerate_all(bn.names, ex, bn)
            enumerations.append(enu)

        normalize = enumerations[index] / sum(enumerations)

        return normalize

    def enumerate_all(self, variables, e, bn):
        if len(variables) == 0:
            return 1.0
        y = variables[0]
        node = bn.get(y)
        if y in e.keys():
            return node.get_probability(e[y], e) * self.enumerate_all(variables[1:], e, bn)
        else:
            ey_true = copy.deepcopy(e)
            ey_true[y] = '+'
            ey_false = copy.deepcopy(e)
            ey_false[y] = '-'
            return node.get_probability('+', e) * self.enumerate_all(variables[1:], ey_true, bn) + \
                   node.get_probability('-', e) * self.enumerate_all(variables[1:], ey_false, bn)

    def ask_eu(self, function, arguments, bn):
        tmp = arguments.split(' | ')
        if len(tmp) > 1:
            tmp[0] = tmp[0] + ', ' + tmp[1]

        variables = tmp[0].split(', ')
        e = dict()
        for item in variables:
            item = item.split(' = ')
            e[item[0]] = item[1]
        eu = self.eu_enumerate_all(e, bn)
        self.write_line(function, eu)

    def eu_enumerate_all(self, e, bn):
        utility = bn.utility
        parents = utility.parents
        result = 0.0
        for t in utility.cpt:
            X = dict()
            for j in range(len(parents)):
                X[parents[j]] = t[j + 1]
            result += self.enumeration_ask(X, e, bn) * t[0]
        return result

    def ask_meu(self, function, arguments, bn):
        tmp = arguments.split(' | ')

        X = list()
        for item in tmp[0].split(', '):
            X.append(item)

        e = dict()
        if len(tmp) == 2:
            for item in tmp[1].split(', '):
                t = item.split(' = ')
                e[t[0]] = t[1]

        meu_values, meu = self.meu_enumerate_all(X, e, bn)
        self.write_line(function, meu, meu_values)

    def meu_enumerate_all(self, x, e, bn):
        maximum = -65535
        max_values = []
        for i in range(2 ** len(x)):
            values = self.generate_boolean(i, len(x))
            ei = copy.deepcopy(e)
            for j in range(len(x)):
                ei[x[j]] = values[j]
            m = self.eu_enumerate_all(ei, bn)
            if m > maximum:
                maximum = m
                max_values = values
        return max_values, maximum

    @staticmethod
    def generate_boolean(num, l):
        values = []
        for i in range(l):
            if (num >> i) & 1 == 0:
                values.append('+')
            else:
                values.append('-')
        return values

    def run(self):
        self.build_bayes_network()

        first_line = True
        for query in self.queries:
            if not first_line:
                self.output.write('\n')
            first_line = False
            self.ask(query, self.bayes_network)


if __name__ == "__main__":
    agent = Agent()
    agent.run()
