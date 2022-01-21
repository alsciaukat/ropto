# written by Jeemin Kim
# Jan 14, 2022
# github.com/mrharrykim

from datetime import timedelta
from lib.utils import RoptoError
from config import TOTAL_OUTPUT_LENGTH_VERBOSE_2, OUTPUT_COMPLETE_INDICATOR

class RouteOperationNotPermittedError(RoptoError):
    pass

class Route:
    """
    Abstract route resembles a path on a weighted graph.

    Properties of Route instance
    * points: A walk through graph. It starts form the left.
    * duration: Weight of the path which is the total time the route takes.
    """
    def __init__(self, points: list[int], duration: int):
        self.points = points
        self.duration = duration
    def __add__(self, other):
        if not isinstance(other, Route):
            raise RouteOperationNotPermittedError("Only supports addition between routes")
        if self.points[-1] != other.points[0]:
            raise RouteOperationNotPermittedError("Route end point and start point doesn't match")
        self.points.extend(other.points[1:])
        self.duration += other.duration
        return self
    def __gt__(self, other):
        if not isinstance(other, Route):
            raise RouteOperationNotPermittedError("Only supports comparison between routes")
        if len(self.points) != len(other.points):
            raise RouteOperationNotPermittedError("Route length is not the same")
        return self.duration > other.duration
    def __lt__(self, other):
        if not isinstance(other, Route):
            raise RouteOperationNotPermittedError("Only supports comparison between routes")
        if len(self.points) != len(other.points):
            raise RouteOperationNotPermittedError("Route length is not the same")
        return self.duration < other.duration
    def __repr__(self):
        duration_formatted = timedelta(milliseconds=self.duration)
        return f"route through: {self.points}\ntakes: {duration_formatted}"

class TSPSolver:
    def __init__(self, verbose: int =1):
        self.verbose = verbose

    def solve(self, duration_matrix: list[list[int]], no_return: bool) -> Route:
        output_prefix = "Solving TSP"
        if self.verbose == 2:
            print(output_prefix + "."*(TOTAL_OUTPUT_LENGTH_VERBOSE_2 - len(output_prefix)), end="\r")
        self.duration_matrix = duration_matrix
        through = set(range(len(duration_matrix)))
        through.remove(0)
        if no_return:
            shortest_route = None
            for point in through:
                copy_of_through = through.copy()
                copy_of_through.remove(point)
                route = self.get_shortest_route(copy_of_through, point)
                if not shortest_route:
                    shortest_route = route
                else:
                    if route < shortest_route:
                        shortest_route = route
            solution = shortest_route
        else:
            solution = self.get_shortest_route(through, 0)
        if self.verbose == 2:
            print(output_prefix + "."*(TOTAL_OUTPUT_LENGTH_VERBOSE_2 - len(output_prefix) - len(OUTPUT_COMPLETE_INDICATOR)) + OUTPUT_COMPLETE_INDICATOR)
        return solution


    def get_shortest_route(self, through: set[int], end: int) -> Route:
        """
        Implementation of Held-Karp algorithm.

        It solves traveling salesman problem (TSP) recursively.
        """
        if not through:
            return Route([0, end], self.duration_matrix[0][end])
        
        shortest_route = None
        for point in through:
            copy_of_through = through.copy()
            copy_of_through.remove(point)
            route = self.get_shortest_route(copy_of_through, point) + Route([point, end], self.duration_matrix[point][end])
            if not shortest_route:
                shortest_route = route
            else:
                if route < shortest_route:
                    shortest_route = route
        return shortest_route


if __name__ == "__main__":
    pass
