from datetime import datetime
from os.path import exists, sep
from os import makedirs

class Logger:
        """
        Provides a logging tool to record and save logging events.

        Attributes:
                begin: The moment the instance was created.
                stopwatch: The timestamp record used to measure main process durations.
                checkpoint: The timestamp record used to measure intermediate process durations.
                file_name: The name of the file the log is saved to.
        """
        def __init__(self, directory = "logs"):
                """Initialises a new instance."""
                self.timestamp = datetime.now()
                self.begin = self.timestamp
                self.stopwatch = self.timestamp
                self.checkpoint = self.timestamp
                if not exists(directory): makedirs(directory)
                self.file_name = directory + sep + str(self.timestamp)[:-7].replace(":","_").replace("-","_").replace(" ","_") + ".log"
                print(self.timestamp.strftime("%d %b %Y %H:%M:%S"))

        def log(self, message, line_breaks = 0):
                """
                Prints and logs a message.

                Args:
                        message: A string message.
                        line_breaks: The number of line breaks to insert after the message.
                """

                with open(self.file_name, "a") as file:
                        if message.strip() != "":
                                message = str(message)
                                print(message + ("\n" * line_breaks))
                                file.write(str(datetime.now()) + " >>> " + message.strip() + "\n")

        def close(self, message = ""):
                """
                Final log message.

                Args:
                        message: A string message.
                """
                self.log(message)
                self.log("Total time: " + self.delta(self.begin, datetime.now()))

        def start(self, message = "", line_breaks = 0):
                """
                Log the start of a major process.
                Resets the stopwatch and logs message.

                Args:
                        message: A string message.
                        line_breaks: The number of line breaks to insert after the message.
                """
                now = datetime.now()
                self.stopwatch = now
                self.checkpoint = now
                self.log(message, line_breaks)

        def stop(self, message = "", line_breaks = 0):
                """
                Log the end of a major process.
                Resets the stopwatch and logs message.

                Args:
                        message: A string message.
                        line_breaks: The number of line breaks to insert after the message.
                """
                elapsed = self.delta(self.stopwatch, datetime.now())
                if message: message = str(message) + " "
                self.log(message + "(" + elapsed + ")", line_breaks)

        def start_check(self, message = ""):
                """
                Log the start of an intermediate process.
                Resets the checkpoint and logs message.

                Args:
                        message: A string message.
                """
                self.log(message)
                self.checkpoint = datetime.now()

        def end_check(self, message = "", line_breaks = 0):
                """
                Log the end of an intermediate process.
                Resets the checkpoint and logs message.

                Args:
                        message: A string message.
                        line_breaks: The number of line breaks to insert after the message.
                """
                elapsed = self.delta(self.checkpoint, datetime.now())
                if message: message = str(message) + " "
                self.log(message + "(" + elapsed + ")", line_breaks)
                self.checkpoint = datetime.now()

        def delta(self, begin, end):
                """
                Calculates the time elapsed between to time points.

                Args:
                        begin: The start of the elapsed period.
                        end: The end of the elapsed period.
                """
                delta = end - begin
                return str(delta).rjust(15, "0")
