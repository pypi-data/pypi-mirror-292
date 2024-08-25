
def some_function(x: int) -> int:
    """Adds 1 to the input.

    Args:
        x (int): Input number.

    Returns:
        int: Number incremented by 1.
    """

    return x + 1

class SomeClass:
    """Holds an integer.

    Args:
        x (int): Input number.
    """

    def __init__(self, x: int):
        self.x = x
    
    def increment(self) -> int:
        """Increments the integer by 1.

        Returns:
            int: Number incremented by 1.
        """

        return self.x + 1
    
    def decrement(self) -> int:
        """Decrements the integer by 1.

        Returns:
            int: Number decremented by 1.
        """

        return self.x - 1