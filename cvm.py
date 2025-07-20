import sys
import argparse
import random

# Κλάση κόμβου για το treap
class Node:
    def __init__(self, value=-1, priority=-1, left=-1, right=-1):
        self.value = value
        self.priority = priority
        self.left = left
        self.right = right

# Κλάση που υλοποιεί treap χρησιμοποιώντας πίνακα σταθερού μεγέθους
class TreapArray:
    def __init__(self, max_nodes):
        self.capacity = max_nodes
        self.tree = [Node() for _ in range(max_nodes)]
        for i in range(max_nodes - 1):
            self.tree[i].left = i + 1
        self.tree[-1].left = -1
        self.free_index = 0
        self.root_index = -1
        self.active_nodes = 0

    def allocate_node(self, value, priority):
        if self.free_index == -1:
            return -1
        index = self.free_index
        self.free_index = self.tree[index].left
        self.tree[index] = Node(value, priority, -1, -1)
        return index

    def release_node(self, index):
        self.tree[index].value = -1
        self.tree[index].priority = -1
        self.tree[index].left = self.free_index
        self.tree[index].right = -1
        self.free_index = index

    def merge_subtrees(self, left_idx, right_idx):
        if left_idx == -1:
            return right_idx
        if right_idx == -1:
            return left_idx
        if self.tree[left_idx].priority > self.tree[right_idx].priority:
            self.tree[left_idx].right = self.merge_subtrees(self.tree[left_idx].right, right_idx)
            return left_idx
        else:
            self.tree[right_idx].left = self.merge_subtrees(left_idx, self.tree[right_idx].left)
            return right_idx

    def split_tree(self, root_idx, key):
        if root_idx == -1:
            return -1, -1
        if key <= self.tree[root_idx].value:
            left_split, right_split = self.split_tree(self.tree[root_idx].left, key)
            self.tree[root_idx].left = right_split
            return left_split, root_idx
        else:
            left_split, right_split = self.split_tree(self.tree[root_idx].right, key)
            self.tree[root_idx].right = left_split
            return root_idx, right_split

    def insert_node(self, current_root, new_idx):
        if current_root == -1:
            return new_idx
        if self.tree[new_idx].priority > self.tree[current_root].priority:
            left, right = self.split_tree(current_root, self.tree[new_idx].value)
            self.tree[new_idx].left = left
            self.tree[new_idx].right = right
            return new_idx
        elif self.tree[new_idx].value < self.tree[current_root].value:
            self.tree[current_root].left = self.insert_node(self.tree[current_root].left, new_idx)
        else:
            self.tree[current_root].right = self.insert_node(self.tree[current_root].right, new_idx)
        return current_root

    def find(self, current_idx, key):
        while current_idx != -1:
            current_val = self.tree[current_idx].value
            if current_val == key:
                return current_idx
            current_idx = self.tree[current_idx].left if key < current_val else self.tree[current_idx].right
        return -1

    def remove(self, current_idx, key):
        if current_idx == -1:
            return -1
        if self.tree[current_idx].value == key:
            combined = self.merge_subtrees(self.tree[current_idx].left, self.tree[current_idx].right)
            self.release_node(current_idx)
            return combined
        elif key < self.tree[current_idx].value:
            self.tree[current_idx].left = self.remove(self.tree[current_idx].left, key)
        else:
            self.tree[current_idx].right = self.remove(self.tree[current_idx].right, key)
        return current_idx

    def max_priority(self):
        return self.tree[self.root_index].priority if self.root_index != -1 else 1.0

    def remove_by_priority(self, target_priority):
        def recurse(index):
            if index == -1:
                return -1, 0
            left_sub, left_removed = recurse(self.tree[index].left)
            right_sub, right_removed = recurse(self.tree[index].right)
            self.tree[index].left = left_sub
            self.tree[index].right = right_sub
            if self.tree[index].priority == target_priority:
                self.release_node(index)
                return self.merge_subtrees(left_sub, right_sub), left_removed + right_removed + 1
            return index, left_removed + right_removed

        self.root_index, total_removed = recurse(self.root_index)
        return total_removed

# Εκτέλεση αλγορίθμου Compressed Value Mapping
def cvm_algorithm(storage_limit, input_file, random_seed=None):
    if random_seed is not None:
        random.seed(random_seed)

    treap = TreapArray(storage_limit)
    count = 0
    prob = 1.0

    with open(input_file) as file:
        for line in file:
            value = int(line.strip())
            if treap.find(treap.root_index, value) != -1:
                treap.root_index = treap.remove(treap.root_index, value)
                count -= 1

            rand_prob = random.random()
            if rand_prob <= prob:
                idx = treap.allocate_node(value, rand_prob)
                if idx == -1:
                    continue
                treap.root_index = treap.insert_node(treap.root_index, idx)
                count += 1
                if count >= storage_limit:
                    prob = treap.max_priority()
                    removed_count = treap.remove_by_priority(prob)
                    count -= removed_count

    estimated = int(count / prob)
    print(estimated)

# Entry point του προγράμματος
def main():
    parser = argparse.ArgumentParser(description="Υπολογισμός μοναδικών στοιχείων με χρήση CVM και treap")
    parser.add_argument("-s", type=int, help="Τιμή seed για random (προαιρετικό)", default=None)
    parser.add_argument("size", type=int, help="Μέγιστο μέγεθος treap")
    parser.add_argument("filename", help="Αρχείο εισόδου με ακέραιους αριθμούς")
    args = parser.parse_args()

    cvm_algorithm(args.size, args.filename, args.s)

if __name__ == "__main__":
    main()
