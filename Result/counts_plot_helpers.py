def norm_counts(counts):
    sum_val = sum(counts.values())
    norm_dict = {k:(v/sum_val) for k, v in counts.items()}
    return norm_dict

def add_zero_values(counts, num_qubits):
    for i in range(2**num_qubits):
        bin_val = bin(i)[2:].zfill(num_qubits)
        if bin_val not in counts.keys():
            counts[bin_val] = 0

def combine_less_then(counts, min_val):
    _sum = 0
    for k, v in list(counts.items())[:]:
        if v < min_val:
            _sum += v
            del counts[k]

    counts["others"] = _sum