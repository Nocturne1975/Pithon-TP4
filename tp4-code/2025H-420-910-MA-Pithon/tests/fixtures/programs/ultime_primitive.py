nums = [1, 2, 3, 4, 5]
total = 0

for n in range(len(nums)):
    if nums[n] % 2 ==0:
        continue
    total = total + nums[n]

print("Somme des impairs:", total)

#Comparaisons

a = 10
b = 5
print(a > b)
print(a < b)
print(a == b)
print(a != b)
print(a >= b)
print(a <= b)

#Manipulations des chaines

s = "pithon"
print (upper(s))
print(str(len(s)) + " lettres")

# Liste des tuples

t = (1, 2)
l = [3, 4]
print(concat(t, tuple(l)))
print(append(nums, 6))
print(head(nums))
print(tail(nums))
