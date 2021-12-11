from dEclat import *
from Helpers import get_200_tweets_by_user, search_tweets_by_tags
import tracemalloc, time

def generate_data():
    pass
    # get_200_tweets("BBCWorld")
    # get_200_tweets("CNN")
    # get_200_tweets("elonmusk")
    # get_200_tweets("Meta")
    # get_200_tweets("troyhunt")

    # words = ["covid", "vaccine", "covid-19", "quarantine", "restrictions", "phizer", "moderna", "astrazeneca",
    #          "fake covid", "wuhan", "coronavirus", "health", "pandemic", "virus", "corona", "stayhome", "lockdown",
    #          "unvaccinated", "omicron", "sars-cov-2", "death", "antibodies", "plandemic"]
    #
    # search_tweets_by_tags(words, "covid")

    # words = ["covid fake plandemic", "covid-19 planned government", "fake covid sard-cov-2 pandemic", "covid-19 safe propaganda",
    #          "sars covid", "covid flatten earth", "virus omicron holidays"]
    # search_tweets_by_tags(words, "covid")


def main(data_path, min_supp, show_supp, show_one_elem_fi, save_fis, out_name, spmf_file, spmf_name):

    tracemalloc.start()
    start_time = time.time()

    declat = dEclat(data_path=data_path,
                    min_supp=min_supp,    # elements, not percentage
                    show_supp=show_supp,
                    show_one_elem_fi=show_one_elem_fi)

    declat.run_declat(save_fis=save_fis,
                      out_name=out_name,
                      spmf_file=spmf_file,
                      spmf_name=spmf_name)

    end_time = time.time()
    _, peak_memory_usage = tracemalloc.get_traced_memory()
    execution_time = end_time - start_time
    tracemalloc.stop()

    return peak_memory_usage, execution_time


if __name__ == "__main__":

    generate_data()

    memory, exec_time = main(data_path=r"data/db-covid.txt",
                             min_supp=20,
                             show_supp=True,
                             show_one_elem_fi=True,
                             save_fis=True,
                             out_name="output-covid",
                             spmf_file=True,
                             spmf_name="spmf-transactions-covid")

    print(f"Maximum memory usage: {memory * 0.000001} Megabytes.\nTotal time ~ {exec_time} seconds.")