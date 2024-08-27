from typing import Any, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class Node:
    value: Any
    left: Optional["Node"] = None
    right: Optional["Node"] = None

    def __str__(self):
        lines = _build_tree_string(self, 0, False, "-")[0]
        return "\n".join(line.rstrip() for line in lines)


def search(root: Node, value: Any) -> Optional[Node]:
    if root is None or root.value == value:
        return root
    if root.value < value:
        return search(root.right, value)
    return search(root.left, value)


def preorder(root: Node, output: List[Node]) -> List[Node]:
    if root.value is not None:
        output.append(root.value)
    if root.left is not None:
        preorder(root.left, output)
    if root.right is not None:
        preorder(root.right, output)
    return output


def _build_tree_string(
    root: Optional[Node],
    curr_index: int,
    include_index: bool = False,
    delimiter: str = "-",
) -> Tuple[List[str], int, int, int]:
    if root is None:
        return [], 0, 0, 0
    line1 = []
    line2 = []
    if include_index:
        node_repr = "{}{}{}".format(curr_index, delimiter, root.value)
    else:
        node_repr = str(root.value)
    new_root_width = gap_size = len(node_repr)
    l_box, l_box_width, l_root_start, l_root_end = _build_tree_string(
        root.left, 2 * curr_index + 1, include_index, delimiter
    )
    r_box, r_box_width, r_root_start, r_root_end = _build_tree_string(
        root.right, 2 * curr_index + 2, include_index, delimiter
    )
    if l_box_width > 0:
        l_root = (l_root_start + l_root_end) // 2 + 1
        line1.append(" " * (l_root + 1))
        line1.append("_" * (l_box_width - l_root))
        line2.append(" " * l_root + "/")
        line2.append(" " * (l_box_width - l_root))
        new_root_start = l_box_width + 1
        gap_size += 1
    else:
        new_root_start = 0
    line1.append(node_repr)
    line2.append(" " * new_root_width)
    if r_box_width > 0:
        r_root = (r_root_start + r_root_end) // 2
        line1.append("_" * r_root)
        line1.append(" " * (r_box_width - r_root + 1))
        line2.append(" " * r_root + "\\")
        line2.append(" " * (r_box_width - r_root))
        gap_size += 1
    new_root_end = new_root_start + new_root_width - 1
    gap = " " * gap_size
    new_box = ["".join(line1), "".join(line2)]
    for i in range(max(len(l_box), len(r_box))):
        l_line = l_box[i] if i < len(l_box) else " " * l_box_width
        r_line = r_box[i] if i < len(r_box) else " " * r_box_width
        new_box.append(l_line + gap + r_line)
    return new_box, len(new_box[0]), new_root_start, new_root_end


build_tree = _build_tree_string
