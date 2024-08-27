class Array:
    def __init__(self, *elements):
        self.elements = list(elements)

    def __repr__(self):
        return f"Array({self.elements})"

    def length(self):
        return len(self.elements)

    def append(self, value):
        self.elements.append(value)

    def pop(self):
        return self.elements.pop()

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
