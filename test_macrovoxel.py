import unittest

from macrovoxel import voxelize


class OctreeTests(unittest.TestCase):
    def test_uniform_domains_stop_after_first_split(self):
        for occupied in (False, True):
            leaves = voxelize(lambda _: occupied)
            self.assertEqual(len(leaves), 8)
            self.assertTrue(all(leaf.filled == occupied for leaf in leaves))
            self.assertEqual(sum(leaf.edge ** 3 for leaf in leaves), 1)

    def test_mixed_domain_partitions_cube_without_overlap(self):
        depth = 3
        resolution = 2 ** depth
        leaves = voxelize(lambda p: p[0] < 0.375, max_depth=depth, samples=96)
        seen = set()
        for leaf in leaves:
            start = [round(v * resolution) for v in leaf.origin]
            width = round(leaf.edge * resolution)
            for x in range(start[0], start[0] + width):
                for y in range(start[1], start[1] + width):
                    for z in range(start[2], start[2] + width):
                        self.assertNotIn((x, y, z), seen)
                        seen.add((x, y, z))
                        self.assertEqual(leaf.filled, x < 3)
        self.assertEqual(len(seen), resolution ** 3)
        self.assertTrue(any("x" in leaf.path for leaf in leaves))

    def test_thresholds_and_reproducibility(self):
        sphere = lambda p: sum((v - 0.5) ** 2 for v in p) < 0.28 ** 2
        self.assertEqual(voxelize(sphere, max_depth=3), voxelize(sphere, max_depth=3))
        with self.assertRaises(ValueError):
            voxelize(sphere, lower=0.7, fill=0.5)


if __name__ == "__main__":
    unittest.main()
