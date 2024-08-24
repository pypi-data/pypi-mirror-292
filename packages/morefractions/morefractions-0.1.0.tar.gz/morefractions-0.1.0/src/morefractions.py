"""A package with classes and functions for manipulating fractions."""

from math import gcd as _gcd, lcm as _lcm, floor as _floor, ceil as _ceil

class Fraction:
    pass

class Fraction:
    """A class for representing rational numbers as the division of two quantities."""

    __slots__ = ("numerator", "denominator")

    def __init__(self, numerator: int | float, denominator: int | float = 1):
        self.numerator = numerator
        """The numerator of this Fraction."""
        self.denominator = denominator
        """The denominator of this Fraction."""

    def __setattr__(self, name, value):
        type_value = type(value)
        if type_value != int and type_value != float:
            raise TypeError("The '" + name + "' attribute should be an int or float")
        try:
            if name == "denominator":
                if value < 0:
                    super().__setattr__("numerator", -self.numerator)
                    value *= -1
                elif value == 0:
                    super().__setattr__("numerator", 0)
                    value = 1
            if name == "numerator":
                super().__setattr__("numerator", value)
            else:
                super().__setattr__("denominator", value)
            if (name == "numerator" and type_value == float and self.denominator) or (name == "denominator" and (type(self.numerator) == float or type_value == float)):
                len_n, len_d = 0, 0
                if str(self.numerator).find(".") != -1:
                    len_n = len(str(self.numerator).split(".")[1])
                if str(self.denominator).find(".") != -1:
                    len_d = len(str(self.denominator).split(".")[1])
                inverse_int = eval("1e+" + str(max(len_n, len_d)))
                super().__setattr__("numerator", int(self.numerator * inverse_int))
                super().__setattr__("denominator", int(self.denominator * inverse_int))
            gcd_of_terms = _gcd(self.numerator, self.denominator)
            super().__setattr__("numerator", self.numerator // gcd_of_terms)
            super().__setattr__("denominator", self.denominator // gcd_of_terms)
        except (AttributeError):
            pass

    def __str__(self):
        return str(self.numerator) + "/" + str(self.denominator)
    
    def __repr__(self):
        return "Fraction(" + str(self.numerator) + ", " + str(self.denominator) + ")"
    
    def __int__(self):
        if self.numerator >= 0:
            return _floor(self)
        else:
            return _ceil(self)

    def __float__(self):
        return self.numerator / self.denominator
    
    def __index__(self):
        return int(self)
    
    def __trunc__(self):
        return int(self)
    
    def __add__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        lcm_of_d = _lcm(self.denominator, other.denominator)
        return Fraction(self.numerator * lcm_of_d / self.denominator + other.numerator * lcm_of_d / other.denominator, lcm_of_d)

    __radd__ = __add__
    
    def __sub__(self, other: int | float | Fraction) -> Fraction:
        return self + -other
    
    def __rsub__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        return other - self
    
    def __mul__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        return Fraction(self.numerator * other.numerator, self.denominator * other.denominator)
    
    __rmul__ = __mul__

    def __truediv__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        return self * other.reciprocal()
    
    def __rtruediv__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        self_rec = self.reciprocal()
        return Fraction(self_rec.numerator * other.numerator, self_rec.denominator * other.denominator)
    
    def __floordiv__(self, other: int | float | Fraction):
        return Fraction(_floor(self / other), 1)
    
    def __rfloordiv__(self, other: int | float | Fraction):
        return Fraction(_floor(other / self), 1)
    
    def __mod__(self, other: int | float | Fraction):
        return (self / other - int(self / other)) * other
    
    def __rmod__(self, other: int | float | Fraction):
        return (other / self - int(other / self)) * self
    
    def __divmod__(self, other: int | float | Fraction):
        return (self // other, self % other)
    
    def __rdivmod__(self, other: int | float | Fraction):
        return (other // self, other % self)

    def __pow__(self, other: int | float | Fraction) -> Fraction:
        other = float(other)
        if other == 0:
            return Fraction(1, 1)
        elif other < 0:
            return self.reciprocal() ** (-other)
        else:
            return Fraction(self.numerator ** other, self.denominator ** other)
        
    def __rpow__(self, other: int | float | Fraction):
        float_self = float(self)
        if type(other) != Fraction:
            other = Fraction(other)
        if self == 0:
            return Fraction(1, 1)
        elif self < 0:
            return other.reciprocal() ** (-self)
        else:
            return Fraction(other.numerator ** float_self, other.denominator ** float_self)
    
    def __neg__(self):
        return Fraction(-self.numerator, self.denominator)
    
    def __pos__(self):
        return self
    
    def __abs__(self):
        return Fraction(abs(self.numerator), self.denominator)
    
    def __round__(self, ndigits):
        return round(float(self), ndigits)
    
    def __floor__(self) -> int:
        return self.numerator // self.denominator
    
    def __ceil__(self):
        return _ceil(self.numerator / self.denominator)
    
    def __lt__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        lcm_of_d = _lcm(self.denominator, other.denominator)
        return self.numerator * lcm_of_d / self.denominator < other.numerator * lcm_of_d / other.denominator
        
    def __gt__(self, other: int | float | Fraction):
        if type(other) != Fraction:
            other = Fraction(other)
        lcm_of_d = _lcm(self.denominator, other.denominator)
        return self.numerator * lcm_of_d / self.denominator > other.numerator * lcm_of_d / other.denominator
    
    def __le__(self, other: int | float | Fraction):
        return not self > other
    
    def __ge__(self, other: int | float | Fraction):
        return not self < other
    
    def __eq__(self, other):
        if type(other) != Fraction:
            other = Fraction(other)
        return self.numerator == other.numerator and self.denominator == self.denominator
    
    def __ne__(self, other):
        return not self == other

    def reciprocal(self):
        """Returns the inverse of this Fraction."""
        return Fraction(self.denominator, self.numerator)
    
    def get_type(self):
        """Returns a string indicating whether this Fraction is a proper fraction, an improper fraction or a unit fraction."""
        if self.numerator < self.denominator:
            return "proper"
        elif self.numerator > self.denominator:
            return "improper"
        else:
            return "unit"
    
def is_like(x: Fraction, y: Fraction):
    """Returns a boolean indicating whether x and y are like fractions."""
    if type(x) != Fraction:
        raise TypeError("The x parameter should be a Fraction")
    elif type(y) != Fraction:
        raise TypeError("The y parameter should be a Fraction")
    return Fraction(x).denominator == Fraction(y).denominator
