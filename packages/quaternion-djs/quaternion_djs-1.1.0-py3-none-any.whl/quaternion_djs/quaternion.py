# Copyright (c) 2024 James Strudwick
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
"""The source code for the Quaternion class."""

from __future__ import annotations
import inspect
import sys

eps = sys.float_info.epsilon


class Quaternion:
    """A class to represent a Quaternion."""

    # TODO: Make full docstring, possibly wait until AutoDocstring gets updated?
    def __init__(
        self,
        x: int | float = 0,
        i: int | float = 0,
        j: int | float = 0,
        k: int | float = 0,
    ):
        """
        Create the Quaternion object.

        Parameters
        ----------
        x : int | float, optional
            The value for the x component, by default 0.
        i : int | float, optional
            The value for the i component, by default 0.
        j : int | float, optional
            The value for the j component, by default 0.
        k : int | float, optional
            The value for the k component, by default 0.

        Attributes
        ----------
        norm : float
            The norm of the constructed quaternion
        trace : float
                The trace of the constructed quaternion
        pure : bool
            A boolean to indicate if the constructed Quaternion is pure or not
        unit : bool
            A boolean to indicate if the constructed Quaternion is a unit or not

        Raises
        ------
        TypeError
            Is raised if any of the arguments are not an int or float.
        """
        # check input types
        for key, key_type in inspect.get_annotations(self.__init__).items():
            print(f"{key=}, {key_type=}")
            if not isinstance(locals()[key], eval(str(key_type))):
                raise TypeError(f"{key} must be {key_type}")

        self.x = x
        self.i = i
        self.j = j
        self.k = k
        self.norm = x**2 + i**2 + j**2 + k**2
        self.trace = 2 * self.x
        self.pure = abs(self.x) <= eps
        self.unit = abs(self.norm - 1) <= eps

    def _type_check(self, other: any):
        """
        Check if another provided object is an instance of this class.

        Parameters
        ----------
        other : any
            The other object to be checked.

        Raises
        ------
        NotImplementedError
            Is raised if the other object is not an instance of this class.
        """
        if not isinstance(other, type(self)):
            raise NotImplementedError(
                "unsupported operation for: "
                f"'{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __eq__(self, value: Quaternion) -> bool:
        """
        Check if this quaternion is equal to another.

        Parameters
        ----------
        value : Quaternion
            The other quaternion that this is compared against.

        Returns
        -------
        bool
            Return True if the two quaternions are equal and False if not.
        """
        # check that the other value is an appropriate type
        self._type_check(value)

        # perform equality check
        is_equal = (
            (abs(value.x - self.x) <= eps)
            and (abs(value.i - self.i) <= eps)
            and (abs(value.j - self.j) <= eps)
            and (abs(value.k - self.k) <= eps)
        )
        return is_equal

    def __str__(self) -> str:
        """
        Create the string representation of this quaternion.

        Returns
        -------
        str
            The string representation of the quaternion.
        """
        # return the string representing this quaternion
        return (
            f"{self.x}"
            f"{'+' if self.i >= 0 else ''}{self.i}i"
            f"{'+' if self.j >= 0 else ''}{self.j}j"
            f"{'+' if self.k >= 0 else ''}{self.k}k"
        )

    def __repr__(self) -> str:
        """
        Create the repr for this quaternion.

        Returns
        -------
        str
            The repr for this quaternion.
        """
        # Produce the repr
        return f"{type(self).__name__}(x={self.x}, i={self.i}, j={self.j}, k={self.k})"

    def __add__(self, other: Quaternion | int | float) -> Quaternion:
        """
        Add two quaternions together or a quaternion and a scalar.

        Parameters
        ----------
        other : Quaternion | int | float
            The other quaternion/scalar to be added.

        Returns
        -------
        Quaternion
            The resulting quaternion from the addition.
        """
        # if the other object is a scalar
        if isinstance(other, int | float):
            return type(self)(self.x + other, self.i, self.j, self.k)
        # check other is a Quaternion
        self._type_check(other)
        # Perform addition
        return type(self)(
            self.x + other.x, self.i + other.i, self.j + other.j, self.k + other.k
        )

    def __radd__(self, other: int | float) -> Quaternion:
        """
        Add from the right, for scalars only.

        Parameters
        ----------
        other : int | float
            The scalar this quaternion is being added to.

        Returns
        -------
        Quaternion
            The resulting quaternion.

        Raises
        ------
        NotImplementedError
            Is raised if the other is not a scalar.
        """
        # if other object is a scalar
        if isinstance(other, int | float):
            # invoke normal addition, as operation is commutative
            return self.__add__(other=other)
        else:
            raise NotImplementedError

    def __sub__(self, other: Quaternion | int | float) -> Quaternion:
        """
        Subtract two quaternions or a quaternion and a scalar.

        Parameters
        ----------
        other : Quaternion | int | float
            The other quaternion/scalar to be subtracted from this quaternion.

        Returns
        -------
        Quaternion
            The resulting quaternion.
        """
        # if the other object is a scalar
        if isinstance(other, int | float):
            return type(self)(self.x - other, self.i, self.j, self.k)

        # check other is a Quaternion
        self._type_check(other)
        # perform subtraction and return
        return type(self)(
            self.x - other.x, self.i - other.i, self.j - other.j, self.k - other.k
        )

    def __rsub__(self, other: int | float) -> Quaternion:
        """
        Sub from the right, for scalars only.

        Parameters
        ----------
        other : int | float
            The scalar this quaternion is being subtracted from.

        Returns
        -------
        Quaternion
            The resulting quaternion.

        Raises
        ------
        NotImplementedError
            Is raised if the other is not a scalar.
        """
        # if other object is a scalar
        if isinstance(other, int | float):
            # invoke subtraction, via negation and addition
            return (-1 * self) + other
        else:
            raise NotImplementedError

    def __mul__(self, other: Quaternion | int | float) -> Quaternion:
        """
        Multiply either two quaternions or quaternions & a scalar.

        Parameters
        ----------
        other : Quaternion | int | float
            The other quaternion to be multiplied with.

        Returns
        -------
        Quaternion
            The resulting quaternion.
        """
        # check if being multiplied by a scalar, if so quick multiply
        if isinstance(other, int | float):
            return Quaternion(
                other * self.x, other * self.i, other * self.j, other * self.k
            )
        # otherwise check other is a quaternion
        self._type_check(other)

        # perform x component calculation
        quaternion_x_component = Quaternion(
            self.x * other.x,
            self.x * other.i,
            self.x * other.j,
            self.x * other.k,
        )
        # perform i component calculation
        quaternion_i_component = Quaternion(
            -self.i * other.i,
            self.i * other.x,
            -self.i * other.k,
            self.i * other.j,
        )
        # perform j component calculation
        quaternion_j_component = Quaternion(
            -self.j * other.j,
            self.j * other.k,
            self.j * other.x,
            -self.j * other.i,
        )
        # perform k component calculation
        quaternion_k_component = Quaternion(
            -self.k * other.k,
            -self.k * other.j,
            self.k * other.i,
            self.k * other.x,
        )
        # combine and return
        return (
            quaternion_x_component
            + quaternion_i_component
            + quaternion_j_component
            + quaternion_k_component
        )

    def __rmul__(self, other: int | float) -> Quaternion:
        """
        Multiply from the right, only for scalars.

        Parameters
        ----------
        other : int | float
            The scalar to be multiplied with this quaternion.

        Returns
        -------
        Quaternion
            The resulting multiplication.

        Raises
        ------
        NotImplementedError
            Is raised if the other object is not a int or a float.
        """
        # check if scalar, if so do calculation
        if isinstance(other, int | float):
            return Quaternion(
                other * self.x, other * self.i, other * self.j, other * self.k
            )
        else:
            # otherwise raise error
            raise NotImplementedError

    def conjugate(self) -> Quaternion:
        """
        Produce the conjugate of the this quaternion.

        Returns
        -------
        Quaternion
            The corresponding conjugate quaternion.
        """
        # conjugate is ever non real part negated
        return Quaternion(self.x, -self.i, -self.j, -self.k)

    def inverse(self) -> Quaternion:
        """
        Produce the inverse of this quaternion.

        Returns
        -------
        Quaternion
            The inverse of this quaternion.
        """
        # return the inverse of this Quaternion
        return (1 / self.norm) * (self.conjugate())

    def __truediv__(self, other: Quaternion | int | float) -> Quaternion:
        """
        Return the results of dividing this Quaternion by another object.

        Parameters
        ----------
        other : Quaternion | int | float
            The object that is dividing this quaternion.

        Returns
        -------
        Quaternion
            The resulting quaternion.
        """
        # TODO: write test

        # check if being divide by a scalar, if so quick div
        if isinstance(other, int | float):
            return Quaternion(
                self.x / other, self.i / other, self.j / other, self.k / other
            )
        # otherwise check other is a quaternion
        self._type_check(other)

        # multiply this quaternion with the inverse of the other
        return self * other.inverse()

    def __rtruediv__(self, other: int | float) -> Quaternion:
        """
        Return the results of dividing another object by this quaternion.

        Parameters
        ----------
        other : int | float
            The other object that is being divided by this quaternion.

        Returns
        -------
        Quaternion
            The resulting quaternion.

        Raises
        ------
        NotImplementedError
            Is raised if the object being divided is not an int or a float
        """
        # TODO: write test

        # check if the other thing being divided is a scalar, if so do div
        if isinstance(other, int | float):
            return other * self.inverse()
        else:
            # otherwise raise error
            raise NotImplementedError
