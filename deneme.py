import pandas as pd


a = list(range(1,10))
b = list(range(11,20))
c = list(range(21,30))


d = pd.DataFrame({'a' : a,
                  'b' : b,
                  'c' : c})

i1 = d.columns.get_loc('a')
i2 = d.columns.get_loc('b')
i3 = d.columns.get_loc('c')



print(d)
print(f'len : {len(d)}')


print(i1)
print(i2)
print(i3)
