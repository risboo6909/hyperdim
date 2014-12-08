# @Boris Tatarintsev
# mailto: ttyv00@gmail.com

# Exceptions hierarchy

# parent class for all exceptions
class ParentException:
    pass

# invert matrix doesn't exist
class InvertedUndetermined(ParentException):
    pass

# occours when sizes of two arguments dont match
class SizeMismatchException(ParentException):
    pass

# occours when wrong index was specified
class WrongIndexException(ParentException):
    pass

# you should know when this occours ;)
class NullPointerException(ParentException):
    pass

# occours when function gets an argument of incompatible type
class WrongTypeException(ParentException):
    pass

# illegal argument
class IllegalArgumentException(ParentException):
    pass

# wrong parent node
class WrongParentNode(ParentException):
    pass

# occours when projection matrix is not initialized
class ProjectionMatrixNotInitialized(ParentException):
    pass
