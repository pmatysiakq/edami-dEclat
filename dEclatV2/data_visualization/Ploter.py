import matplotlib.pyplot as plt
import networkx as nx

def load_experiment_data():
    with open("../results/trump-experiment.csv", "r", encoding='utf-8') as file:
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

def plot_supports_memory():
    """
    Draw plot f(x) = y

    Where:
        * x - Min Support
        * y - Memory usage
    """
    x, _, y, _ = load_experiment_data()
    plt.scatter(x, y)
    plt.title("Memory usage ( Min Support )")
    plt.xlabel("Min Support [%]")
    plt.ylabel("Memory [bytes]")
    plt.show()

def plot_supports_time():
    """
        Draw plot f(x) = y

        Where:
            * x - Min Support
            * y - Time
        """
    x, y, _, _ = load_experiment_data()
    plt.scatter(x, y)
    plt.title("Time ( Min Support )")
    plt.xlabel("Min Support [%]")
    plt.ylabel("Time [seconds]")
    plt.show()

def plot_supports_dis_couts():
    """
        Draw plot f(x) = y

        Where:
            * x - Min Support
            * y - Frequent Item-sets count
        """
    x, _, _, y = load_experiment_data()
    plt.scatter(x, y)
    plt.title("Frequent Itemsets ( Min Support )")
    plt.xlabel("Min Support [%]")
    plt.ylabel("Frequent Itemsets [-]")
    plt.show()

def plot_hasse():
    """
    Draw "hasse-like" graph.
    :return:
    """
    nodes = load_fis_from_file("../output/output-experiment-2-0.04-words.txt")

    G = nx.DiGraph()
    for node in nodes:
        G.add_node(str(node))
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if len(nodes[i]) == len(nodes[j]):
                break
            elif len(nodes[i]) < len(nodes[j]):
                ok = True
                for item in nodes[i]:
                    if item not in nodes[j]:
                        ok = False
                        break
                if ok:
                    G.add_edge(str(nodes[i]), str(nodes[j]), length=2)
            else:
                ok = True
                for item in nodes[j]:
                    if item not in nodes[i]:
                        ok = False
                        break
                if ok:
                    G.add_edge(str(nodes[j]), str(nodes[i]), length=2)
    pos = nx.spiral_layout(G)
    nx.draw(G, pos, with_labels=True, connectionstyle='arc3, rad = 0.1')
    plt.show()


if __name__ == "__main__":
    # plot_supports_memory()
    # plot_supports_time()
    # plot_supports_dis_couts()

    plot_hasse()
