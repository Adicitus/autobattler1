import unittest
from uuid import uuid4
from emitter import Emitter

class EmitterTests(unittest.TestCase):
    def test_emitter_creation(self):
        e = Emitter()

    def test_emitter_on_off(self):
        e = Emitter()

        f = lambda e, d: True

        self.assertFalse("test" in e.events)
        e.on("test", f)
        self.assertTrue("test" in e.events)
        self.assertTrue(len(e.events["test"]) == 1)
        e.off("test", f)
        self.assertTrue(len(e.events["test"]) == 0)
    
    def test_emitter_emit(self):
        e = Emitter()

        flags = {}
        data = uuid4().hex

        keep = lambda *_:  flags.__setitem__("keep", data) or True
        discard = lambda *_: flags.__setitem__("discard", data) or False

        self.assertFalse("test" in e.events)
        e.on("test", keep)
        e.on("test", discard)

        self.assertTrue(len(e.events["test"]) == 2)
        self.assertFalse("keep" in flags)
        self.assertFalse("discard" in flags)

        e.emit("test", None)
        
        self.assertTrue(len(e.events["test"]) == 1)
        self.assertTrue("keep" in flags)
        self.assertTrue("discard" in flags)
        self.assertEqual(flags["keep"], data)
        self.assertEqual(flags["discard"], data)


if __name__ == "__main__":
    unittest.main()