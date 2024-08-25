"""
Unit tests for the classes in testing: Progress, MemoryMonitor, TimeIt, Debuggable
"""
import envtest
import unittest
import time
from bliqtools.testing import Progress, MemoryMonitor, TimeIt, Debuggable


class TestClasses(unittest.TestCase):
    """
    Unittesting demonstrating use of classes.

    """

    def short_test_id(self):
        """
        Simple function to identify running test
        """
        return self.id().split(".")[
            -1
        ]  # Remove complete class name before the function name

    def setUp(self):
        """
        Display what is running since many tests output text to the console.
        """
        print(f"\n# Current test : {self.short_test_id()}")

    def test_01_timeit(self):
        """
        Use case for TimeIt class
        """
        with TimeIt():
            time.sleep(0.5)

    def test_02_progress(self):
        """
        Use case for Progress class
        """
        n = 100
        with Progress(
            total=n, delay_before_showing=0, description="test_progress"
        ) as progress:
            for _ in range(n):
                progress.next()

    def test_03_memory_monitor_with_print(self):
        """
        Use case for MemoryMonitor class, and printing on exiting
        """
        n = 4
        with MemoryMonitor():
            arrays = []
            for _ in range(n):
                a = [1] * 1_000_000_000
                arrays.append(a)

            # Will print stats automatically upon exiting the context

    def test_04_memory_monitor_without_print(self):
        """
        Use case for MemoryMonitor class, without printing on exiting
        """

        with MemoryMonitor(
            description="Memory allocation loop [4Gb]", no_output=True
        ) as monitor:
            n = 100
            arrays = []
            for _ in range(n):
                a = [1] * 10_000_000
                arrays.append(a)

            # If you don't want the output to screen, then you can use the stats yourself:
            # It is a list of dictionaries
            available_mem = [entry["available"] for entry in monitor.stats]
            min_available = min(available_mem)
            process_mem = [entry["process"] for entry in monitor.stats]
            max_process = max(process_mem)
            print(
                f"The minimum available was {min_available:.2f} Gb, the process used maximum {max_process:.2f} Gb"
            )

    def test_05_memory_monitor_with_graph(self):
        """
        Use case for MemoryMonitor class, without printing on exiting
        """

        with MemoryMonitor(
            description="Memory allocation loop [4Gb]", no_output=True
        ) as monitor:
            n = 100
            arrays = []
            for _ in range(n):
                a = [1] * 10_000_000
                arrays.append(a)

            print("Press q to quit or close the window")
            monitor.report_graph()

    def test_06_debuggable(self):
        """
        Use case for using Debuggable as a base class for another class to allow quick inspection.

        """

        class MyTest(Debuggable):
            """
            Test class inheriting from Debuggable
            """

            def __init__(self):
                import numpy

                Debuggable.__init__(self, ["a", "b", "c", "d"])
                self.a = 1
                self.b = "Test"
                self.c = [1] * 200
                self.d = numpy.zeros(shape=(5, 5, 5))

        test = MyTest()
        test.dump_internals()

        test.save_state()
        test.a = 2
        test.dump_internals()  # Will only show the modified variable a, not others


if __name__ == "__main__":
    unittest.main()
    unittest.main(defaultTest=["TestClasses.test_05_memory_monitor_with_graph"])
