import importlib.util, pathlib, unittest

spec = importlib.util.spec_from_file_location(
    "protocol", pathlib.Path(__file__).parent.parent / "custom_components/kamoer_x2sr/protocol.py")
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


class Frames(unittest.TestCase):
    # Byte strings below are the ATT writes from the real capture (and that worked in nRF Connect).
    def test_startup(self):
        got = [p.build_frame(i, p.FIRST_COUNTER + i, b).hex() for i, b in enumerate(p.startup_bodies())]
        self.assertEqual(got, ["4d000009390200010001000100",
                               "4d0001083a02000000000002",
                               "4d00020a3b020002000100040100"])

    def test_set_volume(self):
        self.assertEqual(p.build_frame(3, 0x023c, p.set_volume_body(1.0)).hex(),
                         "4d0003123c02000a0001000300013f80000000000000")
        self.assertEqual(p.build_frame(4, 0x023d, p.set_volume_body(2.0)).hex(),
                         "4d0004123d02000a0001000300014000000000000000")

    def test_start_run_matches_capture(self):
        self.assertEqual(p.build_frame(5, 0x023e, p.START_RUN_BODY).hex(), "4d00050a3e020002000100130100")

    def test_parse(self):
        n = p.parse_notification(bytes.fromhex("4d04030a3b02000200010004010000"))
        self.assertEqual((n.seq, n.counter), (3, 0x023b))
        self.assertIsNone(p.parse_notification(b"\x49\x04\x03\x01\x00"))


if __name__ == "__main__":
    unittest.main()
