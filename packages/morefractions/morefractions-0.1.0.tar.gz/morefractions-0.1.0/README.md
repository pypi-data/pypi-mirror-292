# morefractions
morefractions is a package with classes and functions for manipulating fractions.

## Installation
run the command `pip install -U morefractions`

## Docs

### Class `Fraction`
`class Fraction(numerator: int | float, denominator: int | float = 1)`

Returns a new Fraction with numerator `numerator` and denominator `denominator`.

#### Methods
morefractions.Fraction implements most methods found in section 3.3.8 of [this page](https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types), except for binary operations, such as `<<` or `~`.

Other methods include:

`Fraction.reciprocal() -> Fraction`

Returns the inverse of this Fraction (aka. 1 ÷ Fraction).

`Fraction.get_type() -> ("proper" | "improper" | "unit")`

Returns a string indicating whether this Fraction is a proper fraction, an improper fraction or a unit fraction.

### Functions
`is_like(x: Fraction, y: Fraction) -> bool`

Returns a boolean indicating whether x and y are like fractions.