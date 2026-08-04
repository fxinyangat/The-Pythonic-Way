# Buble sort
# Bubble Sort is an algorithm that sorts an array from the lowest value to the highest value.

unsorted_array = [4,3,6,23,5]


print("Before Sort: ", unsorted_array)

for round_num in range(len(unsorted_array)-1):
    print(f"Round: {round_num+1}")
    for i in range(len(unsorted_array)-1):
        
        x = i
        y = i+1
        if unsorted_array[x] > unsorted_array[y]:
            unsorted_array[x], unsorted_array[y] = unsorted_array[y],unsorted_array[x]
            
            
        print(f"Compare indexes {x}, {y}: {unsorted_array}")

            
        
        
print("After Sort: ", unsorted_array)

# Improvements to bubble sort: Some times the arrays may be already sorted, but it always runs n times. alwyas add a check to see if any swaps was made.


# Selection Sort
# The Selection Sort algorithm finds the lowest value in an array and moves it to the front of the array.

mylist = [64, 34, 25, 5, 22, 11, 90, 12]

n = len(mylist)
for i in range(n-1):
    min_index = i
    for j in range(i+1,n):
        if mylist[j] < mylist[min_index]:
            min_index = j
    min_value = mylist.pop(min_index)
    mylist.insert(i, min_value)
    
print(mylist)

# IMPROVING Selection sort. every time a value is popped or inserted, others 
# have to shift postions. best implement by just swapping than pop.



# QUICK SORT 
# is one of the fastest sorting algorithms.

# The Quicksort algorithm takes an array of values, chooses one of the values as the 'pivot' element, 
# and moves the other values so that lower values are on the left of the pivot element, and higher values 
# are on the right of it.

def quicksort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
        
    if low < high:
        # Partition the array and get the pivot index
        pivot_index = partition(arr, low, high)
        
        # Recursively sort elements before and after partition
        quicksort(arr, low, pivot_index - 1)
        quicksort(arr, pivot_index + 1, high)

def partition(arr, low, high):
    # Choose the last element as the pivot
    pivot = arr[high]
    i = low - 1  # Index of the smaller element
    
    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]  # Swap elements
            
    # Swap the pivot element with the greater element specified by i
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Example usage:
data = [24, 9, 2, 10, 4, 1, 5]
print("Original Array:", data)

quicksort(data)
print("Sorted Array:  ", data)
