from dEclat import *


def main():
    declat = dEclat(user="Meta", min_supp=8, show_supp=True)

    declat.run_declat(declat.initial_dataset)
    declat.save_fis()


if __name__ == "__main__":
    main()
