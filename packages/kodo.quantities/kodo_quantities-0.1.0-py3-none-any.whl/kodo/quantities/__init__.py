# Copyright 2024 Dom Sekotill <dom.sekotill@kodo.org.uk>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Types for representing physical quantities, which have a magnitude and a unit

Defining Units
--------------

Unit types for quantities are created by subclassing the `QuantityUnit` enum base:

>>> class Time(QuantityUnit):
...     MILLISECONDS = 1
...     SECONDS = 1000
...     MINUTES = 60 * SECONDS

>>> class Distance(QuantityUnit):
...     MILLIMETERS = 1
...     CENTIMETERS = 10 * MILLIMETERS
...     METERS = 100 * CENTIMETERS
...     KILOMETERS = 1000 * METERS
...     INCH = 24 * MILLIMETERS
...     HALF_INCH = INCH // 2  # Hey! Hands off
...     QUARTER_INCH = INCH // 4

The enum members form units of relative size to each other. They MUST be integers so
typically the smallest (highest precision) unit is `1` and the others are some multiple of
it. Note that the designated 'unit' can be changed without breaking dependant code (as long
as the code is using the quantities right).  In this case the unitary value is 0.5mm:

>>> class Distance(QuantityUnit):
...     MILLIMETERS = 2  # Scaled to allow SIXTEENTH_INCH to be an integer
...     # [...]
...     SIXTEENTH_INCH = 3  # 1/16″ is 1.5mm
...     INCH = 16 * SIXTEENTH_INCH

Although it would probably be easier to make the unitary value 0.1mm:

>>> class Distance(QuantityUnit):
...     MILLIMETERS = 10
...     # [...]
...     SIXTEENTH_INCH = 15
...     INCH = 16 * SIXTEENTH_INCH

In full:

>>> class Distance(QuantityUnit):
...     MILLIMETERS = 10
...     CENTIMETERS = 10 * MILLIMETERS
...     METERS = 100 * CENTIMETERS
...     KILOMETERS = 1000 * METERS
...     SIXTEENTH_INCH = 15
...     INCH = 16 * SIXTEENTH_INCH
...     HALF_INCH = 8 * SIXTEENTH_INCH
...     QUARTER_INCH = 4 * SIXTEENTH_INCH


Creating Physical Quantities
----------------------------

A physical quantity can be created using the matrix multiplication operator "@" with a
quantity unit, e.g. 2 seconds:

>>> quantity: Quantity[Time] = 2 @ Time.SECONDS

Quantities of the same type relate to one another as you would expect (parentheses for
clarity):

>>> assert (2 @ Time.SECONDS) == (2000 @ Time.MILLISECONDS)

Note that quantities are really just integers which, at runtime, have no additional
information attached to them. This means that Python will happily accept any `Quantity`
wherever it would accept an integer; however static type checkers such as MyPy will complain
about it, which is good as it is almost certainly a mistake to attempt to, for example, sum
time and distance quantities, or sum a quantity with an arbitrary value:

>>> meaningless_value = (2 @ Time.SECONDS) + (10 @ Distance.MILLIMETERS)

>>> # Depending on the declaration of Distance, 100 here could be interpreted by the
>>> # runtime as 100m, 100cm, 100/24″, or anything else...
>>> unreliable_value = (2 @ Distance.METERS) + 100

Multiplying quantities with other quantities, even of the same type, would produce
a different unit, which is not supported.  (However, it is conceivable that it could
be supported in the future.) The following will also fail static type checks:

>>> area = (2 @ Distance.METERS) * (2 @ Distance.METERS)  # 4.0m²
>>> speed = (100 @ Distance.METERS) / (1 @ Time.SECONDS)  # 100m/s


Using Physical Quantities
-------------------------

At some point quantities will need to be passed through an interface of some sort where the
unit information will be lost.  Such interfaces will define a single unit they accept; for
instance `time.sleep()` requires an argument in seconds.  Upon reaching such an interface,
quantities can be stripped of their scalar types and converted to the required unit with the
right bit-shift operator ">>" or floor division operator "//":

>>> delay = 2 @ Time.MINUTES
>>> # [...]
>>> import time
>>> time.sleep(delay >> Time.SECONDS)

With the ">>" operator the type of the resulting value is always a `float` and
will only be precise up to the highest precision unit for a defined `QuantityUnit` type (the
unit with a magnitude of `1`, which need not be explicitly defined).

With the "//" operator the resulting type will be `int`, with whatever loss of precision
that implies.

>>> delay = 3600 @ Time.MILLISECONDS
>>> # [...]
>>> time.sleep(delay // Time.SECONDS)  # Will sleep for 3 seconds


Operations on Quantities
------------------------

At runtime all quantities are a subclass of integers, so all operations that work on
integers will work[^*] however type checkers only allow a subset of operations with certain
types.

[^*]: One small difference is multiplication by floats and division by float or int, which
would normally return floats, returns a new integer quantity.  However division by
a quantity returns a float.  Don't worry too much about this.

Quantities may be added to or subtracted from other quantities with the same unit, returning
a new quantity of that unit:

>>> assert (2 @ Time.SECONDS) + (500 @ Time.MILLISECONDS) == (2500 @ Time.MILLISECONDS)

They may be scaled by multiplying (*) and dividing (/) by unitless numeric values _only_,
resulting in a new quantity of the same unit.  Note however that when scaling down there
will probably be some rounding loss depending on the precision of the unit.

>>> assert (2 @ Time.SECONDS) * 2 == (4 @ Time.SECONDS)
>>> assert (2 @ Time.SECONDS) / 2 == (1 @ Time.SECONDS)
>>> assert (2 @ Time.SECONDS) / 3 == (666 @ Time.MILLISECONDS)  # Rounded down to whole milliseconds

In addition you may use _floor_ division (//) on quantities with another quantity of the
same unit to calculate how many times it can be divided into that size.  Note when using
single units this is equivalent to converting to an untyped value of those units, so this is
the same as using the floor division operator with a unit value.

>>> assert (10 @ Time.SECONDS) // (2 @ Time.SECONDS) == 5
>>> assert (10 @ Time.SECONDS) // (1 @ Time.SECONDS) == 10
>>> assert (10 @ Time.SECONDS) // Time.SECONDS == 10  # Unit may be used as a convenience

To find the remainder after floor division, the modulus operator (%) returns a new quantity:

>>> assert (10 @ Time.SECONDS) % (3 @ Time.SECONDS) == (1 @ Time.SECONDS)
>>> assert (3.6 @ Time.SECONDS) % Time.SECONDS == (600 @ Time.MILLISECONDS)

This pairs well with the shift and floor division operators to get the modulus values as
floats or ints of a particular unit:

>>> assert (3.6 @ Time.SECONDS) % Time.SECONDS >> Time.SECONDS == 0.6
>>> assert (3.6 @ Time.SECONDS) % Time.SECONDS // Time.MILLISECONDS == 600


Choice of Operators
-------------------

The operators for constructing ("@") and deconstructing (">>") quantities may seem a bit
odd, given that what they actually do is multiply and divide the values. They were chosen to
be visually distinct from other multiplication and division operations on quantities and
scalar units.

The matrix multiplication operator therefore replaces the scalar multiplication operator,
while the shift operator, which looks arrow-like, is used to convert to the indicated unit.
i.e.:

>>> # quantity  (converted to)  units
>>> delay             >>        Time.SECONDS
3.6
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from typing import Generic
from typing import Self
from typing import TypeVar
from typing import overload

U = TypeVar("U", bound="QuantityUnit")


if TYPE_CHECKING:
	class Quantity(Generic[U]):
		"""
		A physical quantity of a given unit type 'U'
		"""

		def __init__(self, value: int|float|Quantity[U], /) -> None: ...

		# Adding two quantities creates a new quantity
		def __add__(self, other: Quantity[U], /) -> Quantity[U]: ...

		# Subtracting a quantity from another creates a new quantity
		def __sub__(self, other: Quantity[U], /) -> Quantity[U]: ...

		# Quantities can be multiplied by unitless values to produce a new quantity
		def __mul__(self, other: int|float, /) -> Quantity[U]: ...

		# Quantities can be divided by unitless values to produce a new quantity
		def __truediv__(self, other: int|float, /) -> Quantity[U]: ...

		# Quantities can be divided by (into) quantities of the same unit to produce
		# a unitless value (the number of whole divisions of the quantity)
		def __floordiv__(self, other: Quantity[U], /) -> int: ...

		# The remainder of a floor division with another quantity
		def __mod__(self, other: Quantity[U], /) -> Quantity[U]: ...

else:
	# Although the runtime implementation does not use TypeVars, it is still generic to
	# allow type subscripting.

	class Quantity(int, Generic[U]):
		"""
		A physical quantity of a given unit type 'U'
		"""

		def __mul__(self, other: int|float, /) -> Quantity:
			return Quantity(other.__rmul__(self))

		def __truediv__(self, other: int|float, /) -> Quantity:
			if isinstance(other, Quantity):
				return super().__truediv__(other)
			return Quantity(other.__rtruediv__(self))


class QuantityUnit(enum.Enum):
	"""
	Enum base class for units
	"""

	if TYPE_CHECKING:
		@property
		def value(self) -> int: ...  # noqa: D102

	def __rmatmul__(self, scalar: float|int) -> Quantity[Self]:
		return Quantity(self.value * scalar)

	def __rrshift__(self, quantity: Quantity[Self]) -> float:
		return self.value.__rtruediv__(quantity)  # type: ignore[operator]

	def __rfloordiv__(self, quantity: Quantity[Self]) -> int:
		return quantity // self.value  # type: ignore[operator,no-any-return]

	def __rmod__(self, quantity: Quantity[Self]) -> Quantity[Self]:
		return Quantity(quantity % self.value)  # type: ignore[operator]
