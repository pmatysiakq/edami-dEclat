from dEclat import *
from Helpers import get_200_tweets


def main():

    # get_200_tweets("BBCWorld")
    # get_200_tweets("CNN")
    # get_200_tweets("elonmusk")
    # get_200_tweets("Meta")

    declat = dEclat(data_path=r"data/tweets-elonmusk.txt",
                    min_supp=10,
                    show_supp=True)

    declat.run_declat(save_fis=True,
                      out_name="output-elonmusk",
                      spmf_file=True,
                      spmf_name="spmf-transactions-elonmusk")


if __name__ == "__main__":
    main()
