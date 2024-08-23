"""
Creates a window that captures the user's monitor for a given bounding box.
"""
import cv2
from mss import mss

import src.pixeler.vision.oir as oir
import src.pixeler.vision.utils as utils
from src.pixeler.bot.bot import Bot
from src.pixeler.vision.color import GREEN


class ScreenTracking(Bot):
    def on_start(self):
        pass

    def on_stop(self):
        cv2.destroyAllWindows()

    def loop(self):
        bounding_box = {'top': 0, 'left': 0, 'width': 400, 'height': 300}
        sct = mss()
        shapes = []

        while True:
            sct_img = sct.grab(bounding_box)
            mat = utils.mss_to_cv2(sct_img)
            cv2.imshow('screen', mat)
            for shape in shapes:
                cv2.imshow('screen', shape)

            # print(ocr.extract_text(mat))
            # Loops until ESC is pressed
            k = cv2.waitKey(1)
            if k == 27:
                self.stop()
            # Listen for 'r' key
            if k == 114:
                print('drawing rectangle')
                oir.draw_rectangle(mat, (0, 0), 100, 100, GREEN)
                cv2.imshow('screen', mat)
                shapes.append(mat)
            # Listen for 'c' key to clear canvas
            if k == 99:
                shapes.clear()


if __name__ == '__main__':
    example = ScreenTracking()
    example.start()
