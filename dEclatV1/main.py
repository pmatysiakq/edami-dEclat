from dEclat import *
from Helpers import get_200_tweets


def main():

    # get_200_tweets("BBCWorld")
    # get_200_tweets("CNN")
    # get_200_tweets("elonmusk")
    # get_200_tweets("Meta")
    # get_200_tweets("troyhunt")

    declat = dEclat(data_path=r"data/combined.txt",
                    min_supp=10,
                    show_supp=True)

    declat.run_declat(save_fis=True,
                      out_name="output-combined",
                      spmf_file=True,
                      spmf_name="spmf-transactions-combined")


if __name__ == "__main__":
    main()
