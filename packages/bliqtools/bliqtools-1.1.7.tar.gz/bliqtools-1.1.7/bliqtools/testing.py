"""
This module is for testing classes that provide contextlib helpers to monitor and assess the performance of 
functions during unit testing.

"""

import sys
import os
import time
from threading import Thread, Lock
from contextlib import suppress

import psutil


class TimeIt:
    """
    A Timer for performance testing in unittesting. Can be used as a context as in:

        with TimeIt():
            time.sleep(0.5)
    ...

    Attributes
    ----------
    description : str
        A meaningful description

    """

    def __init__(self, description=None):
        """

        Initialize the timer with a description, can be used with contextlib with TimeIt():
        to time the block of code that is included.

            Parameters:
                    description (str): A meaningful description. Defaults to "Elapsed time"

        """
        self.start_time = None
        self.duration = None
        if description is None:
            description = "Elapsed time"
        self.description = description

    def __enter__(self):
        """
        When the context is created, start the timer.

        """
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When exiting the context, provide the timing information for the block.
        """
        self.duration = time.time() - self.start_time
        print(f"{self.description} : {self.duration:.2f}s")


class MemoryMonitor:
    """
    A Memory monitor for tasks that use large amounts of memory that require
    some testing and optimization. Will collect the available virtual memory (in Gb)
    every 0.1 seconds and output the time evolution to screen when done.


    with MemoryMonitor():
        # do something

    """

    def __init__(self, description=None, delay=0.1, no_output=False):
        """
        Initializer

            Parameters:
                    description (str): A meaningful description. Defaults to "Memory Monitor"
                    delay (float)    : A delay (defaults to 0.1) between sampling points.
                    no_output (bool): If true, will not print to screenm the stats when exiting.
                    You can use the stats with your own function before exiting the context.

        """

        if description is None:
            description = Debuggable.line_descript(
                frame_up=2, format_string="Memory monitor @line {2} in {1}"
            )

        self.description = description
        self.delay = delay
        self.stats = []
        self.no_output = no_output
        self.start_time = None

        self._thread = None
        self._lock = Lock()
        self._must_exit = False

    def __enter__(self):
        """
        When the context is created, start the timer and the background thread that will monitor
        the memory without requiring any other action by the user.

        """
        self.start_time = time.time()
        self._thread = Thread(target=self.monitor)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When exiting the context, ask the background thread to quit, and wait for the thread to have
        fully exited.  Then, report stats.

        """
        with self._lock:
            self._must_exit = True
        self._thread.join()
        if not self.no_output:
            self.report_stats()

    def monitor(self):
        """
        The background thread loop that samples the memory at regular intervals, until requested to quit.
        """
        while True:
            time_now = time.time() - self.start_time
            memory_available_in_gb = psutil.virtual_memory().available / 1e9
            process = psutil.Process()
            memory_used_by_process_in_gb = process.memory_info().rss / 1e9
            with self._lock:
                self.stats.append(
                    {
                        "time": time_now,
                        "available": memory_available_in_gb,
                        "process": memory_used_by_process_in_gb,
                    }
                )
                if self._must_exit:
                    break
            time.sleep(self.delay)

    def report_stats(self):
        """
        Print the description followed by a tab-separated list of times and available memory.
        """
        available_mem = [entry["available"] for entry in self.stats]
        min_available = min(available_mem)
        process_mem = [entry["process"] for entry in self.stats]
        max_process = max(process_mem)

        print(f"-- begin stats for {self.description}")
        print(f"Maximum used by process: {max_process:.3} Gb")
        print(f"Minimum virtual memory: {min_available:.3} Gb")

        print("time [s]\tavailable [Gb]\tprocess [Gb]")
        for memstats in self.stats:
            sampling_time = memstats["time"]
            available = memstats["available"]
            process = memstats["process"]
            print(f"{sampling_time:8.2f}\t{available:13.2f}\t{process:12.2f}")
        print(f"-- end stats")

    def report_graph(self):
        """
        Show a graph of memory versus time using matplotlib
        """
        import matplotlib.pyplot as plt

        with suppress(Exception):
            plt.style.use(
                "https://raw.githubusercontent.com/dccote/Enseignement/master/SRC/dccote-basic.mplstyle"
            )

        _, ax = plt.subplots()

        sampling_time = [entry["time"] for entry in self.stats]
        available_mem = [entry["available"] for entry in self.stats]
        process_mem = [entry["process"] for entry in self.stats]
        ax.plot(sampling_time, process_mem, "k-", label="Process used")
        ax.plot(sampling_time, available_mem, "k--", label="System available")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Memory [Gb]")
        ax.legend()
        plt.show()


class Progress:
    """
    A simple Progress class to provide feedback to the user when a task is taking a long time.
    Can provide feedback every N iterations, and not before a certain time (no need to provide feedback
    if the task is not long enough).  The default is 3 seconds.


    Simply create as a context and call next() every iteration.

    n = 100
    with Progress(total=n, show_every=10, delay_before_showing=0) as progress:
        for _ in range(n):
            progress.next()

    """

    def __init__(
        self,
        total,
        description=None,
        show_count=10,
        delay_before_showing=3,
        message=None,
    ):
        """
        Initialize with the total number of iterations

            Parameters:
                total (int) : total number of iterations in the task
                description (str): A meaningful description
                show_count (int) : How many times you need progress shown
                show_every (int) : provide feedback every 'show_every' iterations.
                delay_before_showing (float): Don't provide any feedback before this delay
                message (str) : The format-string for providing feedback. Defaults to "{1}: {0:.0f}%"
        """
        self.total = total
        self.iteration = 0
        self.message = message
        self.start_time = None

        if description is not None:
            self.description = description
        else:
            self.description = "Completed"

        self.show_count = show_count
        self.show_every = self.total // self.show_count

        self.delay_before_showing = delay_before_showing
        if message is None:
            self.message = "{1}: {0:.0f}%"
        self._last_iteration_shown = None

    def __enter__(self):
        """
        When the context is created, start the timer.

        """
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When exiting the context, show final feedback at 100% if needed (frustrating to
        see 97% as the last feedback in a loop)

        """
        if (
            self._last_iteration_shown != self.total
            and self._last_iteration_shown is not None
        ):
            self.iteration = self.total
            self.show()

    def next(self):
        """
        This function must be called by the user of the class after each iteration.
        """
        self.iteration += 1

        if time.time() - self.start_time > self.delay_before_showing:
            if self.iteration % self.show_every == 0:
                self.show()

    def show(self):
        """
        Show default feedback.
        """
        print(self.message.format(self.iteration / self.total * 100, self.description))
        self._last_iteration_shown = self.iteration


class Debuggable:
    """
    A very simple protocol that can be added as a parent class to any class in order to inspect
    the internal variables relatively painlessly (and in a way that is more powerful than just 'print')

    It can also save the current state, and provide feedback on only what has changed since that time.

    Add it to your class like so and call its __init__():

    MyClass(Debuggable):
        def __init__(self, ...):
            Debuggable.__init__(self, variables_to_inspect=['a','timer','etc'])
            ...

    """

    def __init__(self, variables_to_inspect):
        """
        Initialize the list of variables to inspect (providing feedback for everything would be useless)
        Internally, the state is kept
        """
        self.saved_state = None
        self.variables_to_inspect = variables_to_inspect
        self.reference = None
        self.max_preview_characters = 20

    def save_state(self):
        """
        Save the current state, which will be used as a reference later if requested
        """
        self.saved_state = self.get_state()

    def get_state(self):
        """
        Return the state of all variables
        """
        state = {}
        for var_name in self.variables_to_inspect:
            var = getattr(self, var_name)
            state[var_name] = var
        return state

    def get_differential_state(self):
        """
        Return the state of only the variables that have changed since the state was saved.

        """
        current_state = self.get_state()
        previous_sate = self.saved_state
        if self.saved_state is None:
            return current_state

        for var_name, saved_var in previous_sate.items():
            var = current_state[var_name]
            try:
                if saved_var == var:
                    current_state.pop(var_name)
            except ValueError:
                if (saved_var == var).all():
                    current_state.pop(var_name)

        return current_state

    def dump_internals(self):
        """
        Dump to screen a debugger-like output with the value of variables to inspect.
        If variables are large, provide a shorter version with meaningful info.
        """
        line = self.line_descript()
        print(f"\n-- begin {line}\n")

        if self.saved_state:
            state = self.get_differential_state()
        else:
            state = self.get_state()

        elements_to_output = []
        for var_name, var in state.items():
            output = var
            if sys.getsizeof(var) > 100:
                output = f"{var}"
                n_max = min(len(output), self.max_preview_characters)
                output = output.replace("\n", " ")
                preview = output[0:n_max]

                # We use the type as a string to avoid having to load numpy
                type_as_str = str(type(var))
                if "numpy.ndarray" in type_as_str:
                    output = f"shape={var.shape}, [{preview}..."
                elif "list" in type_as_str:
                    output = f"len={len(var)}, [{preview}..."
                else:
                    output = f"Too large, {preview}"

            elements_to_output.append([var_name, str(type(var)), str(output)])

        widths = [0, 0, 0]
        for record in elements_to_output:
            for i, element in enumerate(record):
                widths[i] = max(len(element), widths[i])

        for element in elements_to_output:
            var_name = element[0]
            var_type = element[1]
            output = element[2]
            print(f"   {var_name:{widths[0]+3}} {var_type:{widths[1]}} : {output}")
        print(f"\n-- end {line}")

    @classmethod
    def line_descript(cls, frame_up=2, format_string=None, short=True):
        """
        A method used internally to obtain information about what line of code called the
        _dump_internals_ method.

        You can provide a format string for the function name {0} filename {1} and line_number {2}
        """
        if format_string is None:
            format_string = "{0} ({1} @line {2})"

        frame = sys._getframe(frame_up)
        co = frame.f_code

        filename = co.co_filename
        if short:
            _, filename = os.path.split(co.co_filename)

        return format_string.format(co.co_name, filename, frame.f_lineno)
