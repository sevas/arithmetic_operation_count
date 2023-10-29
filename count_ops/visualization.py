from pathlib import Path
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

from count_ops.common import OpCountNode
from count_ops.parse import parse
from count_ops.lang_py import make_opcount_tree, get_func_named

SRC_FILE = Path(__file__).parent.parent / "main_numba.py"
FUNC_NAME = "simple_branch"


class ColorPalette:
    black = "#1d2021"
    red = "#cc241d"
    green = "#98971a"
    yellow = "#d79921"
    blue = "#458588"
    purple = "#b16286"
    aqua = "#689d6a"
    white = "#eeeeee"


def add_tree_to_scene(op_tree, gv: pg.GraphicsView):
    # gv.clear()
    # gv.setAspectLocked(True)
    # gv.setRange(QtCore.QRectF(0, 0, 100, 100))
    # gv.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

    scene = gv.scene()

    def add_node_to_scene(node: OpCountNode, pos, parent=None):
        if parent is None:
            parent = scene

        color_fill = pg.mkColor(ColorPalette.blue)
        color_border = pg.mkColor(ColorPalette.white)
        if node.is_branch:
            color_fill = pg.mkColor(ColorPalette.red)
        elif node.children_op_mult > 1:
            color_fill = pg.mkColor(ColorPalette.green)
        elif node.op_count.add > 0 or node.op_count.mul > 0:
            color_fill = pg.mkColor(ColorPalette.yellow)

        msg = f"{node.name}"[:10]
        # box_width = 20 * len(msg)
        box_width = 50
        node_item = QtWidgets.QGraphicsRectItem(pos[0], pos[1], box_width, 50)
        node_item.setToolTip(msg)
        node_item.setBrush(QtGui.QBrush(color_fill))
        node_item.setPen(QtGui.QPen(color_border, 3))

        txt = QtWidgets.QGraphicsTextItem(msg)
        txt.setPos(pos[0] + 10, pos[1] + 10)
        txt.z = 10

        parent.addItem(node_item)
        parent.addItem(txt)

        if node.children:
            for i, child in enumerate(node.children):
                child_item = add_node_to_scene(child, pos=(pos[0] + box_width + 50, pos[1] + (i * 100)), parent=parent)

                line = QtWidgets.QGraphicsLineItem(
                    node_item.boundingRect().center().x(),
                    node_item.boundingRect().center().y(),
                    child_item.boundingRect().center().x(),
                    child_item.boundingRect().center().y(),
                )
                line.setPen(pg.mkPen(color_border, width=3))
                scene.addItem(line)

        return node_item

    add_node_to_scene(op_tree, (0, 0))


def main():
    parsed = parse(SRC_FILE.read_text())
    f = get_func_named(parsed, FUNC_NAME)
    op_tree = make_opcount_tree(f)

    pg.setConfigOption("foreground", "w")
    pg.setConfigOption("background", pg.mkColor(ColorPalette.black))
    # pg.setConfigOptions(antialias=True)
    app = pg.mkQApp()
    win = pg.GraphicsView()
    win.resize(1000, 600)
    win.setWindowTitle("Func operation count tree")
    win.show()
    add_tree_to_scene(op_tree, win)

    app.exec()


if __name__ == "__main__":
    main()
