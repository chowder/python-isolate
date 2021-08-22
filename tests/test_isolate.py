import os
import unittest

from isolate import IsolateOptions


class IsolateTest(unittest.TestCase):
    def setUp(self) -> None:
        os.chdir(os.path.dirname(__file__))

    def test_isolate_workspace(self):
        from isolate import isolate

        with isolate(IsolateOptions(box_id=10)) as sandbox:
            sandbox.add_file('test_data/echo.sh')
            result = sandbox.run(['/bin/bash', 'echo.sh'])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.decode().strip(), "Hello World")
