import math

import numpy as np
import numpy.typing as npt
from numpy.lib.stride_tricks import as_strided

from PIL import Image as im

from .colors import RGBA_COLOR_D
from .colors import RGBA_COLOR_U
from .image import Image


NumpyType = npt.NDArray
import fpg.generator.neighborhood as nh


class Cells(Image):
    """
    This class defines the cells of the Cellular Automata (CA).
    """

    def __init__(
        self,
        nstrategy: nh.NeighborStrategy = nh.NeumannStrategy(),
        *args: str,
        **kwargs: int,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._disc = np.zeros(self._img.shape, dtype=np.float32)
        self._nstrategy = nstrategy

    @property
    def discs(self) -> NumpyType:
        return self._disc

    @property
    def visited(self) -> NumpyType:
        return self._visited

    ############################################################################

    def get_disc(self, x: int, y: int) -> float:
        return self._disc[y, x]

    def set_disc(self, x: int, y: int, disc: float) -> None:
        self._disc[y, x] = disc

    ############################################################################

    def get_visited(self, x: int, y: int) -> bool:
        return self._visited[y, x]

    def set_visited(self, x: int, y: int) -> None:
        self._visited[y, x] = True

    def reset_visited(self) -> None:
        self._visited = np.zeros(self._img.shape, dtype=np.uint8)

    ############################################################################

    def show_cells(self) -> None:
        pil = im.fromarray(self.data, mode="RGBA")
        pil.show()

    def print_visits(self) -> None:
        print("visited:\n", self._visited)

    def print_discs(self) -> None:
        print()
        print("print discriminators: ")
        for row in self._disc:
            print("[", end="")
            for d in row:
                if d > 0:
                    print(" +", end="")
                elif d < 0:
                    print(" -", end="")
                else:
                    print("  ", end="")
            print("]")
        print()

    ############################################################################

    def develop(self, RA: int, RI: int, w: float) -> None:
        """Develop the next generation of Cells.

        Note:
            Is done by using the Cellular Automata (CA) by David Young.

        Args:
            RA (int): the radius of the activator cells
            RI (int): the radius of the inhibitor cells
            w (float): the weight of the inhibitor RI. Whereas RA has a fixed
                weight of 1 for simplicity.
        """
        # plausibility check for radius
        if RA >= RI:
            raise ValueError(
                f"Activator radius {RA=} should be less than the inhibitor"
                f"radius {RI=}!"
            )

        # 1st pass : calculate cells Disc and apply cells-set
        print("1st pass start - calculate cells Disc and apply cells-set")
        self.update_discs(RA, RI, w)

        # 2nd pass : apply cells to image:
        print("2nd pass start - apply cells to image")
        for y in range(self.height):
            for x in range(self.width):
                pos = (x, y)
                d = self.get_disc(*pos)
                if d > 0:
                    self.set_color(*pos, RGBA_COLOR_D)
                elif d < 0:
                    self.set_color(*pos, RGBA_COLOR_U)

        print("finished")

    def update_discs(self, RA: int, RI: int, w: float) -> int:
        for y in range(self.height):
            for x in range(self.width):
                pos = (x, y)
                AD = self.count_d_cells(pos, RA)  # radius/circle
                ID = self.count_d_cells(pos, RI) - AD  # ring

                # This computation happens to all cells at the same time,
                # therefore we must defer the setting of the color to a 2nd step.
                disc = AD - (w * ID)
                # print("activators: ", AD)
                # print("inhibitors: ", ID)
                # print("disc: ", disc)
                self.set_disc(*pos, disc)

    def count_d_cells(self, pos: tuple[int, int], distance: int) -> int:
        """Counts the D cells at position pos in a given radius."""
        cell_count = 0
        region = self._nstrategy.get_neighborhood(self, pos, distance)

        for pos in region:
            # print("pos: ", type(pos))
            # print("pos: ", pos)
            cell_color = self.get_color(*pos)
            is_equal = (
                cell_color[0] == RGBA_COLOR_D.r
                and cell_color[1] == RGBA_COLOR_D.g
                and cell_color[2] == RGBA_COLOR_D.b
                and cell_color[3] == RGBA_COLOR_D.a
            )
            if is_equal:
                cell_count += 1
        return cell_count
