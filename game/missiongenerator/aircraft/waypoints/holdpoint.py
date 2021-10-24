import logging

from dcs.point import MovingPoint
from dcs.task import ControlledTask, OrbitAction

from gen.flights.flightplan import LoiterFlightPlan
from .pydcswaypointbuilder import PydcsWaypointBuilder


class HoldPointBuilder(PydcsWaypointBuilder):
    def build(self) -> MovingPoint:
        waypoint = super().build()
        loiter = ControlledTask(
            OrbitAction(altitude=waypoint.alt, pattern=OrbitAction.OrbitPattern.Circle)
        )
        if not isinstance(self.flight.flight_plan, LoiterFlightPlan):
            flight_plan_type = self.flight.flight_plan.__class__.__name__
            logging.error(
                f"Cannot configure hold for for {self.flight} because "
                f"{flight_plan_type} does not define a push time. AI will push "
                "immediately and may flight unsuitable speeds."
            )
            return waypoint
        push_time = self.flight.flight_plan.push_time
        self.waypoint.departure_time = push_time
        loiter.stop_after_time(int(push_time.total_seconds()))
        waypoint.add_task(loiter)
        return waypoint
