#!/usr/bin/env python
import sys


class Sentence:
    def __init__(self, op, args=[]):
        self.op = op
        self.args = map(Sentence.build_sentence, args)

    def __hash__(self):
        return hash(self.op) ^ hash(tuple(self.args))

    def __repr__(self):
        if len(self.args) == 0:
            return self.op
        elif self.op not in ['&&', '=>']:
            args = str(self.args[0])
            if args[0].islower():
                args = '_'
            for arg in self.args[1:]:
                arg = str(arg)
                if arg[0].islower():
                    arg = '_'
                args = args + ', ' + arg
            return self.op + '(' + args + ')'
        else:
            if self.args[0].op in ['&&', '=>']:
                sentence = '(' + str(self.args[0]) + ')'
            else:
                sentence = str(self.args[0])
            sentence += ' ' + self.op + ' '

            if self.args[1].op in ['&&', '=>']:
                sentence += '(' + str(self.args[1]) + ')'
            else:
                sentence += str(self.args[1])
            return sentence

    def __eq__(self, other):
        return isinstance(other, Sentence) and self.op == other.op and self.args == other.args

    @staticmethod
    def build_sentence(item):
        if isinstance(item, Sentence):
            return item

        if '=>' in item:
            pos = item.index('=>')
            lhs, rhs = item[:pos], item[pos + 1:]
            expr = Sentence('=>', [lhs, rhs])
            return expr
        elif '&&' in item:
            pos = item.index('&&')
            first, second = item[:pos], item[pos + 1:]
            expr = Sentence('&&', [first, second])
            return expr
        elif isinstance(item, str):
            return Sentence(item)

        if len(item) == 1:
            return Sentence.build_sentence(item[0])

        sentence = Sentence(item[0], item[1:][0])
        return sentence

    @staticmethod
    def parse(s):
        s = '(' + s + ')'
        s = s.replace('(', ' ( ')
        s = s.replace(')', ' ) ')
        s = s.replace(',', ' ')

        s = s.replace('&&', ' && ')
        s = s.replace('=>', ' => ')
        tokens = s.split()
        return Sentence.read_token_list(tokens)

    @staticmethod
    def read_token_list(tokens):
        first = tokens.pop(0)
        if first == '(':
            new_sentence = []
            while tokens[0] != ')':
                new_sentence.append(Sentence.read_token_list(tokens))
            tokens.pop(0)
            return new_sentence
        else:
            return first

    @staticmethod
    def is_variable(item):
        return isinstance(item, Sentence) and item.op.islower() and item.args == []


class KnowledgeBase:
    var_count = 0
    logs = []
    flag = False

    def __init__(self, raw_sentences=list()):
        self.sentences = {}
        self.goals = set()
        for sentence in raw_sentences:
            self.tell(sentence)

    def tell(self, sentence):
        self.index_predicate(sentence, sentence)

    def ask(self, query):
        return KnowledgeBase.fol_bc_ask(self, query)

    def index_predicate(self, main_sentence, inner_sentence):
        if self.is_predicate(inner_sentence):
            if inner_sentence.op in self.sentences:
                if main_sentence not in self.sentences[inner_sentence.op]:
                    self.sentences[inner_sentence.op].append(main_sentence)
            else:
                self.sentences[inner_sentence.op] = [main_sentence]
        else:
            self.index_predicate(main_sentence, inner_sentence.args[0])
            self.index_predicate(main_sentence, inner_sentence.args[1])

    def get_rules_for_goal(self, goal):
        predicate = self.get_predicate(goal)
        if predicate in self.sentences:
            rules = []
            for sentence in self.sentences[predicate]:
                rule = sentence
                if sentence.op == '=>':
                    sentence = sentence.args[1]
                if sentence.op != goal.op:
                    continue
                if len(sentence.args) != len(goal.args):
                    continue

                # check every arg
                flag = True
                for i in range(len(sentence.args)):
                    if goal.args[i] == sentence.args[i]:
                        pass
                    elif Sentence.is_variable(goal.args[i]) or Sentence.is_variable(sentence.args[i]):
                        pass
                    else:
                        flag = False

                if flag:
                    rules.append(rule)
            return rules
        else:
            return []

    def get_predicate(self, goal):
        if self.is_predicate(goal):
            return goal.op
        else:
            return self.get_predicate(goal.args[0])

    @staticmethod
    def is_predicate(sentence):
        return sentence.op not in ['&&', '=>'] and sentence.op[0].isupper()

    @staticmethod
    def fol_bc_ask(kb, query):
        return KnowledgeBase.fol_bc_or(kb, query, {})

    @staticmethod
    def fol_bc_or(kb, goal, theta):
        KnowledgeBase.logs.append("Ask: " + str(KnowledgeBase.substitute(theta, goal)))

        flag = False
        rules = kb.get_rules_for_goal(goal)
        for i in range(len(rules)):
            std_rule = KnowledgeBase.standardize_variables(rules[i])
            lhs, rhs = KnowledgeBase.separate_sentence(std_rule)

            for theta1 in KnowledgeBase.fol_bc_and(kb, lhs, KnowledgeBase.unify(rhs, goal, theta)):
                KnowledgeBase.logs.append("True: " + str(KnowledgeBase.substitute(theta1, goal)))
                flag = True
                yield theta1

            if (i < len(rules) - 1) and KnowledgeBase.flag:
                KnowledgeBase.flag = False
                KnowledgeBase.logs.append("Ask: " + str(KnowledgeBase.substitute(theta, goal)))

        if not flag:
            KnowledgeBase.flag = True
            KnowledgeBase.logs.append("False: " + str(KnowledgeBase.substitute(theta, goal)))

    @staticmethod
    def fol_bc_and(kb, goals, theta):
        b = goals
        if theta is None:
            pass
        elif isinstance(goals, list) and len(goals) == 0:
            yield theta
        else:
            if goals.op == '&&':
                first = goals.args[0]
                rest = goals.args[1]

                if first.op == '&&':
                    while not KnowledgeBase.is_predicate(first):
                        rest = Sentence('&&', [first.args[1], rest])
                        first = first.args[0]
            else:
                first = goals
                rest = []

            for theta1 in KnowledgeBase.fol_bc_or(kb, KnowledgeBase.substitute(theta, first), theta):
                for theta2 in KnowledgeBase.fol_bc_and(kb, rest, theta1):
                    yield theta2

    @staticmethod
    def standardize_variables(sentence, variables=None):
        if variables is None:
            variables = {}

        if not isinstance(sentence, Sentence):
            return sentence

        if Sentence.is_variable(sentence):
            if sentence in variables:
                return variables[sentence]
            else:
                new_variable = Sentence('z_' + str(KnowledgeBase.var_count))
                KnowledgeBase.var_count += 1
                variables[sentence] = new_variable
                return new_variable
        else:
            return Sentence(sentence.op,
                            list(KnowledgeBase.standardize_variables(arg, variables) for arg in sentence.args))

    @staticmethod
    def separate_sentence(sentence):
        if sentence.op == '=>':
            return KnowledgeBase.expand_brackets(sentence.args[0]), sentence.args[1]
        else:
            return [], sentence

    @staticmethod
    def expand_brackets(sentence):
        if sentence.op == "&&":
            arg1 = KnowledgeBase.expand_brackets(sentence.args[0])
            arg2 = KnowledgeBase.expand_brackets(sentence.args[1])
            return Sentence(sentence.op, [arg1, arg2])
        else:
            return sentence

    @staticmethod
    def unify(x, y, theta={}):
        if theta is None:
            return None
        elif x == y:
            return theta
        elif Sentence.is_variable(x):
            return KnowledgeBase.unify_var(x, y, theta)
        elif Sentence.is_variable(y):
            return KnowledgeBase.unify_var(y, x, theta)
        elif isinstance(x, Sentence) and isinstance(y, Sentence):
            return KnowledgeBase.unify(x.args, y.args, KnowledgeBase.unify(x.op, y.op, theta))
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            return KnowledgeBase.unify(x[1:], y[1:], KnowledgeBase.unify(x[0], y[0], theta))
        else:
            return None

    @staticmethod
    def unify_var(var, x, theta):
        if var in theta:
            return KnowledgeBase.unify(theta[var], x, theta)
        elif x in theta:
            return KnowledgeBase.unify(var, theta[x], theta)

        new_subst = theta.copy()
        new_subst[var] = x
        return new_subst

    @staticmethod
    def substitute(theta, sentence):
        assert isinstance(sentence, Sentence)

        if Sentence.is_variable(sentence):
            if sentence in theta:
                return theta[sentence]
            else:
                return sentence
        else:
            return Sentence(sentence.op, list(KnowledgeBase.substitute(theta, arg) for arg in sentence.args))


class Solution:
    @staticmethod
    def run():
        rules = []
        # file_name = "sample01.txt"
        file_name = sys.argv[2]

        with open(file_name) as f:
            goal = f.readline().strip()
            count = int(f.next().strip())
            while count > 0:
                sentence = f.next().strip()
                rules.append(sentence)
                count -= 1

        f = open("output.txt", "w")
        if Solution.is_valid(goal, rules):
            for log in KnowledgeBase.logs:
                f.write(log + "\n")
            f.write("True")
        else:
            for log in KnowledgeBase.logs:
                f.write(log + "\n")
            f.write("False")

    @staticmethod
    def is_valid(goal, rules):
        knowledge_base = KnowledgeBase(map(Sentence.build_sentence, map(Sentence.parse, rules)))
        queries = goal.split("&&")
        results = []
        for query in queries:
            q = Sentence.build_sentence(Sentence.parse(query))
            flag = False
            for ans in knowledge_base.ask(q):
                flag = True
                break
            results.append(flag)

        for result in results:
            if not result:
                return False

        return True


if __name__ == '__main__':
    Solution.run()
