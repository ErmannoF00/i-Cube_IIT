import enum
import gevent


class AggregateMode(enum.Enum):
    SYNC = 0,
    ASYNC = 1


class CallbackAggregator:
    """
    @package CallbackAggregator
    @brief a module to aggregate multiple callbacks and call them in a serial or asynchronous way
    @author Dario Pasquali
    """

    def __init__(self, aggr_mode):
        """
        @param aggr_mode: How to execute the callbacks:
        * CallbackAggregator.ExecMode.SYNC = sequential execution
        * CallbackAggregator.ExecMode.ASYNC = start a new callback if there is a delay in the current one
        """
        self.aggr_mode = aggr_mode
        self.callbacks = []

    def set_exec_mode(self, exec_mode):
        self.aggr_mode = exec_mode

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def handle(self, *data):
        """
        Handle the data from the iCUbe
        @param data:
        @return:
        """
        if self.aggr_mode == AggregateMode.SYNC:
            for clb in self.callbacks:
                clb(*data)
        else:
            gevent.joinall([gevent.spawn(clb(*data)) for clb in self.callbacks])
