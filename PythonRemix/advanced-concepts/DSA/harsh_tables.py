def hash_function(value):
    sum_of_chars = 0
    
    for char in value:
        sum_of_chars += ord(char)
        
    return sum_of_chars % 10


print("'Bob' has a hash code:", hash_function('Bob'))


my_list = []

for _ in range(100):
    my_list.append(None)
def add(name):
    index = hash_function(name)
    my_list[index] = name

add('Bob')
add('Pete')
add('Jones')
add('Lisa')
add('Siri')
print(my_list)

def contains(name):
    index = hash_function(name)
    return my_list[index] == name

print("'Xavier' is in the Hash Table:", contains('Xavier'))