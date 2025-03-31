"""
DO NOT MODIFY ANY GIVEN FIELDS OR COMPELTED FUNCTIONS
    You must implement getBestJoinOrder(self) and getCardinality(self, inRels : list)
    You can add new functions or variables if you wish
"""


class JoinGraph:
    """
    A class used to represent a join graph

    Fields
    -----------
    rels : [Relation]
        all join relations specified in the input file
    joinConditions : [JoinCondition]
        all join conditions specified in the input file
    """

    rels = None
    joinConditions = None

    def __init__(self, path: str) -> None:
        with open(path, "r") as f:
            lines = f.readlines()
            self._load(lines)

    def getBestJoinOrder(self):
        """
        Compute the join order with lowest cost.
        Return : JoinPlan
            root of the join tree
        """
        # You must implement this function
        # so a DP algorithm

        dp = {}

        # Base Case
        length = len(self.rels)

        for i in range(length):
            dp[(i, i)] = JoinPlan(None, None, [self.rels[i]],
                                  self.getCardinality([self.rels[i]]))

        # now build case
        for size in range(2, length + 1):
            # print(i)
            for j in range(0, length - size + 1):

                sizeJ = size + j - 1

                for k in range(j, sizeJ):
                    if (j, k) not in dp or (k + 1, sizeJ) not in dp:
                        continue
                    leftChild = dp[(j, k)]
                    rightChild = dp[(k + 1, sizeJ)]

                    relationsToJoin = leftChild.rels + rightChild.rels

                    # right

                    if rightChild.estOutCard > leftChild.estOutCard:
                        leftChild, rightChild = rightChild, leftChild

                    plan = JoinPlan(
                        leftChild, rightChild, relationsToJoin, self.getCardinality(relationsToJoin))

                    if (j, sizeJ) not in dp or plan.estCost < dp[(j, sizeJ)].estCost:
                        dp[(j, sizeJ)] = plan
        return dp[(0, length - 1)]

    def _load(self, lines: list) -> None:
        """
        Inject join relations and conditions
        """
        assert (len(lines) >= 3)
        numRels = int(lines[0])
        self.rels = [None] * numRels
        # inject join rels
        cardinalities = lines[1].split(",")
        assert (len(cardinalities) == numRels)
        relationNameIdxMap = {}
        for i in range(numRels):
            relationName = "R" + str(i)
            self.rels[i] = Relation(relationName, i, int(cardinalities[i]))
            relationNameIdxMap[relationName] = i
        # inject foreign keys
        foreignRelationNames = lines[2].split(",")
        assert (len(foreignRelationNames) == numRels - 1)
        self.joinConditions = [None] * (numRels - 1)
        for i in range(numRels - 1):
            foreignRelationIdx = relationNameIdxMap[foreignRelationNames[i]]
            if i == foreignRelationIdx:
                self.joinConditions[i] = JoinCondition(
                    self.rels[i+1], self.rels[i])
            elif i + 1 == foreignRelationIdx:
                self.joinConditions[i] = JoinCondition(
                    self.rels[i], self.rels[i+1])
            else:
                assert (False)

    def getCardinality(self, inRels: list) -> int:
        """
        Compute cardinality given a list of join relations
        Input: [Relation]
        Output: int
            estimated output cardinality of given join relations
        """
        # You must implement this function

        #      Fields
        # -----------
        # rels : [Relation]
        #     all join relations specified in the input file
        # joinConditions : [JoinCondition]
        #     all join conditions specified in the input file
        # """

        # class JoinCondition:
        """
        A class used to track foreign key for chain joins

        Fields
        -----------
        primaryRelation : Relation
            relation containing primary key
        foreignRelation : int
            relation containing foreign key
        """

        if len(inRels) == 1:
            return inRels[0].cardinality

        numerator = 1
        denominator = 1

        for rel in inRels:
            numerator *= rel.cardinality

        for i in range(len(inRels) - 1):
            leftRel = inRels[i]
            rightRel = inRels[i + 1]

            for condition in self.joinConditions:
                if (condition.primaryRel == leftRel and condition.foreignRel == rightRel):
                    denominator *= leftRel.cardinality
                    break
                elif (condition.foreignRel == leftRel and condition.primaryRel == rightRel):
                    denominator *= rightRel.cardinality
                    break

        return numerator // denominator


class Relation:
    """
    A class used to represent base relation table

    Fields
    -----------
    name : str
        name of the relation
    idx  : int
        index of the relation generated during injection
    cardinality : int
        cardinality of the relation
    """

    name = None
    idx = None
    cardinality = None

    def __init__(self, name: str, idx: int, cardinality: int) -> None:
        self.name = name
        self.idx = idx
        self.cardinality = cardinality

    def __str__(self) -> str:
        """
        Represent relation in the format of name(idx):cardinality
        E.g. A(0):50
        """
        return self.name + "(" + str(self.idx) + "):" + str(self.cardinality)


class JoinCondition:
    """
    A class used to track foreign key for chain joins

    Fields
    -----------
    primaryRelation : Relation
        relation containing primary key
    foreignRelation : int
        relation containing foreign key
    """

    primaryRel = None
    foreignRel = None

    def __init__(self, primaryRel: Relation, foreignRel: Relation) -> None:
        self.primaryRel = primaryRel
        self.foreignRel = foreignRel


class JoinPlan:
    """
    A class used to represent a logical join tree

    Fields
    -----------
    left : JoinPlan
        left child
    right : JoinPlan
        right child
    rels : [Relation]
        join relations matched in the join tree
    estOutCard : int
        estimated output cardinality of the join tree
    estCost : int
        cost of the join tree
    """

    left = None
    right = None
    rels = None
    estOutCard = 0
    estCost = 0

    def __init__(self, left, right, rels: list, estOutCard: int) -> None:
        self.left = left
        self.right = right
        self.rels = rels
        self.estOutCard = int(estOutCard)
        assert (self.estOutCard != 0)
        if self.isLeaf():
            self.estCost = 0
        else:
            self.estCost = left.estCost + right.estCost + estOutCard

    def isLeaf(self) -> bool:
        """
        Check if this is the leaf
        """
        return self.left is None and self.right is None
