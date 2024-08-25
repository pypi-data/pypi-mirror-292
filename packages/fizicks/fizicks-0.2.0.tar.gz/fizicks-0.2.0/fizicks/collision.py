from typing import TYPE_CHECKING, Union

from fizicks.data import Vector
from fizicks.universe import Universe

if TYPE_CHECKING:
    from fizicks.matter import Matter


class Collision:
    """
    Handles collision detection and resolution between objects.

    For boundary collisions, the object is teleported to the other
    side of the border.

    For object collisions, the objects are resolved using elastic
    collision formulas.

    Methods
    -------
    detect(object1: Matter, object2: Union[Matter, Universe]) -> bool
        Detects if a collision has occurred between an object and another
        object or the universe border.
    resolve(object: Matter, universe: Universe, other: Matter = None) -> None
        Resolves the collision between two objects using elastic
        collision formulas.
    """

    @staticmethod
    def detect(
        object: "Matter", other: Union["Matter", "Universe"], debug: bool = False
    ) -> bool:
        """
        Detects if a collision has occurred between an object and another object
        or the universe border.

        Parameters:
        -----------
        object : Matter
            The object to check for collision.
        other : Union[Matter, Universe]
            Either another Matter object to check for collision with object1,
            or a Universe object to check for border collision.

        Returns:
        --------
        bool
            True if a collision is detected, False otherwise.
        """
        if isinstance(other, Universe):

            if debug:
                debug_log(
                    f"Checking for border collision with {other.__class__.__name__}",
                    object,
                )
            return Collision._detect_border(object, other, debug=debug)
        else:
            if debug:
                debug_log(
                    f"Checking for object collision with {other.__class__.__name__}",
                    object,
                )
            return Collision._detect_objects(object, other, debug=debug)

    @staticmethod
    def resolve(
        object: "Matter", other: Union["Matter", "Universe"], debug: bool = False
    ) -> None:
        """
        Resolves the collision between two objects using elastic collision formulas.

        Parameters
        ----------
        object : Matter
            The object to resolve the collision for.
        universe : Universe
            The universe within which the collision is taking place.
        other : Union[Matter, Universe]
            The other object involved in the collision.
        """
        if isinstance(other, Universe):
            if debug:

                debug_log(
                    f"Resolving border collision with {other.__class__.__name__}",
                    object,
                )
            Collision._resolve_border(object, other, debug=debug)
        else:
            if debug:
                debug_log(
                    f"Resolving object collision with {other.__class__.__name__}",
                    object,
                )
            Collision._resolve_objects(object, other, debug=debug)

    @staticmethod
    def _detect_objects(
        object1: "Matter", object2: "Matter", debug: bool = False
    ) -> bool:
        """
        Detects if a collision has occurred between two objects.

        Parameters
        ----------
        object1 : Matter
            The first object.
        object2 : Matter
            The second object.

        Returns
        -------
        bool
            True if a collision has occurred, False otherwise.
        """
        if debug:
            debug_log(
                f"Step {object1.time}: Detecting collision between {object1.description()} and {object2.description()}",
                object1,
            )
        distance = (object1.position - object2.position).magnitude()
        return distance < (object1.radius + object2.radius)

    @staticmethod
    def _resolve_objects(
        object1: "Matter", object2: "Matter", debug: bool = False
    ) -> None:
        """
        Resolves the collision between two objects using elastic collision formulas.

        Parameters
        ----------
        object1 : Matter
            The first object.
        object2 : Matter
            The second object.
        """
        if debug:
            debug_log(
                f"Step {object1.time}: Resolving collision between {object1.description()} and {object2.description()}",
                object1,
            )
        # Calculate the normal and tangential vectors
        normal = (object2.position - object1.position).normalize()
        tangent = Vector(-normal.y, normal.x)

        # Decompose velocities into normal and tangential components
        v1n = normal.dot(object1.velocity)
        v1t = tangent.dot(object1.velocity)
        v2n = normal.dot(object2.velocity)
        v2t = tangent.dot(object2.velocity)  # Add this line to define v2t

        # Update normal components using 1D elastic collision formulas
        total_mass = object1.mass + object2.mass
        v1n_after = (
            (object1.mass - object2.mass) * v1n + 2 * object2.mass * v2n
        ) / total_mass
        v2n_after = (
            (object2.mass - object1.mass) * v2n + 2 * object1.mass * v1n
        ) / total_mass

        # Calculate the new velocities
        v1_after = normal * v1n_after + tangent * v1t
        v2_after = normal * v2n_after + tangent * v2t

        # Calculate the force needed to achieve the new velocities
        force1 = (v1_after - object1.velocity) * object1.mass
        force2 = (v2_after - object2.velocity) * object2.mass

        # Add the forces as debt to the objects
        object1.add_debt(force1)
        object2.add_debt(force2)

        # Update velocities directly
        object1.velocity = v1_after
        object2.velocity = v2_after

        if debug:
            debug_log(
                f"Step {object1.time}: New velocity for object1: {v1_after}", object1
            )
            debug_log(
                f"Step {object1.time}: New velocity for object2: {v2_after}", object2
            )
            debug_log(
                f"Step {object1.time}: Added force debt {force1} to object1", object1
            )
            debug_log(
                f"Step {object1.time}: Added force debt {force2} to object2", object2
            )

    def _detect_border(
        object: "Matter", universe: "Universe", debug: bool = False
    ) -> bool:
        """
        Detects if an object has collided with the border of the space.
        """
        if debug:
            debug_log(
                f"Step {object.time}: Detecting border collision with {universe.description()}",
                object,
            )
        return (
            object.position.x - object.radius < 0
            or object.position.x + object.radius > universe.dimensions.x
            or object.position.y - object.radius < 0
            or object.position.y + object.radius > universe.dimensions.y
        )

    def _resolve_border(
        object: "Matter", universe: "Universe", debug: bool = False
    ) -> None:
        """
        Resolves the collision between an object and the border of the space.
        """
        if debug:
            debug_log(
                f"Step {object.time}: Resolving border collision with border", object
            )
        if universe.toroidal:
            # For toroidal universe, wrap the object's position
            if object.position.x < 0:
                object.position.x = universe.dimensions.x
            elif object.position.x > universe.dimensions.x:
                object.position.x = 0

            if object.position.y < 0:
                object.position.y = universe.dimensions.y
            elif object.position.y > universe.dimensions.y:
                object.position.y = 0

            if debug:
                debug_log(
                    f"Step {object.time}: Wrapped position to {object.position}", object
                )
        else:
            # For non-toroidal universe, reverse velocity upon hitting border
            if (
                object.position.x - object.radius < 0
                or object.position.x + object.radius > universe.dimensions.x
            ):
                object.velocity.x = -object.velocity.x
                # Adjust position to ensure object is within bounds
                object.position.x = max(
                    object.radius,
                    min(object.position.x, universe.dimensions.x - object.radius),
                )

            if (
                object.position.y - object.radius < 0
                or object.position.y + object.radius > universe.dimensions.y
            ):
                object.velocity.y = -object.velocity.y
                # Adjust position to ensure object is within bounds
                object.position.y = max(
                    object.radius,
                    min(object.position.y, universe.dimensions.y - object.radius),
                )

            if debug:
                debug_log(
                    f"Step {object.time}: Reversed velocity to {object.velocity}",
                    object,
                )
                debug_log(
                    f"Step {object.time}: Adjusted position to {object.position}",
                    object,
                )
