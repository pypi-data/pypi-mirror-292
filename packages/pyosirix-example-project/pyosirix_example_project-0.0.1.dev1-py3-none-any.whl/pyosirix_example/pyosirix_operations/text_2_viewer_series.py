import os
from typing import Tuple

import osirix
from osirix.dcm_pix import DCMPix
from osirix.viewer_controller import ViewerController
import numpy as np

from pyosirix_example.utilities.text_2_image import Text2Image


class Text2Viewer:
    """ Burn text to images on an OsiriX viewer controller.
    """
    def __init__(self, text_file: str = None, text_rgb: Tuple[int, int, int] = (255, 255, 255),
                 background_rgb: Tuple[int, int, int] = (0, 0, 0), remove_background: bool = True):
        # Where we expect to find this file.
        if text_file is None:
            current_path = os.path.dirname(os.path.abspath(__file__))
            text_file = os.path.join(current_path, "..", "data", "viewer_text.txt")
        self._text_file = text_file
        self._text_rgb = text_rgb
        self._background_rgb = background_rgb
        self._remove_background = remove_background

    @property
    def text_file(self) -> str:
        """ The file path containing the text to display.
        """
        return self._text_file

    @property
    def text_rgb(self) -> Tuple[int, int, int]:
        """ The RGB values of the text to display (if image is RGB).
        """
        return self._text_rgb

    @property
    def background_rgb(self) -> Tuple[int, int, int]:
        """ The RGB values of the text background (if image is RGB).
        """
        return self._background_rgb

    @property
    def remove_background(self) -> bool:
        """ Whether to include the background box of the text.
        """
        return self._remove_background

    def read_text(self) -> str:
        """ Load the desired text file.

        This emulates loading weights for a deep-learning model for example.

        Returns:
            str: The desired string.
        """
        with open(self.text_file, "r") as f:
            s = f.read()
        return s

    def write_text_in_pix(self, text: str, pix: DCMPix) -> None:
        """ Write a text string in an OsiriX DCMPix instance.

        Args:
            text (str): The desired string.
            pix (DCMPix): The OsiriX DCMPix.
        """
        t2i = Text2Image()
        if pix.is_rgb:
            rgba = np.roll(pix.image, -1, axis=-1).astype("uint8")
            new_array = t2i.paste_text_in_array(text,
                                                rgba,
                                                location=3,  # Top right
                                                scale=0.4,
                                                offset=0.05,
                                                remove_background=self.remove_background,
                                                align="left",
                                                font_path="GillSans.ttc",
                                                color=self.text_rgb,
                                                bg_color=self.background_rgb)
        else:
            new_array = t2i.paste_text_in_array(text,
                                                pix.image,
                                                location=3,  # Top left
                                                scale=0.75,
                                                offset=0.05,
                                                remove_background=self.remove_background,
                                                align="left",
                                                font_path="GillSans.ttc",
                                                value=4095,
                                                bg_value=0)
        pix.image = np.roll(new_array, 1, axis=-1)

    def write_text_in_viewer_controller(self, text: str, viewer: ViewerController,
                                        movie_idx: int = -1) -> None:
        """ Write a text string in all DCMPix instances within a viewer.

        Args:
            text (str): The desired string.
            viewer (ViewerController): The OsiriX ViewerController.
            movie_idx (int): The frame of the viewer in which to write the text. Default is -1 in
                which case all frames are written.
        """
        if movie_idx == -1:
            for idx in range(viewer.max_movie_index):
                pix_list = viewer.pix_list(idx)
                for pix in pix_list:
                    self.write_text_in_pix(text, pix)
        else:
            pix_list = viewer.pix_list(movie_idx)
            for pix in pix_list:
                self.write_text_in_pix(text, pix)
        viewer.needs_display_update()

    def write_text_in_selected_viewer_controller(self, text: str, movie_idx: int = -1) -> None:
        """ Write a text string in all DCMPix instances within the user-selected viewer.

        Args:
            text (str): The desired string.
            movie_idx (int): The frame of the viewer in which to write the text. Default is -1 in
                which case all frames are written.
        """
        viewer = osirix.frontmost_viewer()
        self.write_text_in_viewer_controller(text, viewer, movie_idx)

    def write_text_in_displayed_pix(self, text: str) -> None:
        """ Write a text string in the currently displayed image.

        Args:
            text (str): The desired string.
        """
        viewer = osirix.frontmost_viewer()
        cur_dcm = viewer.cur_dcm()
        self.write_text_in_pix(text, cur_dcm)
        viewer.needs_display_update()

    def run(self):
        text = self.read_text()
        self.write_text_in_selected_viewer_controller(text)


# There should be at least one "hook" file that runs during execution of the script.
if __name__ == '__main__':
    t2v = Text2Viewer()
    t2v.run()
