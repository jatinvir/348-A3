"""
DO NOT MODIFY THIS FILE AT ALL
"""

# e.g., To run this script to generate a join plan for a query with the input file named input1:
#     python main.py --query input1
# and to get cardinality of each subquery with consecutive relations add the -c option:
#     python main.py --query input1 -c

# NOTE: We are using python 3 syntax (do NOT use python 2)
#       The input file must be in the current directory 
#       or you must provide a path relative to the current directory
#       (line 35 is getting the file path simply via: "./" + args.queury)

import argparse

from join_graph import *

def printTree(node, level=0):
    if node is not None:
        printTree(node.right, level + 1)        
        if node.isLeaf():
            assert(1 == len(node.rels))
            print("\t" * level + node.rels[0].name)
        else:    
            print("\t" * level + "JO(" + str(node.estOutCard) +")")
        printTree(node.left, level + 1)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True)
    parser.add_argument('-c', '--cardinality',
        help='print cardinality of subqueries, otherwise print join plan.',
        action="store_false")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    joinGraph = JoinGraph("./" + args.query)
    if args.cardinality:
        joinOrder = joinGraph.getBestJoinOrder()
        printTree(joinOrder)
    else:
        numRels = len(joinGraph.rels)
        for num_rels_joined in range(2, numRels):
            for first_rel_pos in range(0, numRels - num_rels_joined):
                end_rel_pos = first_rel_pos + num_rels_joined
                rels = joinGraph.rels[first_rel_pos: end_rel_pos]
                print(joinGraph.getCardinality(rels))
        print(joinGraph.getCardinality(joinGraph.rels))

