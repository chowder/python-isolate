from isolate.options import IsolateOptions
import os
import unittest


class IsolateTest(unittest.TestCase):
    def setUp(self) -> None:
        with open('test.sh', 'w+') as f:
            f.write('echo "Hello World"')

    def tearDown(self) -> None:
        if os.path.exists('test.sh'):
            os.remove('test.sh')

    def test_isolate_workspace(self):
        from isolate import isolate

        with isolate(IsolateOptions(box_id=10)) as sandbox:
            sandbox.add_file('test.sh')
            result = sandbox.run(['/bin/bash', 'test.sh'])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.decode().strip(), "Hello World")
