def palindrome(input):
    temp = str(input)
    # new_string = temp[::-1]
    # new_string = []

    # for l in reversed(input):
    #     new_string.push(l)

    # new_string = ''.join(new_string)

    if temp == new_string:
        return True

    return False


print(palindrome(123))
print(palindrome(121))
print(palindrome(-121))
