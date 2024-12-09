import matplotlib.pyplot as plt
from matplotlib.ticker import LogFormatter, ScalarFormatter

file_name = "bench.data"
number_of_words = []
times = []

with open(file_name, "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) >= 2:
            number_of_words.append(int(parts[0]))
            times.append(int(parts[1]))

plt.figure(figsize=(10, 6))
plt.plot(number_of_words, times, marker="o", linestyle="-", label="Execution Time")
plt.title("Execution Time per Target number of words")
plt.xlabel("Number of words")
plt.ylabel("Time (ms)")

plt.yscale("log")
plt.gca().yaxis.set_major_formatter(ScalarFormatter())

plt.grid(True)
plt.legend()

output_image = "execution_time_chart.png"
plt.savefig(output_image)
print(f"Chart saved as {output_image}")
