"""Writes the rock chunk models thrown out of blasted walls, as MD3 files."""
import math
import os
import random
import struct
import sys

SEED = 4242
MD3_IDENT = b'IDP3'
SHADER = b'gfx/wrecked-quake-iii-arena/chunk'

# (name, radius) of each chunk model
CHUNKS = [('chunk1', 3.5), ('chunk2', 5.0), ('chunk3', 6.5), ('chunk4', 8.0), ('chunk5', 10.0), ('chunk6', 13.0),
          ('gravel1', 2.0), ('gravel2', 2.7), ('gravel3', 3.4)]


def normalize(v):
    length = math.sqrt(sum(c * c for c in v))
    return tuple(c / length for c in v)


def boulder(rng, radius):
    """A lumpy, flat-faceted rock: a subdivided octahedron with every corner pushed in or out."""
    corners = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    faces = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    points = list(corners)
    mids = {}

    def mid(a, b):
        key = (min(a, b), max(a, b))
        if key not in mids:
            mids[key] = len(points)
            points.append(normalize(tuple((points[a][k] + points[b][k]) / 2 for k in range(3))))
        return mids[key]

    tris = []
    for a, b, c in faces:
        ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
        tris += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]

    stretch = (1.0, rng.uniform(0.65, 1.15), rng.uniform(0.45, 0.85))
    pushed = []
    for p in points:
        r = radius * rng.uniform(0.7, 1.2)
        pushed.append(tuple(p[k] * r * stretch[k] for k in range(3)))
    return pushed, tris


def encode_normal(n):
    lat = int(round(math.atan2(n[1], n[0]) * 256 / (2 * math.pi))) & 255
    lng = int(round(math.acos(max(-1.0, min(1.0, n[2]))) * 256 / (2 * math.pi))) & 255
    return (lat << 8) | lng


def write_md3(path, name, points, tris):
    # every triangle gets its own corners, so the facets stay flat and sharp
    verts, sts, out_tris = [], [], []
    for a, b, c in tris:
        pa, pb, pc = points[a], points[b], points[c]
        e1 = tuple(pb[k] - pa[k] for k in range(3))
        e2 = tuple(pc[k] - pa[k] for k in range(3))
        n = normalize((e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]))
        base = len(verts)
        for p in (pa, pb, pc):
            verts.append((p, n))
            # project the texture from the facet's main direction
            axis = max(range(3), key=lambda k: abs(n[k]))
            s_axis, t_axis = [k for k in range(3) if k != axis]
            sts.append((p[s_axis] / 24.0, p[t_axis] / 24.0))
        out_tris.append((base, base + 2, base + 1))

    mins = [min(p[k] for p, _ in verts) for k in range(3)]
    maxs = [max(p[k] for p, _ in verts) for k in range(3)]
    radius = max(math.sqrt(sum(c * c for c in p)) for p, _ in verts)

    surf_header = 108
    ofs_shaders = surf_header
    ofs_tris = ofs_shaders + 68
    ofs_st = ofs_tris + 12 * len(out_tris)
    ofs_xyz = ofs_st + 8 * len(verts)
    surf_end = ofs_xyz + 8 * len(verts)

    surface = struct.pack('<4s64siiiiiiiiii', MD3_IDENT, b'rock', 0, 1, 1, len(verts), len(out_tris),
                          ofs_tris, ofs_shaders, ofs_st, ofs_xyz, surf_end)
    surface += struct.pack('<64si', SHADER, 0)
    surface += b''.join(struct.pack('<3i', *t) for t in out_tris)
    surface += b''.join(struct.pack('<2f', *st) for st in sts)
    surface += b''.join(struct.pack('<3hH', *[int(round(c * 64)) for c in p], encode_normal(n)) for p, n in verts)

    header_size = 108
    ofs_frames = header_size
    ofs_surfaces = ofs_frames + 56
    ofs_end = ofs_surfaces + len(surface)
    data = struct.pack('<4si64siiiiiiiii', MD3_IDENT, 15, name.encode(), 0, 1, 0, 1, 0,
                       ofs_frames, ofs_surfaces, ofs_surfaces, ofs_end)
    data += struct.pack('<3f3f3ff16s', *mins, *maxs, 0, 0, 0, radius, b'frame0')
    data += surface

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def main(out_dir):
    rng = random.Random(SEED)
    for name, radius in CHUNKS:
        points, tris = boulder(rng, radius)
        write_md3(os.path.join(out_dir, 'models', 'wrecked-quake-iii-arena', name + '.md3'),
                  'models/wrecked-quake-iii-arena/' + name + '.md3', points, tris)


if __name__ == '__main__':
    main(sys.argv[1])
