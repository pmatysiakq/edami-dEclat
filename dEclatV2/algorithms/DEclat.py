from dEclatV2.db.TransactionDatabase import *
import time, math, tracemalloc

class DEclat:

    def __init__(self):
        self.minsup_relative: int
        self.database: TransactionDatabase
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.frequent_itemsets = []
        self.itemset_count = 0
        self.BUFFER_SIZE = 2000
        self.itemset_buffer = []
        self.show_transaction_ids = False
        self.max_itemset_size = 99999
        self.output_file = None
        self.peak_memory = None

    def run_algorithm(self, output: str, database: TransactionDatabase, minsupp: float):
        """

        :param output:
        :param database:
        :param minsupp:
        :return: (start_time, end_time, memory, database.size, fi.size)
        """
        self.output_file = open(output, "w")
        self.itemset_count = 0
        self.database = database
        self.start_timestamp = time.time()
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
        self.end_timestamp = time.time()
        self.output_file.close()

        _, self.peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return self.start_timestamp, self.end_timestamp, self.peak_memory, self.database.size, len(frequent_items)

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
                tidset_IJ = self.perform_AND(tidset_I, len(tidset_I), tidset_J, len(tidset_J))

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

                    tidset_IJ = self.perform_AND(tidset_I, support_I, tidset_J, support_J)
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

    def calculate_support(self, length_of_X: int, support_prefix: int, tidsetX: set):
        if length_of_X == 1:
            return len(tidsetX)
        else:
            return support_prefix - len(tidsetX)

    def perform_AND_first_time(self, tidset_I: set, support_I: int, tidset_J: set, support_J: int):
        diffset_IJ = set()

        for tid in tidset_I:
            if tid not in tidset_J:
                diffset_IJ.add(tid)
        return diffset_IJ

    def perform_AND(self, tidset_I: set, support_I: int, tidset_J: set, support_J: int):
        diffsetIJ = set()

        for tid in tidset_J:
            if tid not in tidset_I:
                diffsetIJ.add(tid)
        return diffsetIJ

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
        self.output_file.write("\n")

    def print_stats(self):
        print("\n=============  dECLAT Based on SPMF Java implemetation - STATS =============")
        temp = self.end_timestamp - self.start_timestamp
        print(f" Transactions count from database: {self.database.size}")
        print(f" Frequent itemsets count: {self.itemset_count}")
        print(f" Total time ~ {temp * 100} ms")
        print(f" Maximum memory usage: {self.peak_memory * 0.000001} mb")
        print("===========================================================================")

    def perform_experiment(self):
        # Define different min_sup values
        sup_values = [0.1, 0.08, 0.06, 0.04, 0.03, 0.02, 0.01, 0.009, 0.008, 0.007, 0.006, 0.005]
        # Create file to save results
        results = open("../results/trump-experiment.csv", "w", encoding="utf-8")
        # Indicate input database file and create new database instance
        input = "../input_data/trump-transactions.txt"
        database = TransactionDatabase(file_path=input)
        # describe values in csv file
        results.write("min_sup,total_time,peak_memory,db_size,fis_count")
        # For each support value, run declat algorithm and save results to the scv file
        for sup in sup_values:
            output = f"../output/output-experiment-2-{sup}.txt"
            start_time, end_time, memory, db_size, fi_count = self.run_algorithm(output=output, database=database, minsupp=sup)
            total_time = end_time - start_time
            results.write(f"\n{sup},{total_time},{memory},{db_size},{fi_count}")
            database.translate_integers_into_words(file_path=output)
        results.close()


if __name__ == "__main__":
    # # We define path to the input file
    # input = "../input_data/elonmusk-transactions.txt"
    # # We define path to the output file
    # output = "../output/output-experiment-1.txt"
    # # We set-up min-supp parameter - 5%
    # min_supp = 0.05
    # # We create TransactionDatabase instance using input file
    # database = TransactionDatabase(file_path=input)
    #
    # # We create dEclat instance
    # declat = DEclat()
    # # We run algorithm for specified parameters
    # declat.run_algorithm(output=output, database=database, minsupp=min_supp)
    # # We print out statistics
    # declat.print_stats()
    # # Additionally, we translate found frequent item-sets to the actual words
    # database.translate_integers_into_words(file_path=output)

    declat = DEclat()
    declat.perform_experiment()