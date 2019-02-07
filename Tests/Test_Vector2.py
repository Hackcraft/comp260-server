import sys
sys.path.append('..')

from Vector2 import Vector2

# Vectors can be created
assert Vector2(1,1) != None

# Create test vectors
test_vec1 = Vector2(1,1)
test_vec2 = Vector2(5,50)

# Vectors can be read
assert test_vec1.x == 1
assert test_vec1.y == 1

# Vectors can be added
assert (test_vec1 + test_vec2) == Vector2(6, 51)

# Vectors can be subtracted
assert (test_vec1 - test_vec2) == Vector2(-4, -49)

# Vectors can be compared
assert (test_vec1 == test_vec2) == False
assert (test_vec1 != test_vec2) == True

# Vectors can be printed
assert str(test_vec1) == "x: 1 y: 1" 
