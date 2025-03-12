"""application.scalars.long"""

__all__ = ['scalar']

from ariadne import ScalarType

## Define a scalar type for long integers
scalar = ScalarType('Long')
