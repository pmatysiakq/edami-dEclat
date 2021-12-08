class FI:

    def __init__(self, setx):
        self.itemset = setx
        self.supp = 0
        self.difflist = set()

    def increment_supp(self):
        self.supp += 1

    def get_supp(self):
        return self.supp

    def set_supp(self, new_supp):
        self.supp = new_supp

    def get_itemset(self):
        return self.itemset

    def get_difflist(self):
        return self.difflist

    def set_difflist(self, new_difflist):
        self.difflist = new_difflist
