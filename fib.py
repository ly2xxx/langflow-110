def fibonacci(n):
    if n <= 0:
        return []
    result = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        next_num = a + b
        a, b = b, next_num
    return result

# Example usage:
n = int(input("Enter the number of terms: "))
sequence = fibonacci(n)
print(f"The first {n} Fibonacci numbers are: {sequence}")