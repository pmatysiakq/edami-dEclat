class FI:

    def __init__(self, setx):
        self.itemset = setx
        self.supp = 0
        self.difflist = set()

    def increment_supp(self):
        self.supp += 1

    def get_supp(self):
        return self.supp

    def get_itemset(self):
        return self.itemset
