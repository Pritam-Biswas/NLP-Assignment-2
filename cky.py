"""
COMS W4705 - Natural Language Processing - Fall 2019
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg
import json

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        n = len(tokens)

        dp = [[ [] for x in range(n)] for y in range(n)]

        for i in range(0,n):
            parses = self.grammar.rhs_to_rules[(tokens[i],)]
            for parse in parses:
                head = parse[0]
                if not head in dp[i][i]:
                    dp[i][i].append(head)

        for l in range(2,n+1):
            for i in range(0,n-l+1):
                j = i+l-1

                for k in range(i,j):
                    head = dp[i][k]
                    tail = dp[k+1][j]

                    if len(head) == 0 or len(tail) == 0:
                        continue

                    # get combinations
                    combinations = []
                    for x in range(0,len(head)):
                        for y in range(0,len(tail)):
                            parses = self.grammar.rhs_to_rules[(head[x], tail[y])]

                            for parse in parses:
                                if not parse[0] in combinations:
                                    combinations.append(parse[0])

                    dp[i][j] = dp[i][j] + combinations

                dp[i][j] = list(set(dp[i][j]))

        if self.grammar.startsymbol in dp[0][n-1]:
            return True
        else:
            return False

    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        table= {}
        probs = {}

        non_terminals = self.grammar.lhs_to_rules.keys()

        n = len(tokens)

        #initialization
        for i in range(0,n):
            parses = self.grammar.rhs_to_rules[(tokens[i],)]

            table[(i,i+1)] = {}
            probs[(i,i+1)] = {}

            for parse in parses:
                head = parse[0]
                prob = parse[-1]

                if not head in table[(i,i+1)]:
                    table[(i,i+1)][head] = tokens[i]
                    probs[(i,i+1)][head] = math.log2(prob)
                else:
                    if probs[(i,i+1)][head] < prob:
                        table[(i,i+1)][head] = tokens[i]
                        probs[(i,i+1)][head] = math.log2(prob)


        for l in range(2,n+1):
            for i in range(0,n-l+1):
                j = i+l-1

                table[(i,j+1)] = {}
                probs[(i,j+1)] = {}
                for k in range(i,j):
                    if not (i,k+1) in table or not (k+1,j+1) in table:
                        continue
                    head = table[(i,k+1)]
                    tail = table[(k+1,j+1)]


                    if len(head.keys()) == 0 or len(tail.keys()) == 0:
                        continue

                    for head_key in head.keys():
                        for tail_key in tail.keys():
                            parses = self.grammar.rhs_to_rules[(head_key, tail_key)]

                            for parse in parses:
                                parse_head = parse[0]
                                parse_prob = parse[-1]

                                if not parse_head in table[(i,j+1)]:
                                    table[(i,j+1)][parse_head] = ((head_key, i, k+1), (tail_key, k+1,j+1))
                                    probs[(i,j+1)][parse_head] = math.log2(parse_prob) + probs[(i,k+1)][head_key] + probs[(k+1,j+1)][tail_key]

                                else:

                                    if probs[(i,j+1)][parse_head] < math.log2(parse_prob) + probs[(i,k+1)][head_key] + probs[(k+1,j+1)][tail_key]:
                                        table[(i,j+1)][parse_head] = ((head_key, i, k+1), (tail_key, k+1,j+1))
                                        probs[(i,j+1)][parse_head] = math.log2(parse_prob) + probs[(i,k+1)][head_key] + probs[(k+1,j+1)][tail_key]

        return table, probs


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4

    # print ('enter for i:'+str(i)+', j:'+str(j)+', symbol :'+nt)
    # print('\n')
    # if not nt in chart[(i,j)]:
    #     print ('enter edge case of non existing symbol')
    #     return;

    parse = chart[(i,j)][nt]

    output_str = '(\'' + nt+'\', '

    if not isinstance(parse,str):
        if len(parse) == 2: # 2 children
            c1 = parse[0]
            c2 = parse[1]
            
            head1 = c1[0]
            head2 = c2[0]

            output1 = get_tree(chart, c1[1],c1[2], head1)
            output2 = get_tree(chart, c2[1], c2[2], head2)

            return (nt, output1, output2)

    if isinstance(parse,str):
        head = parse

        return (nt, head)

    return None 
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        # toks =['miami', 'flights','cleveland', 'from', 'to','.']
        print(parser.is_in_language(toks))

        if parser.is_in_language(toks):
            table,probs = parser.parse_with_backpointers(toks)
            assert check_table_format(table)
            assert check_probs_format(probs)

            print (get_tree(table, 0, len(toks), grammar.startsymbol))

        
