from dEclat import *
from Helpers import get_200_tweets


def main():

    # get_200_tweets("BBCWorld")
    # get_200_tweets("CNN")
    # get_200_tweets("elonmusk")
    # get_200_tweets("Meta")
    # get_200_tweets("troyhunt")

    declat = dEclat(data_path=r"data/tweets-Meta.txt",
                    min_supp=8,
                    show_supp=True)

    declat.run_declat(save_fis=True,
                      out_name="output-meta",
                      spmf_file=True,
                      spmf_name="spmf-transactions-meta")


if __name__ == "__main__":
    main()
