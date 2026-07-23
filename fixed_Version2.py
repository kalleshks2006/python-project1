# Fixed version: build a new list (safe and simple)
def remove_negatives(nums):
    return [n for n in nums if n >= 0]

if __name__ == "__main__":
    print(remove_negatives([1, -2, -3, 4, -5]))  # -> [1, 4]