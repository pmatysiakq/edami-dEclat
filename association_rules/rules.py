from itertools import permutations


def read_fi_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        fis = []
        for line in lines:
            line = line.split(" ")
            fi = []
            for item in line:
                item = item.replace('\n', '')
                if "#SUP" in item:
                    continue
                fi.append(item)
            support = int(item)
            fis.append((fi[:-1], support))
    return fis


def create_rules(itemsets, min_confidence=0.5):
    max_fis_cnt = -1
    for fis, _ in itemsets:
        max_fis_cnt = max(max_fis_cnt, len(fis)) #checking how many items are in iremset and finds the  max number of item (longest) in each itemset
    # make dictionary with keys as string with items separated by space and values as support
    itemsets_dict = {" ".join(fi): sup for fi, sup in itemsets}
    print(itemsets_dict)
    max_fises = [] # list of the longest items
    for fis, support in itemsets: # adding to list
        if len(fis) == max_fis_cnt:
            max_fises.append(fis)
    rules = []
    for fis in max_fises: # itering each elements with  biggest itemsets, checking all permutations
        for fis_perm in permutations(fis): #iterating over permutation over itemsets
            for ii in range(1, len(fis_perm)):  # iterating over dividing where rules were created
                left_side = fis[:ii]
                right_side = fis[ii:]
                left_support = itemsets_dict[" ".join(left_side)]
                full_support = itemsets_dict[" ".join(fis)]
                confidence = full_support/left_support # calculating confidence
                if confidence > min_confidence:
                    rules.append((tuple(left_side), tuple(right_side), confidence)) #each list element left side right side and confidence
    return list(set(rules)) # delete duplications


def save_rules_to_file(rules, output):
    with open(output, "w") as file:
        for rule_data in rules:
            left_side = " ".join(rule_data[0])
            right_side = " ".join(rule_data[1])
            file.write(f"{left_side} -> {right_side}: {rule_data[2]}\n")


itemsets = read_fi_file("../dEclatV2/output/output-experiment-imprv-0.009-words.txt")
rules = create_rules(itemsets)
save_rules_to_file(rules, "rules-imprv-0.009.csv")
