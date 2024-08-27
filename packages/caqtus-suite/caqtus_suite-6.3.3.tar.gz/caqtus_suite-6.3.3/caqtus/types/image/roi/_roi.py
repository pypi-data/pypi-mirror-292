from abc import ABC, abstractmethod
from typing import NewType, Iterable

import attrs
import numpy as np

Width = NewType("Width", int)
Height = NewType("Height", int)


@attrs.define
class ROI(ABC):
    """Base class for regions of interest inside an image.

    Attributes:
        original_image_size: The size of the original image as (width, height).
    """

    original_image_size: tuple[Width, Height] = attrs.field(
        on_setattr=attrs.setters.validate,
    )

    @original_image_size.validator  # type: ignore
    def _validate_original_image_size(self, _, value):
        if not isinstance(value, tuple):
            raise TypeError(f"original_image_size must be a tuple, got {type(value)}")
        if len(value) != 2:
            raise ValueError(
                "original_image_size must be a tuple (width, height) with two elements"
            )
        if not all(isinstance(x, int) for x in value):
            raise ValueError("original_image_size must be a tuple of integers")
        if not all(x > 0 for x in value):
            raise ValueError("original_image_size must be a tuple of positive integers")

    def get_mask(self) -> np.ndarray:
        """A boolean array with the same shape as the original image.

        True values indicate that the pixel is part of the region of interest."""

        mask = np.full(self.original_image_size, False)
        mask[*self.get_indices()] = True
        return mask

    @abstractmethod
    def get_indices(self) -> tuple[Iterable[int], Iterable[int]]:
        """Return the indices of the pixels in the ROI."""

        raise NotImplementedError

    @property
    def original_width(self) -> int:
        """Return the width of the original image."""

        return self.original_image_size[0]

    @property
    def original_height(self) -> int:
        """Return the height of the original image."""

        return self.original_image_size[1]
