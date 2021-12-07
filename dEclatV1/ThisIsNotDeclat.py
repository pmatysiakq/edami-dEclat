from ParseData import *
from FrequentItemset import *

class dEclat:
    def __init__(self, user, min_supp):
        self.user = user
        self.data = Data(user)
        self.min_supp = min_supp
        self.freq_itemsets = []
        self.step = 1
        self.itemsets = []
        # self.show_transacitons_id = False
        # self.max_pattern_len = 9999999999

    def create_itemsets(self, max_items):
        items = sorted(self.data.unique_numbers, reverse=False)
        sets = []

        for i in items:
            new_set = set()
            new_set.add(i)
            sets.append(new_set)
        if max_items == 1:
            return sets

        for i in range(max_items-1):
            new_sets = []
            for setx in sets:
                for j in range(len(sets)):
                    new_sets.append(setx.union(sets[j]))
            sets = sets + new_sets

        return sets

    def create_candidate_fis(self):
        sets = self.create_itemsets(2)
        fis = []
        for setx in sets:
            fi = FrequentItemset(setx)
            fis.append(fi)
        return fis

    def calculate_fis(self):
        candidates = self.create_candidate_fis()
        tweets = self.data.discretized_data

        for candidate in candidates:
            for tweet in tweets:
                if candidate.itemset.issubset(tweet):
                    candidate.increment_supp()

        fis = []
        for candidate in candidates:
            if candidate.supp > self.min_supp:
                fis.append(candidate)
        return fis

    def show_fis(self):
        fis = self.calculate_fis()
        array = []
        for fi in fis:
            setx = []
            for item in fi.itemset:
                for key in self.data.dictionary.keys():
                    if item == self.data.dictionary[key]:
                        setx.append(key)
            if [fi.supp, setx] not in array:
                array.append([fi.supp, setx])
        with open(f"results/fis-{self.user}.txt", "w", encoding='utf-8') as file:
            for supp, setx in sorted(array, reverse=True):
                file.write(f"SUPP: {supp} .. SET: {setx}\n")
                print(f"SUPP: {supp} .. SET: {setx}")

if __name__ == "__main__":
    declat = dEclat("elonmusk", 3)

    declat.show_fis()

