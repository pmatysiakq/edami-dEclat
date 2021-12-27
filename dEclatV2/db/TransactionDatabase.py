import json

class TransactionDatabase:
    """
    Represents transactional database. This database is provided as input for dEclat/Eclat algorithm.
    """

    def __init__(self, file_path):
        self.items = []
        self.transactions = []
        self.dictionary = dict()
        self.parse_data_from_file(file_path=file_path)
        self.sort_data()
        self.size = len(self.transactions)


    def parse_data_from_file(self, file_path):
        """
        As input we provide text file which contains 2 parts.
        1st part is transactional database line "==== DICTIONARY ===="
        indicates the end of DB. Then we provide dictionary which will
        be used to translate integer items into real words.
        :param file_path: Path to text file
        """
        with open(file_path, "r") as file:
            database = file.readlines()
        for line in database:
            # When we found this line, we know that we loaded all transactions
            # Last line is dictionary which will allow to translate integers
            # into real words
            if "==== DICTIONARY ====" in line:
                self.dictionary = json.loads(database[-1])
                return
            line = (line.strip()).split()
            transaction = []
            for item in line:
                if item not in transaction:
                    transaction.append(int(item))
            self.transactions.append(transaction)
            for item in transaction:
                if item not in self.items:
                    self.items.append(item)

    def sort_data(self):
        self.items.sort()
        for transaction in self.transactions:
            transaction.sort()

    def print_transactions(self):
        tid = 1
        print(f"{'tid':>4} {'transacton'}")
        for transaction in self.transactions:
            print(f"{tid:>3} {transaction}")
            tid += 1

    def print_items(self):
        print(f"ITEMS:", end=" ")
        for item in self.items:
            print(item, end=" ")
        print("\n\n")

    def get_items(self):
        return self.items

    def translate_integers_into_words(self, file_path):
        """
        Used to translate frequent item-sets indicated by integers
        into frequent item-sets which consists of real words
        :param file_path: Path to file, which is output of the algorithm
        :return: New text file with frequent item-sets
        """
        with open(file_path, "r", encoding="utf-8") as in_file:
            new_file_path = file_path[:-4] + "-words.txt"
            with open(new_file_path, "w", encoding="utf-8") as out_file:
                initial_lines = in_file.readlines()
                for line in initial_lines:
                    new_line = ""
                    line = line.split(" ")
                    for word in line:
                        if "#SUP" in word:
                            new_line += (word + " " + line[-1])
                            break
                        else:
                            new_line += self.dictionary[f"{word}"] + " "
                    out_file.write(new_line)
