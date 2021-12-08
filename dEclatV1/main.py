from dEclat import *


def main():
    declat = dEclat(user="Meta", min_supp=20, show_supp=True)

    declat.run_declat(declat.initial_dataset)
    declat.save_fis()
    declat.data.save_db_in_standard_format()


if __name__ == "__main__":
    main()
