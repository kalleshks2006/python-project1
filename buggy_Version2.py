# Example buggy code: removing items while iterating (can skip elements)
def remove_negatives(nums):
    for i, n in enumerate(nums):
        if n < 0:
            nums.pop(i)
    return nums

if __name__ == "__main__":
    print(remove_negatives([1, -2, -3, 4, -5]))  # unexpected output