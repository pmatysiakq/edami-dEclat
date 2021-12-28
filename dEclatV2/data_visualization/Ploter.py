import matplotlib.pyplot as plt
import networkx as nx

def load_experiment_data(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        lines = file.readlines()
        fields = lines[0].strip("\n").split(",")

        supports, times, memory_usage, dis_counts = [], [], [], []
        values = []
        for i in range(1, len(lines)):
            single_experiment = lines[i].strip("\n").split(",")
            values.append(single_experiment)
        for val in values:
            supports.append(float(val[0])*100)
            times.append(float(val[1]))
            memory_usage.append(int(val[2]))
            dis_counts.append(int(val[4]))
        print(memory_usage)
    return supports, times, memory_usage, dis_counts


def load_fis_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        fis = []
        for line in lines:
            line = line.split(" ")
            fi = []
            for item in line:
                if "#SUP" in item:
                    break
                fi.append(item)
            fis.append(fi)
    return fis


def plot_supports_memory(declat_file_path, imprv_file_path=""):
    """
    Draw plot f(x) = y

    Where:
        * x - Min Support
        * y - Memory usage
    """
    x1, _, y1, _ = load_experiment_data(declat_file_path)
    plt.scatter(x1, y1, label="Basic dEclat")
    if imprv_file_path != "":
        x2, _, y2, _ = load_experiment_data(imprv_file_path)
        plt.scatter(x2, y2, label="Improved dEclat", marker="*")

    plt.title("Memory usage ( Min Support )")
    plt.xlabel("Min Support [%]")
    plt.ylabel("Memory [bytes]")
    plt.legend()
    plt.show()


def plot_supports_time(declat_file_path, imprv_file_path=""):
    """
        Draw plot f(x) = y

        Where:
            * x - Min Support
            * y - Time
        """
    x1, y1, _, _ = load_experiment_data(declat_file_path)
    plt.scatter(x1, y1, label="Basic dEclat")
    if imprv_file_path != "":
        x2, y2, _, _ = load_experiment_data(imprv_file_path)
        plt.scatter(x2, y2, label="Improved dEclat", marker="*")

    plt.title("Time ( Min Support )")
    plt.xlabel("Min Support [%]")
    plt.ylabel("Time [seconds]")
    plt.legend()
    plt.show()


def plot_supports_dis_couts(declat_file_path, imprv_file_path=""):
    """
        Draw plot f(x) = y

        Where:
            * x - Min Support
            * y - Frequent Item-sets count
        """
    x1, _, _, y1 = load_experiment_data(declat_file_path)
    plt.scatter(x1, y1, label="Basic dEclat")
    if imprv_file_path != "":
        x2, _, _, y2 = load_experiment_data(imprv_file_path)
        plt.scatter(x2, y2, label="Improved dEclat", marker="*")

    plt.title("Frequent Itemsets ( Min Support )")
    plt.xlabel("Min Support [%]")
    plt.ylabel("Frequent Itemsets [-]")
    plt.legend()
    plt.show()


def plot_hasse():
    """
    Draw "hasse-like" graph.
    :return:
    """
    nodes = load_fis_from_file("../output/output-experiment-2-0.1-words.txt")

    G = nx.DiGraph()
    for node in nodes:
        G.add_node(str(node))
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if len(nodes[i]) == len(nodes[j]):
                continue
            elif len(nodes[i]) < len(nodes[j]):
                ok = True
                for item in nodes[i]:
                    if item not in nodes[j]:
                        ok = False
                        break
                if ok and abs(len(nodes[i]) - len(nodes[j])) == 1:
                    G.add_edge(str(nodes[i]), str(nodes[j]), length=2)
            else:
                ok = True
                for item in nodes[j]:
                    if item not in nodes[i]:
                        ok = False
                        break
                if ok and abs(len(nodes[i]) - len(nodes[j])) == 1:
                    G.add_edge(str(nodes[j]), str(nodes[i]), length=2)
    pos = nx.spiral_layout(G)
    nx.draw(G, pos, with_labels=True, connectionstyle='arc3, rad = 0.3')
    plt.show()


if __name__ == "__main__":
    declat_file = "../results/trump-experiment.csv"
    imprv_declat_file = "../results/trump-experiment-imprv.csv"

    plot_supports_memory(declat_file)
    plot_supports_time(declat_file)
    plot_supports_dis_couts(declat_file)

    plot_supports_memory(declat_file, imprv_declat_file)
    plot_supports_time(declat_file, imprv_declat_file)
    plot_supports_dis_couts(declat_file, imprv_declat_file)

    plot_hasse()
"../results/trump-experiment.csv"