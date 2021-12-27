from dEclatV2.db.TransactionDatabase import *
import time, math, tracemalloc


class Eclat:

    def __init__(self):
        self.minsup_relative: int
        self.database: TransactionDatabase
        self.start_time_stamp = 0
        self.endTime = 0
        self.frequent_itemsets = []
        self.itemset_count = 0
        self.BUFFER_SIZE = 2000
        self.itemset_buffer = []
        self.show_transaction_ids = False
        self.max_itemset_size = 99999
        self.output_file = None
        self.peak_memory = None

    def run_algorithm(self, output: str, database: TransactionDatabase, minsupp: float):
        self.output_file = open(output, "w")
        self.itemset_count = 0
        self.database = database
        self.start_time_stamp = time.time()
        self.minsup_relative = int(math.ceil(minsupp * database.size))

        tracemalloc.start()

        # for each item | Only when Triangular Matrix Optimization is used
        _, map_item_count = self.calculate_support_single_items(database)

        # Create the list of single items
        frequent_items = []

        # for each item
        for key in map_item_count.keys():
            # get tie tidset of that item
            tidset = map_item_count[key]
            # get the support of that item
            support = len(tidset)
            item = key
            if support >= self.minsup_relative and self.max_itemset_size >= 1:
                frequent_items.append(item)
                self.save_single_item(item, tidset, len(tidset))

        # TODO check if it's okay. It may need lambda or sth.
        # self.frequentItemsets.sort()

        # Now we will combine each pair of signle items to generate equivalence classes
        # of 2-item-sets
        if self.max_itemset_size >= 2:
            for i in range(len(frequent_items)):
                item_I = frequent_items[i]
                tidset_I = map_item_count[item_I]
                support_I = len(tidset_I)

                # List of integers
                equivalence_class_I_items = []
                # List of sets
                equivalence_class_I_tidsets = []

                for j in range(i+1, len(frequent_items)):
                    item_J = frequent_items[j]
                    tidset_J = map_item_count[item_J]
                    support_J = len(tidset_J)

                    tidset_IJ = self.perform_AND_first_time(tidset_I, support_I, tidset_J, support_J)

                    if self.calculate_support(2, support_I, tidset_IJ) >= self.minsup_relative:
                        equivalence_class_I_items.append(item_J)
                        equivalence_class_I_tidsets.append(tidset_IJ)
                if len(equivalence_class_I_items) > 0:
                    try:
                        self.itemset_buffer[0] = item_I
                    except:
                        self.itemset_buffer.append(0)
                        self.itemset_buffer[0] = item_I
                    self.process_equivalence_class(self.itemset_buffer, 1, support_I,
                                                   equivalence_class_I_items, equivalence_class_I_tidsets)
        self.endTime = time.time()
        self.output_file.close()

        _, self.peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return self.frequent_itemsets

    def process_equivalence_class(self, prefix: [], prefix_length: int, support_prefix: int,
                                  equivalence_class_items: [], equivalence_class_tidsets: []):
        length = prefix_length + 1
        if len(equivalence_class_items) == 1:
            item_I = equivalence_class_items[0]
            tidset_I_items = equivalence_class_tidsets[0]

            support = self.calculate_support(length, support_prefix, tidset_I_items)
            self.save(prefix, prefix_length, item_I, tidset_I_items, support)
            return

        if len(equivalence_class_items) == 2:
            item_I = equivalence_class_items[0]
            tidset_I = equivalence_class_tidsets[0]
            support_I = self.calculate_support(length, support_prefix, tidset_I)
            self.save(prefix, prefix_length, item_I, tidset_I, support_I)

            item_J = equivalence_class_items[1]
            tidset_J = equivalence_class_tidsets[1]
            support_J = self.calculate_support(length, support_prefix, tidset_J)
            self.save(prefix, prefix_length, item_J, tidset_J, support_J)

            if prefix_length+2 <= self.max_itemset_size:
                tidset_IJ = self.perform_AND_first_time(tidset_I, len(tidset_I), tidset_J, len(tidset_J))

                support_IJ = self.calculate_support(length, support_I, tidset_IJ)
                if support_IJ >= self.minsup_relative:
                    new_prefix_length = prefix_length+1
                    try:
                        prefix[prefix_length] = item_I
                    except Exception:
                        prefix.append(0)
                        prefix[prefix_length] = item_I

                    self.save(prefix, new_prefix_length, item_J, tidset_IJ, support_IJ)
            return

        for i in range(len(equivalence_class_items)):
            suffix_I = equivalence_class_items[i]
            tidset_I = equivalence_class_tidsets[i]
            support_I = self.calculate_support(length, support_prefix, tidset_I)
            self.save(prefix, prefix_length, suffix_I, tidset_I, support_I)

            if prefix_length+2 <= self.max_itemset_size:
                equivalence_class_I_suffix_items = []
                equivalence_I_tidsets = []

                for j in range(i+1, len(equivalence_class_items)):
                    suffix_J = equivalence_class_items[j]
                    tidset_J = equivalence_class_tidsets[j]
                    support_J = self.calculate_support(length, support_prefix, tidset_J)

                    tidset_IJ = self.perform_AND_first_time(tidset_I, support_I, tidset_J, support_J)
                    support_IJ = self.calculate_support(length, support_I, tidset_IJ)
                    if support_IJ >= self.minsup_relative:
                        equivalence_class_I_suffix_items.append(suffix_J)
                        equivalence_I_tidsets.append(tidset_IJ)
                if len(equivalence_class_I_suffix_items) > 0:
                    try:
                        prefix[prefix_length] = suffix_I
                    except Exception:
                        prefix.append(0)
                        prefix[prefix_length] = suffix_I
                    new_prefix_length = prefix_length+1

                    self.process_equivalence_class(prefix, new_prefix_length, support_I, equivalence_class_I_suffix_items, equivalence_I_tidsets)

    def calculate_support(self, length_of_X: int, support_prefix: int, tidsetI: set):
        return len(tidsetI)

    def perform_AND_first_time(self, tidset_I: set, support_I: int, tidset_J: set, support_J: int):
        tidset_IJ = set()

        if support_I > support_J:
            for tid in tidset_J:
                if tid in tidset_I:
                    tidset_IJ.add(tid)
        else:
            for tid in tidset_I:
                if tid in tidset_J:
                    tidset_IJ.add(tid)

        return tidset_IJ

    def save_single_item(self, item, tidset, support):
        self.itemset_count += 1
        self.output_file.write(f"{item} #SUP: {support}")
        # for tid in tidset:
        #     self.output_file.write(" " + str(tid))
        self.output_file.write("\n")

    def calculate_support_single_items(self, database: TransactionDatabase):
        max_item_id = 0
        map_item_count = dict()
        for i in range(database.size):
            transaction = database.transactions[i]
            for item in transaction:
                try:
                    setx = map_item_count[item]
                except Exception:
                    map_item_count[item] = set()
                    setx = map_item_count[item]
                if len(setx) == 0:
                    setx = set()
                    map_item_count[item] = setx
                    if item > max_item_id:
                        max_item_id = item
                setx.add(i)

        return max_item_id, map_item_count

    def save(self, prefix: [], prefix_length: int, suffix_item: int, tidset: set, support: int):
        self.itemset_count += 1
        for i in range(prefix_length):
            item = prefix[i]
            self.output_file.write(str(item) + " ")
        self.output_file.write(str(suffix_item))
        self.output_file.write(" #SUP: " + str(support))
        # for tid in tidset:
        #     self.output_file.write(" " + str(tid))
        #     print(" " + str(tid), end="")
        self.output_file.write("\n")

    def print_stats(self):
        print("\n=============  ECLAT Based on SPMF Java implemetation - STATS =============")
        temp = self.endTime - self.start_time_stamp
        print(f" Transactions count from database: {self.database.size}")
        print(f" Frequent itemsets count: {self.itemset_count}")
        print(f" Total time ~ {temp * 100} ms")
        print(f" Maximum memory usage: {self.peak_memory * 0.000001} mb")
        print("===========================================================================")


if __name__ == "__main__":
    input = "../input_data/elonmusk-transactions.txt"
    # input = "../input_data/covid-transactions.txt"
    # input = "../input_data/trump-transactions.txt"
    output = "../output/output-eclat.txt"

    # This parameter indicated percent of transactions. Possible values: (0, 1)
    min_supp = 0.01


    database = TransactionDatabase(file_path=input)

    eclat = Eclat()
    eclat.run_algorithm(output=output, database=database, minsupp=min_supp)
    eclat.print_stats()

    database.translate_integers_into_words(file_path=output)