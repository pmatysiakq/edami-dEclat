from dEclatV2.db.TransactionDatabase import *
import time, math, tracemalloc

class ImprvDEclat:

    def __init__(self):
        self.minsup_relative: int
        self.database: TransactionDatabase
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.itemset_count = 0
        self.itemset_buffer = []
        self.max_itemset_size = 99999
        self.output_file = None
        self.peak_memory = None

    # Annotation: Frequent Itemsets of length 1 and 2 always calculate using tidsets
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

        # Returns a map of tidsets for each item
        _, map_item_count = self.calculate_support_single_items(database)

        # Create the list of single items
        frequent_items = []

        # Find frequent items of length 1 and save them to the file.
        for key in map_item_count.keys():
            # get tidset of that item
            tidset = map_item_count[key]
            # get the support of that item
            support = len(tidset)
            if support >= self.minsup_relative and self.max_itemset_size >= 1:
                frequent_items.append(key)
                self.save_single_item(key, tidset, len(tidset))

        # TODO Sort frequent items based on support - important?
        # frequent_items.sort()

        # Combine each pair of single items to generate
        # equivalence classes of 2-itemsets
        if self.max_itemset_size >= 2:
            # For each item "i" in frequent_items
            for i in range(len(frequent_items)):
                item_I = frequent_items[i]
                tidset_I = map_item_count[item_I]
                support_I = len(tidset_I)

                # List of integers
                equivalence_class_I_items = []
                # List of sets
                equivalence_class_I_tidsets = []

                # For each item "j", where j > i
                for j in range(i+1, len(frequent_items)):
                    item_J = frequent_items[j]
                    tidset_J = map_item_count[item_J]
                    support_J = len(tidset_J)

                    # Finds tidset of items IJ - for FIs of length 2 always use tidsets.
                    tidset_IJ = self.perform_AND_eclat(tidset_I, support_I, tidset_J, support_J)

                    if self.calculate_support_eclat(2, support_I, tidset_IJ) >= self.minsup_relative:
                        # We add only item_J to the equivalence class, but item "i" is provided as
                        # a priefix so we know item_IJ
                        equivalence_class_I_items.append(item_J)
                        equivalence_class_I_tidsets.append(tidset_IJ)
                if len(equivalence_class_I_items) > 0:
                    try:
                        self.itemset_buffer[0] = item_I
                    except:
                        self.itemset_buffer.append(0)
                        self.itemset_buffer[0] = item_I
                    # Here we process frequent itemsets which are greater than 2
                    # This method is called recursively
                    self.process_equivalence_class(self.itemset_buffer, 1, support_I, equivalence_class_I_items,
                                                   equivalence_class_I_tidsets, declat=False, declat_first_time=False)
        self.end_timestamp = time.time()
        self.output_file.close()

        _, self.peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return self.start_timestamp, self.end_timestamp, self.peak_memory, self.database.size, len(frequent_items)

    def process_equivalence_class(self, prefix: [], prefix_length: int, support_prefix: int,
                                  equivalence_class_items: [], equivalence_class_tidsets: [], declat: bool, declat_first_time: bool):
        """
        Process frequent itemsets of length greater than 2.

        For each item in previous equivalence class create new equivalence class
        and process resursively until all frequent itemsets are found.

        :param prefix: Item "i" which is prefix for items "j"
        :param prefix_length: Length of the prefix
        :param support_prefix: support of item "i"
        :param equivalence_class_items: Frequent Items "j" for specified prefix
        :param equivalence_class_tidsets: Tidsets of found FIs for specified prefix
        :param declat: Indicates if diffsets are provided (True) or tidsets (False)
        :param declat_first_time: Indicates if we should change tid -> diff in this iteration
        """
        length = prefix_length + 1
        # Save information if we already changed tidsets to diffsets
        is_declat = declat
        # Initialise variable - if changing condition is met for more than 50% of
        # newly created items - set this variable to True and use diffsets
        change_to_declat = False
        # Counter for items for which changing condition is met
        condition_met = 0

        if len(equivalence_class_items) == 1:
            item_I = equivalence_class_items[0]
            tidset_I_items = equivalence_class_tidsets[0]
            if declat:
                support = self.calculate_support_declat(length, support_prefix, tidset_I_items)
            else:
                support = self.calculate_support_eclat(length, support_prefix, tidset_I_items)

            self.save(prefix, prefix_length, item_I, tidset_I_items, support)
            return

        if len(equivalence_class_items) == 2:
            item_I = equivalence_class_items[0]
            tidset_I = equivalence_class_tidsets[0]

            if declat:
                support_I = self.calculate_support_declat(length, support_prefix, tidset_I)
            else:
                support_I = self.calculate_support_eclat(length, support_prefix, tidset_I)

            self.save(prefix, prefix_length, item_I, tidset_I, support_I)

            item_J = equivalence_class_items[1]
            tidset_J = equivalence_class_tidsets[1]

            if declat:
                support_J = self.calculate_support_declat(length, support_prefix, tidset_J)
            else:
                support_J = self.calculate_support_eclat(length, support_prefix, tidset_J)

            self.save(prefix, prefix_length, item_J, tidset_J, support_J)

            if prefix_length+2 <= self.max_itemset_size:
                if declat_first_time:
                    tidset_IJ = self.perform_AND_first_time_declat(tidset_I, len(tidset_I), tidset_J, len(tidset_J))
                    support_IJ = self.calculate_support_declat(length, support_I, tidset_IJ)
                elif declat:
                    tidset_IJ = self.perform_AND_declat(tidset_I, len(tidset_I), tidset_J, len(tidset_J))
                    support_IJ = self.calculate_support_declat(length, support_I, tidset_IJ)
                else:
                    tidset_IJ = self.perform_AND_eclat(tidset_I, len(tidset_I), tidset_J, len(tidset_J))
                    support_IJ = self.calculate_support_eclat(length, support_I, tidset_IJ)


                if support_IJ >= self.minsup_relative:
                    new_prefix_length = prefix_length+1
                    try:
                        prefix[prefix_length] = item_I
                    except Exception:
                        prefix.append(0)
                        prefix[prefix_length] = item_I

                    self.save(prefix, new_prefix_length, item_J, tidset_IJ, support_IJ)
            return

        # If there are more than 2 frequent items do this.
        for i in range(len(equivalence_class_items)):
            suffix_I = equivalence_class_items[i]
            tidset_I = equivalence_class_tidsets[i]
            if declat:
                support_I = self.calculate_support_declat(length, support_prefix, tidset_I)
            else:
                support_I = self.calculate_support_eclat(length, support_prefix, tidset_I)

            self.save(prefix, prefix_length, suffix_I, tidset_I, support_I)

            if prefix_length+2 <= self.max_itemset_size:
                equivalence_class_I_suffix_items = []
                equivalence_I_tidsets = []

                for j in range(i+1, len(equivalence_class_items)):
                    suffix_J = equivalence_class_items[j]
                    tidset_J = equivalence_class_tidsets[j]
                    if declat:
                        support_J = self.calculate_support_declat(length, support_prefix, tidset_J)
                    else:
                        support_J = self.calculate_support_eclat(length, support_prefix, tidset_J)

                    if declat_first_time:
                        tidset_IJ = self.perform_AND_first_time_declat(tidset_I, support_I, tidset_J, support_J)
                        support_IJ = self.calculate_support_declat(length, support_I, tidset_IJ)
                    elif declat:
                        tidset_IJ = self.perform_AND_declat(tidset_I, support_I, tidset_J, support_J)
                        support_IJ = self.calculate_support_declat(length, support_I, tidset_IJ)
                    else:
                        tidset_IJ = self.perform_AND_eclat(tidset_I, support_I, tidset_J, support_J)
                        support_IJ = self.calculate_support_eclat(length, support_I, tidset_IJ)

                        # If changing condition is met for processed tidset increment `condition_met` variable.
                        # Do only if diffsets are not already active.
                        if self.check_condition_single_tidset(supPXY=support_IJ, supPX=support_J) and not declat:
                            condition_met += 1

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

                    # Check if we should change tidsets to diffsets
                    # If diffsets are already used do nothing (declat=True), if more than 50% of items met
                    # the changing condition, then convert tidsets to diffsets in the next iteration
                    if declat:
                        pass
                    elif condition_met >= 0.5 * len(equivalence_class_items):
                        is_declat = True
                        change_to_declat = True

                    self.process_equivalence_class(prefix, new_prefix_length, support_I, equivalence_class_I_suffix_items, equivalence_I_tidsets, is_declat, change_to_declat)

    def calculate_support_declat(self, length_of_X: int, support_prefix: int, tidsetX: set):
        if length_of_X == 1:
            return len(tidsetX)
        else:
            return support_prefix - len(tidsetX)

    def calculate_support_eclat(self, length_of_X: int, support_prefix: int, tidsetI: set):
        return len(tidsetI)

    def perform_AND_first_time_declat(self, tidset_I: set, support_I: int, tidset_J: set, support_J: int):
        diffset_IJ = set()

        for tid in tidset_I:
            if tid not in tidset_J:
                diffset_IJ.add(tid)
        return diffset_IJ

    def perform_AND_declat(self, diffset_I: set, support_I: int, diffset_J: set, support_J: int):
        diffsetIJ = set()

        for tid in diffset_J:
            if tid not in diffset_I:
                diffsetIJ.add(tid)
        return diffsetIJ

    def perform_AND_eclat(self, tidset_I: set, support_I: int, tidset_J: set, support_J: int):
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

    def check_condition_single_tidset(self, supPXY, supPX):
        if supPXY >= supPX:
            return True
        else:
            return False

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
        sup_values = [0.1, 0.08, 0.06, 0.04, 0.03, 0.02, 0.01, 0.009, 0.008, 0.007, 0.006, 0.005, 0.004]
        # Create file to save results
        results = open("../results/trump-experiment-imprv.csv", "w", encoding="utf-8")
        # Indicate input database file and create new database instance
        input = "../input_data/trump-transactions.txt"
        database = TransactionDatabase(file_path=input)
        # describe values in csv file
        results.write("min_sup,total_time,peak_memory,db_size,fis_count")
        # For each support value, run declat algorithm and save results to the scv file
        for sup in sup_values:
            output = f"../output/output-experiment-imprv-{sup}.txt"
            start_time, end_time, memory, db_size, fi_count = self.run_algorithm(output=output, database=database, minsupp=sup)
            total_time = end_time - start_time
            results.write(f"\n{sup},{total_time},{memory},{db_size},{fi_count}")
            database.translate_integers_into_words(file_path=output)
        results.close()


if __name__ == "__main__":

    # Experiment 2
    imprv_declat = ImprvDEclat()
    imprv_declat.perform_experiment()
