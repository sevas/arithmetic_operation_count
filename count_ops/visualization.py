from pathlib import Path
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

from count_ops.common import OpCountNode
from count_ops.parse import parse
from count_ops.lang_py import make_opcount_tree, get_func_named

SRC_FILE = Path(__file__).parent.parent / "main_numba.py"
FUNC_NAME = "sobel"


class ColorPalette:
    black = "#1d2021"
    red = "#cc241d"
    green = "#98971a"
    yellow = "#d79921"
    blue = "#458588"
    purple = "#b16286"
    aqua = "#689d6a"
    white = "#eeeeee"
    grey = "#303030"


def add_tree_to_scene(op_tree, gv: pg.GraphicsView):
    all_items = []

    def add_node_to_scene(node: OpCountNode, pos):
        color_fill = pg.mkColor(ColorPalette.grey)
        color_border = pg.mkColor(ColorPalette.white)
        tooltip = f"""<b>Node: </b>{node.name}"""
        box_width = 50

        if node.is_branch:
            color_fill = pg.mkColor(ColorPalette.blue)
            box_width += 10
        elif node.children_op_mult > 1:
            box_width += 10
            color_fill = pg.mkColor(ColorPalette.green)
            tooltip = f"""<b>Node: </b>{node.name}<br><b>Op multiplier:</b> {node.children_op_mult}"""
        elif node.op_count.add > 0 or node.op_count.mul > 0:
            box_width += 10
            color_fill = pg.mkColor(ColorPalette.yellow)
            tooltip = f"""<b>Node: </b>{node.name}<br><b>#muls: </b>: {node.op_count.mul}<br><b>#adds:</b>{node.op_count.add}"""

        label = f"{node.name}"[:10]
        # box_width = 20 * len(msg)
        node_item = QtWidgets.QGraphicsRectItem(pos[0], pos[1], box_width, 50)
        node_item.setToolTip(tooltip)
        node_item.setBrush(QtGui.QBrush(color_fill))
        node_item.setPen(QtGui.QPen(color_border, 1))
        node_item.z = 10
        txt = QtWidgets.QGraphicsTextItem(label)
        txt.setPos(pos[0] + 10, pos[1] + 5)
        txt.z = 10

        gv.addItem(node_item)
        gv.addItem(txt)
        all_items.append(txt)
        all_items.append(node_item)
        children_count = 0
        total_row_count = 0
        if node.children:
            for i, child in enumerate(node.children):
                child_item, nrows = add_node_to_scene(
                    child, pos=(pos[0] + box_width + 50, pos[1] + (total_row_count * 50))
                )

                x0 = node_item.boundingRect().center().x()
                y0 = node_item.boundingRect().center().y()
                x1 = child_item.boundingRect().center().x()
                y1 = child_item.boundingRect().center().y()
                path = QtGui.QPainterPath()
                path.moveTo(x0, y0)
                path.lineTo(x0, y1)
                path.lineTo(x1, y1)
                line = QtWidgets.QGraphicsPathItem(path)
                line.setPen(pg.mkPen(color_border, width=3))
                gv.addItem(line)
                all_items.append(line)
                total_row_count += nrows

        return node_item, total_row_count + 1

    add_node_to_scene(op_tree, (0, 0))
    print(len(all_items))


def main():
    parsed = parse(SRC_FILE.read_text())
    f = get_func_named(parsed, FUNC_NAME)
    op_tree = make_opcount_tree(f)

    pg.setConfigOption("foreground", "w")
    pg.setConfigOption("background", pg.mkColor(ColorPalette.black))
    # pg.setConfigOptions(antialias=True)
    app = pg.mkQApp()
    win = pg.GraphicsView()
    win.enableMouse()
    win.resize(1000, 600)
    win.setWindowTitle("Func operation count tree")
    win.show()
    add_tree_to_scene(op_tree, win)

    app.exec()


def graphicscene_sandbox():
    app = pg.mkQApp()
    win = pg.GraphicsView()
    win.enableMouse()
    box = QtWidgets.QGraphicsRectItem(0, 0, 100, 100)
    box.setBrush(QtGui.QBrush(pg.mkColor(ColorPalette.blue)))
    box.setToolTip("box")

    box2 = QtWidgets.QGraphicsRectItem(150, 150, 100, 100)
    box2.setBrush(QtGui.QBrush(pg.mkColor(ColorPalette.blue)))

    box2.setToolTip("box2")
    win.addItem(box)
    win.addItem(box2)
    win.show()

    app.exec()


if __name__ == "__main__":
    main()
    # graphicscene_sandbox()
