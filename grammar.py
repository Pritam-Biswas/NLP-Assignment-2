"""
COMS W4705 - Natural Language Processing - Fall 2019
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1
        non_terminals = self.lhs_to_rules.keys()
 
        for key in self.lhs_to_rules.keys():
            prob_list = []
            parse_list = self.lhs_to_rules[key]


            for parse in parse_list:
                head = parse[0]
                if not len(parse) == 3:
                    return False
                if head.islower() or not head in non_terminals:
                    
                    return False

                mapping = parse[1]

                if len(mapping) == 2:
                    if not mapping[0] in non_terminals or not mapping[1] in non_terminals:
                        return False
                if len(mapping) == 1:
                    if mapping[0].isupper():
                        return False
                if len(mapping) > 2:
                    return False

                prob_list.append(parse[-1])
            prob_sum = fsum(prob_list)
            prob_sum = round(prob_sum,2)
            if not prob_sum == 1.0:
                return False
        return True


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        res = grammar.verify_grammar()
        if res == True:
            print("valid grammar")
        else:
            print("not a valid grammar")
