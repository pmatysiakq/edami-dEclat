from Data import *
from FI import *


class dEclat:
    def __init__(self, user, min_supp, show_supp=False):
        self.user = user
        self.data = Data(user)
        self.min_supp = min_supp
        self.freq_isets = list()
        self.initial_dataset = self.create_initial_itemsets()
        self.show_supp = show_supp

    def create_initial_itemsets(self):
        data = self.data.unique_numbers
        tweets = self.data.discretized_data
        candidates = list()
        for elem in data:
            candidate = FI({elem})
            candidates.append(candidate)

        for candidate in candidates:
            for tweet in tweets:
                if candidate.get_itemset().issubset(tweet[1]):
                    candidate.increment_supp()
                else:
                    candidate.difflist.add(tweet[0])

        initial_fi = self.remove_non_frequent(candidates)

        return initial_fi

    @staticmethod
    def calc_difflists(set_A: FI, set_B: FI):
        return set_B.difflist.difference(set_A.difflist)

    def remove_non_frequent(self, candidates):
        frequent_itemsets = list()
        for candidate in candidates:
            if candidate.get_supp() >= self.min_supp:
                frequent_itemsets.append(candidate)
                self.freq_isets.append(candidate) # Add FI of length 1 as FIs

        return frequent_itemsets

    # I'm not sure if it's working properly, yet.
    def run_declat(self, P):
        candidates = list()
        for i in range(0, len(P)):
            candidates_i = list()
            for j in range(i+1, len(P)):
                r = FI(P[i].get_itemset().union(P[j].get_itemset()))
                r.difflist = r.difflist.union(self.calc_difflists(P[i], P[j]))
                r.supp = (P[i].get_supp() - len(r.difflist))
                if r.get_supp() >= self.min_supp:
                    candidates_i.append(r)
                    if r not in self.freq_isets:
                        self.freq_isets.append(r)
            if len(candidates_i) > 0:
                candidates.append(candidates_i)
        for i in range(len(candidates)):
            self.run_declat(candidates[i])

    # Rediscretization of words. Print and save to text file discovered FIs
    def save_fis(self):
        fis = self.freq_isets
        array = list()
        for fi in fis:
            setx = list()
            for item in fi.get_itemset():
                for key in self.data.dictionary.keys():
                    if item == self.data.dictionary[key]:
                        setx.append(key)
            if [fi.supp, setx] not in array:
                array.append([fi.supp, setx])

        with open(f"results/fis-{self.user}.txt", "w", encoding='utf-8') as file:
            for supp, setx in sorted(array, reverse=True):
                if self.show_supp:
                    file.write(f" --- Support: {supp} --- FI: {setx}\n")
                    print(f" --- Support: {supp} --- FI: {setx}")
                else:
                    file.write(f"FI: {setx}\n")
                    print(f"FI: {setx}")

        print(f"\nSAVED TO FILE \"results/fis-{self.user}.txt\"")

