from dEclat import *

def main():
    declat = dEclat("BBCWorld", 4)
    # fis = declat.P
    # for fi in fis:
    #     print(fi.get_items(), fi.supp, fi.difflist)
    # print(sorted(declat.data.database))
    # print(declat.data.get_unique_words())
    # print(declat.data.get_unique_numbers())
    # print(declat.data.dictionary)
    # print(declat.data.discretized_data)
    declat.run_declat(declat.P)
    declat.get_fis()

if __name__ == "__main__":
    main()
