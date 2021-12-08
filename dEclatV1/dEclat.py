from Data import *
from FI import *
from Helpers import calc_difflists


class dEclat:
    def __init__(self, data_path, min_supp, show_supp=False):
        self.data = Data(data_path)
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

    def remove_non_frequent(self, candidates):
        frequent_itemsets = list()
        for candidate in candidates:
            if candidate.get_supp() >= self.min_supp:
                frequent_itemsets.append(candidate)
                self.freq_isets.append(candidate) # Add FI of length 1 as FIs

        return frequent_itemsets

    # I'm not sure if it's working properly, yet.
    def declat_algorithm(self, P):
        candidates = list()
        for i in range(0, len(P)):
            candidates_i = list()
            for j in range(i+1, len(P)):
                r = FI(P[i].get_itemset().union(P[j].get_itemset()))
                r.difflist = r.difflist.union(calc_difflists(P[i], P[j]))
                r.supp = (P[i].get_supp() - len(r.difflist))
                if r.get_supp() >= self.min_supp:
                    candidates_i.append(r)
                    if r not in self.freq_isets:
                        self.freq_isets.append(r)
            if len(candidates_i) > 0:
                candidates.append(candidates_i)
        for i in range(len(candidates)):
            self.declat_algorithm(candidates[i])

    # Rediscretization of words. Print and save to text file discovered FIs
    def save_fis(self, file_name):
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

        with open(f"results/fis-{file_name}.txt", "w", encoding='utf-8') as file:
            file.write(f" --- min_supp = {self.min_supp} ---\n")
            file.write(f" --- total_fis = {len(array)} ---\n\n")
            for supp, setx in sorted(array, reverse=True):
                if self.show_supp:
                    file.write(f" --- Supp: {supp} --- FI: {setx}\n")
                    print(f" --- Supp: {supp} --- FI: {setx}")
                else:
                    file.write(f"FI: {setx}\n")
                    print(f"FI: {setx}")

        print(f"\nSAVED TO FILE \"results/fis-{file_name}.txt\"")

    def run_declat(self, save_fis=True, out_name="output", spmf_file=True, spmf_name="std_db.txt"):
        self.declat_algorithm(self.initial_dataset)
        if save_fis:
            self.save_fis(out_name)
        if spmf_file:
            self.data.save_db_in_standard_format(spmf_name)