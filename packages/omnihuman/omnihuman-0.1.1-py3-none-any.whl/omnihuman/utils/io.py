"""
IO Module
=========

This module provides utility functions for reading and writing files.

Functions:
----------
- read_frames: Read frames from image or video file as 4D tensor (n_frames, n_channels, height, width).
"""

__all__ = ["read_frames"]

from mimetypes import guess_type
from typing import Any, Union

import torch
from torchvision.io import read_image, read_video


def read_frames(path: str, return_as_numpy: bool = False) -> Union[torch.Tensor, Any]:
    """Read frames from image or video file as 4D tensor (n_frames, n_channels, height, width).

    Args:
        path (str): Where the image or video file is located.
        return_as_numpy (bool, optional): Whether to return the frames as numpy array, or torch.Tensor if False. Defaults to False.

    Raises:
        ValueError: If the file type is neither image nor video.

    Returns:
        Union[torch.Tensor, numpy.ndarray]: Frames as 4d torch tensor if return_type is "torch", otherwise as numpy array in shape (n_frames, n_channels, height, width).
    """

    file_type = guess_type(path)[0] or ""
    if file_type.startswith("image"):
        frames = read_image(path)
        frames = frames.unsqueeze(0)
    elif file_type.startswith("video"):
        frames, *_ = read_video(path)
    else:
        raise ValueError(f"Unsupported file type: {file_type} of '{path}'")

    if return_as_numpy == "numpy":
        frames = frames.numpy()

    return frames
