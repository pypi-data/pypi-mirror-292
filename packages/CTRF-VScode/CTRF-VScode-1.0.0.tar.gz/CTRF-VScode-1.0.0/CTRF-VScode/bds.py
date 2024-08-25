
def minterm_now(tree, max_feature, max_value, node_max_class, n_classes):
    count = [0] * n_classes
    MinT = [[] for _ in range(n_classes)]
    C = [[] for _ in range(n_classes)]
    T = [[] for _ in range(n_classes)]
    MinF = [[] for _ in range(n_classes)]
    MinV = [[] for _ in range(n_classes)]

    # Loop over all nodes in the tree
    for x in range(len(tree)):
        if not max_value[x]:
            class_idx = node_max_class[x]
            count[class_idx] += 1

            # Get the minterm for the current node
            C[class_idx] = []
            if tree[x] % 2 == 1:
                T[class_idx].append(tree[x])
                W = tree[x]
                while W != 0:
                    if W % 2 == 1:
                        parent = (W - 1) // 2
                    else:
                        parent = (W - 2) // 2
                    W = parent
                    C[class_idx].append(parent)

            else:
                T[class_idx].append(tree[x])
                W = tree[x]
                while W != 0:
                    if W % 2 == 1:
                        parent = (W - 1) // 2
                    else:
                        parent = (W - 2) // 2
                    W = parent
                    C[class_idx].append(parent)

            if count[class_idx] > len(MinT[class_idx]):
                MinT[class_idx].append([])

            MinT[class_idx][count[class_idx] - 1] = C[class_idx][::-1]

            # Get the features and values for the minterm
            MinF[class_idx].append([])
            MinV[class_idx].append([])
            for i in range(len(MinT[class_idx][count[class_idx] - 1])):
                for j in range(len(tree)):
                    if MinT[class_idx][count[class_idx] - 1][i] == tree[j]:
                        MinF[class_idx][count[class_idx] - 1].append(max_feature[j])
                        MinV[class_idx][count[class_idx] - 1].append(max_value[j])
                    # Reverse the elements of the sublists of MinT, MinF, and MinV
            MinT[class_idx][count[class_idx] - 1].reverse()
            MinF[class_idx][count[class_idx] - 1].reverse()
            MinV[class_idx][count[class_idx] - 1].reverse()
    # Insert T values into MinT
    for i in range(n_classes):
        for j in range(len(T[i])):
            MinT[i][j].insert(0, T[i][j])
    return MinT, MinF, MinV, T
