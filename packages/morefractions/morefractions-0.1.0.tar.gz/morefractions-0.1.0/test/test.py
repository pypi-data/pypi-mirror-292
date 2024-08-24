from morefractions import *
from time import time

# create variables
# ================

frac1 = Fraction(17, 0.0626)
frac2 = Fraction(1204.5, -1650)
float1 = 0.65
float2 = 0.5517
float3 = 3.85
float4 = 4.24
start_time = time()

# begin tests
# ===========

assert str(frac1) == "85000/313", "test failed: str(frac1) != \"85000/313\""
assert repr(frac1) == "Fraction(85000, 313)", "test failed: repr(frac1) != Fraction(85000, 313)"
assert int(frac1) == 271, "test failed: int(frac1) != 271"
assert float(frac1) == 271.5654952076677, "test failed: float(frac1) != 271.5654952076677"
assert str(frac2) == "-73/100", "test failed: str(frac2) != \"-73/100\""
assert repr(frac2) == "Fraction(-73, 100)", "test failed: repr(frac2) != Fraction(-73, 100)"
assert int(frac2) == 0, "test failed: int(frac2) != 0"
assert float(frac2) == -0.73, "test failed: float(frac2) != -0.73"
assert str(frac1 + float1) == "1704069/6260", "test failed: str(frac1 + float1) != \"1704069/6260\""
assert str(frac2 + float2) == "-1783/10000", "test failed: str(frac2 + float2) != \"-1783/10000\""
assert str(frac1 + frac2) == "8477151/31300", "test failed: str(frac1 + frac2) != \"8477151/31300\""
assert str(frac1 - float1) == "1695931/6260", "test failed: str(frac1 - float1) != \"1695931/6260\""
assert str(frac2 - float2) == "-12817/10000", "test failed: str(frac2 - float2) != \"-12817/10000\""
assert str(float1 - frac1) == "-1695931/6260", "test failed: str(float1 - frac1) != \"-1695931/6260\""
assert str(float2 - frac2) == "12817/10000", "test failed: str(float2 - frac2) != \"12817/10000\""
assert str(frac1 - frac2) == "8522849/31300", "test failed: str(frac1 - frac2) != \"8522849/31300\""
assert str(frac1 * float1) == "55250/313", "test failed: str(frac1 * float1) != \"55250/313\""
assert str(frac2 * float2) == "-402741/1000000", "test failed: str(frac2 * float2) != \"-402741/1000000\""
assert str(frac1 * frac2) == "-62050/313", "test failed: str(frac2 * float2) != \"-62050/313\""
assert str(frac1 / float1) == "1700000/4069", "test failed: str(frac1 / float1) != \"1700000/4069\""
assert str(frac2 / float2) == "-7300/5517", "test failed: str(frac2 / float2) != \"-7300/5517\""
assert str(float1 / frac1) == "4069/1700000", "test failed: str(float1 / frac1) != \"4069/1700000\""
assert str(float2 / frac2) == "-5517/7300", "test failed: str(float2 / frac2) != \"-5517/7300\""
assert str(frac1 / frac2) == "-8500000/22849", "test failed: str(frac1 / frac2) != \"-8500000/22849\""
assert str(frac1 // float1) == "417/1", "test failed: str(frac1 // float1) != \"417/1\""
assert str(frac2 // float2) == "-2/1", "test failed: str(frac2 // float2) != \"-2/1\""
assert str(float1 // frac1) == "0/1", "test failed: str(float1 // frac1) != \"0/1\""
assert str(float2 // frac2) == "-1/1", "test failed: str(float2 // frac2) != \"-1/1\""
assert str(frac1 // frac2) == "-373/1", "test failed: str(frac1 // frac2) != \"-373/1\""
assert str(frac1 % float1) == "3227/6260", "test failed: str(frac1 % \float1) != \"3227/6260\""
assert str(frac2 % float2) == "-1783/10000", "test failed: str(frac2 % \float2) != \"-1783/10000\""
print("Tests finished with no fails in " + str(time() - start_time) + " seconds.")