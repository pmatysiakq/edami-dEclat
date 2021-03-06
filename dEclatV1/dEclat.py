from Data import *
from FI import *
from Helpers import calc_difflists


class dEclat:
    def __init__(self, data: Data, min_supp, show_supp=False, show_one_elem_fi=True):
        self.one_elem_fi = show_one_elem_fi
        self.data = data
        self.min_supp = min_supp
        self.freq_isets = list()
        self.initial_dataset = self.create_initial_itemsets()
        self.show_supp = show_supp

    # This method is slow, because it's burte-force. TODO
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
            if candidate.get_supp() > self.min_supp:
                frequent_itemsets.append(candidate)
                if self.one_elem_fi:
                    self.freq_isets.append(candidate) # Add FI of length 1 as FIs

        return frequent_itemsets

    def declat_algorithm(self, P):
        print("Start")
        T = list()
        for i in range(0, len(P)):
            new_P = list()
            for j in range(i+1, len(P)):
                r = FI((P[i].get_itemset()).union(P[j].get_itemset()))
                r.set_difflist((r.get_difflist()).union(calc_difflists(P[i], P[j])))
                r.set_supp(P[i].get_supp() - len(r.get_difflist()))
                if r.get_supp() > self.min_supp:
                    new_P.append(r)
                    if r not in self.freq_isets:
                        self.freq_isets.append(r)
            if len(new_P) > 0:
                T.append(new_P)
        for i in range(len(T)):
            self.declat_algorithm(T[i])
        print("END")

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
            file.write(f" -----------------------\n")
            file.write(f" --- min_supp = {self.min_supp} ---\n")
            file.write(f" --- total_fis = {len(array)} ---\n")
            file.write(f" -----------------------\n\n")
            for supp, setx in sorted(array, reverse=True):
                if self.show_supp:
                    file.write(f" #SUP: {supp} | #FI: {setx}\n")
                else:
                    file.write(f"#FI: {setx}\n")

        print(f"FOUND {len(array)} Frequent Itemsets")
        print(f"SAVED TO FILE \"results/fis-{file_name}.txt\"")

    def run_declat(self, save_fis=True, out_name="output", spmf_file=True, spmf_name="std_db.txt"):
        self.declat_algorithm(self.initial_dataset)
        if save_fis:
            self.save_fis(out_name)
        if spmf_file:
            self.data.save_db_in_standard_format(spmf_name)