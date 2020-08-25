from .constant import Direction as dirs


def get_move_direction(src, dst):
    if src == dst:
        return None

    src_x, src_y = src
    dst_x, dst_y = dst
    dir_x = dst_x - src_x
    dir_y = dst_y - src_y

    if dir_x == 0:
        if dir_y > 0:
            return dirs.n
        else:
            return dirs.s
    elif dir_y == 0:
        if dir_x > 0:
            return dirs.e
        else:
            return dirs.w
    elif dir_x > 0 and dir_y > 0:
        return dirs.ne
    elif dir_x > 0 and dir_y < 0:
        return dirs.se
    elif dir_x < 0 and dir_y < 0:
        return dirs.sw
    else:
        return dirs.nw
