from ParseData import *
from FrequentItemset import *

class dEclat:
    def __init__(self, user, min_supp):
        self.user = user
        self.data = Data(user)
        self.min_supp = min_supp
        self.freq_itemsets = []
        self.P = self.create_initial_itemsets()
        # self.show_transacitons_id = False
        # self.max_pattern_len = 9999999999

    def create_initial_itemsets(self):
        data = self.data.unique_numbers
        tweets = self.data.discretized_data
        candidates = []
        for elem in data:
            candidate = FrequentItemset({elem})
            candidates.append(candidate)

        for candidate in candidates:
            for tweet in tweets:
                if candidate.itemset.issubset(tweet[1]):
                    candidate.increment_supp()
                else:
                    candidate.difflist.add(tweet[0])

        initial_fi = self.remove_non_frequent(candidates)

        return initial_fi

    def calculate_difflists(self, set_A: FrequentItemset, set_B: FrequentItemset):
        return set_B.difflist.difference(set_A.difflist)

    def remove_non_frequent(self, candidates):
        frequent_itemsets = []
        for candidate in candidates:
            if candidate.get_supp() >= self.min_supp:
                frequent_itemsets.append(candidate)

        return frequent_itemsets

    def run_declat(self, P):
        T = []
        for i in range(0, len(P)):
            Ti = []
            for j in range(i+1, len(P)):
                R = FrequentItemset(P[i].itemset.union(P[j].itemset))
                R.difflist = R.difflist.union(self.calculate_difflists(P[i], P[j]))
                R.supp = (P[i].get_supp() - len(R.difflist))
                if R.get_supp() >= self.min_supp:
                    Ti.append(R)
                    if R not in self.freq_itemsets:
                        self.freq_itemsets.append(R)
            if len(Ti) > 0:
                T.append(Ti)
        for i in range(len(T)):
            self.run_declat(T[i])

    def get_fis(self):
        fis = self.freq_itemsets
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
