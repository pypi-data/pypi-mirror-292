import enum
from typing import TYPE_CHECKING, Iterator, Optional, Tuple, Type, Union

from tapa import util
from tapa.verilog import ast
from tapa.verilog import xilinx as rtl

if TYPE_CHECKING:
  from .task import Task


class Instance:
  """Instance of a child Task in an upper-level task.

  A task can be instantiated multiple times in the same upper-level task.
  Each object of this class corresponds to such a instance of a task.

  Attributes:
    task: Task, corresponding task of this instance.
    instance_id: int, index of the instance of the same task.
    step: int, bulk-synchronous step when instantiated.
    args: a dict mapping arg names to Arg.

  Properties:
    name: str, instance name, unique in the parent module.

  """

  class Arg:

    class Cat(enum.Enum):
      INPUT = 1 << 0
      OUTPUT = 1 << 1
      SCALAR = 1 << 2
      STREAM = 1 << 3
      MMAP = 1 << 4
      ASYNC = 1 << 5
      ASYNC_MMAP = MMAP | ASYNC
      ISTREAM = STREAM | INPUT
      OSTREAM = STREAM | OUTPUT

      @property
      def is_scalar(self) -> bool:
        return self == self.SCALAR

      @property
      def is_istream(self) -> bool:
        return self == self.ISTREAM

      @property
      def is_ostream(self) -> bool:
        return self == self.OSTREAM

      @property
      def is_stream(self) -> bool:
        return bool(self.value & self.STREAM.value)

      @property
      def is_sync_mmap(self) -> bool:
        return self == self.MMAP

      @property
      def is_async_mmap(self) -> bool:
        return self == self.ASYNC_MMAP

      @property
      def is_mmap(self) -> bool:
        return bool(self.value & self.MMAP.value)

    def __init__(self,
                 name: str,
                 instance: 'Instance',
                 cat: Union[str, Cat],
                 port: str,
                 is_upper=False):
      self.name = name
      self.instance = instance
      if isinstance(cat, str):
        self.cat = {
            'istream': Instance.Arg.Cat.ISTREAM,
            'ostream': Instance.Arg.Cat.OSTREAM,
            'scalar': Instance.Arg.Cat.SCALAR,
            'mmap': Instance.Arg.Cat.MMAP,
            'async_mmap': Instance.Arg.Cat.ASYNC_MMAP
        }[cat]
        # only lower-level async_mmap is acknowledged
        if is_upper and self.cat == Instance.Arg.Cat.ASYNC_MMAP:
          self.cat = Instance.Arg.Cat.MMAP
      else:
        self.cat = cat
      self.port = port
      self.width = None
      self.shared = False  # only set for (async) mmaps
      self.chan_count: Optional[int] = None  # only set for hmap
      self.chan_size: Optional[int] = None  # only set for hmap

    def __lt__(self, other):
      if isinstance(other, Instance.Arg):
        return self.name < other.name
      return NotImplemented

    @property
    def mmap_name(self) -> str:
      return self.get_mmap_name()

    def get_mmap_name(self, idx: Optional[int] = None) -> str:
      assert self.cat in {Instance.Arg.Cat.MMAP, Instance.Arg.Cat.ASYNC_MMAP}
      indexed_name = util.get_indexed_name(self.name, idx)
      if self.shared:
        return f'{indexed_name}___{self.instance.name}___{self.port}'
      return indexed_name

  def __init__(self, task: 'Task', instance_id: int, **kwargs):
    self.task = task
    self.instance_id = instance_id
    self.step = kwargs.pop('step')
    self.args: Tuple[Instance.Arg, ...] = tuple(
        sorted(
            Instance.Arg(
                name=rtl.sanitize_array_name(arg['arg']),
                instance=self,
                cat=arg['cat'],
                port=port,
                is_upper=task.is_upper,
            ) for port, arg in kwargs.pop('args').items()))

  @property
  def name(self) -> str:
    return util.get_instance_name((self.task.name, self.instance_id))

  @property
  def is_autorun(self) -> bool:
    return self.step < 0

  # # lower-level state machine
  #
  # ## inputs
  # + start_upper: start signal of the upper-level module
  # + done_upper: done signal of the upper-level module
  # + done: done signal of the lower-level module
  # + ready: ready signal of the lower-level module
  #
  # ## outputs:
  # + start: start signal of the lower-level module
  # + is_done: used for the upper-level module to determine its done state
  #
  # ## states
  # + 00: waiting for start_upper
  #   + start: 0
  #   + is_done: 0
  # + 01: waiting for ready
  #   + start: 1
  #   + is_done: 0
  # + 11: waiting for done
  #   + start: 0
  #   + is_done: 0
  # + 10: waiting for done_upper
  #   + start: 0
  #   + is_done: 1
  #
  # start <- state == 01
  # is_done <- state == 10
  #
  # ## state transitions
  # +    -> 00: if reset
  # + 00 -> 00: if start_upper == 0
  # + 00 -> 01: if start_upper == 1
  # + 01 -> 01: if ready == 0
  # + 01 -> 11: if ready == 1 && done == 0
  # + 01 -> 10: if ready == 1 && done == 1
  # + 11 -> 11: if done == 0
  # + 11 -> 10: if done == 1
  # + 10 -> 10: if done_upper == 0
  # + 10 -> 00: if done_upper == 1

  # # upper-level state machine
  #
  # ## inputs
  # + start: start signal of the upper-level module
  # + xxx_is_done: whether lower-level modules are done
  #
  # ## outputs:
  # + done: done / ready signal of the upper-level module
  # + idle: idle signal of the upper-level module
  #
  # ## states
  # + 00: waiting for start
  #   + done: 0
  #   + idle: 1
  # + 01: waiting for xxx_is_done
  #   + done: 0
  #   + idle: 0
  # + 10: sending done
  #   + done: 1
  #   + idle: 0
  # + 11: register delay for sending done signal
  #   + done: 1
  #   + idle: 0
  #
  # done <- state[1]
  # idle <- state == 00
  #
  # ## state transititions
  # +    -> 00: if reset
  # + 00 -> 00: if start == 0
  # + 00 -> 01: if start == 1
  # + 01 -> 01: if all(*is_done) == 0
  # + 01 -> 10: if all(*is_done) == 1
  # + 10 -> 00: if register_level == 0; countdown <- register_level
  # + 10 -> 11: if register_level > 0; countdown <- register_level
  # + 11 -> 11: if countdown > 1; countdown <- countdown - 1
  # + 11 -> 00: if countdown == 1

  @property
  def state(self) -> ast.Identifier:
    """State of this instance."""
    return ast.Identifier(f'{self.name}__state')

  def set_state(self, new_state: ast.Node) -> ast.NonblockingSubstitution:
    return ast.NonblockingSubstitution(left=self.state, right=new_state)

  def is_state(self, state: ast.Node) -> ast.Eq:
    return ast.Eq(left=self.state, right=state)

  @property
  def start(self) -> ast.Identifier:
    """The handshake start signal.

    This signal is asserted until the ready signal is asserted when the instance
    of task starts.

    Returns:
      The ast.Identifier node of this signal.
    """
    return ast.Identifier(f'{self.name}__{rtl.HANDSHAKE_START}')

  @property
  def done(self) -> ast.Identifier:
    """The handshake done signal.

    This signal is asserted for 1 cycle when the instance of task finishes.

    Returns:
      The ast.Identifier node of this signal.
    """
    return ast.Identifier(f'{self.name}__{rtl.HANDSHAKE_DONE}')

  @property
  def is_done(self) -> ast.Identifier:
    """Signal used to determine the upper-level state."""
    return ast.Identifier(f'{self.name}__is_done')

  @property
  def idle(self) -> ast.Identifier:
    """Whether this isntance is idle."""
    return ast.Identifier(f'{self.name}__{rtl.HANDSHAKE_IDLE}')

  @property
  def ready(self) -> ast.Identifier:
    """Whether this isntance is ready to take new input."""
    return ast.Identifier(f'{self.name}__{rtl.HANDSHAKE_READY}')

  @property
  def _public_handshake_tuples(self) -> Iterator[Tuple[  #
      Union[Type[ast.Reg], Type[ast.Wire]],  # signal_type
      Union[Type[ast.Input], Type[ast.Output]],  # port_type
      str,  # name
  ]]:
    """Public handshake information tuples used for this instance."""
    if self.is_autorun:
      yield (
          ast.Reg,
          ast.Output,
          self.start.name,
      )
    else:
      yield (
          ast.Wire,
          ast.Output,
          self.start.name,
      )
      yield (
          ast.Wire,
          ast.Input,
          rtl.wire_name(self.name, rtl.HANDSHAKE_READY),
      )
      yield (
          ast.Wire,
          ast.Input,
          rtl.wire_name(self.name, rtl.HANDSHAKE_DONE),
      )
      yield (
          ast.Wire,
          ast.Input,
          rtl.wire_name(self.name, rtl.HANDSHAKE_IDLE),
      )

  @property
  def public_handshake_ports(self) -> Iterator[ast.Decl]:
    """Public handshake IO ports used for this instance.

    These include all public IO ports like `ap_start` and `ap_done`.

    Yields:
      ast.Decl of IO ports.
    """
    for _, port_type, name in self._public_handshake_tuples:
      yield port_type(name)

  @property
  def public_handshake_signals(self) -> Iterator[Union[ast.Wire, ast.Reg]]:
    """Public handshake signals used for this instance.

    These include all public signals like `ap_start` and `ap_done`.

    Yields:
      Union[ast.Wire, ast.Reg] of signals.
    """
    for signal_type, _, name in self._public_handshake_tuples:
      yield signal_type(name)

  @property
  def all_handshake_signals(self) -> Iterator[Union[ast.Wire, ast.Reg]]:
    """All handshake signals used for this instance.

    These include both public signals like `ap_start` and `ap_done`, and any
    private state signals.

    Yields:
      Union[ast.Wire, ast.Reg] of signals.
    """
    yield from self.public_handshake_signals
    if not self.is_autorun:
      yield ast.Reg(name=self.state.name, width=ast.make_width(2))

  def get_instance_arg(self, arg: str) -> str:
    if "'d" in arg:  # Constant literals are passed as-is.
      return arg
    return f'{self.name}___{arg}'


class Port:

  def __init__(self, obj):
    self.cat = {
        'istream': Instance.Arg.Cat.ISTREAM,
        'ostream': Instance.Arg.Cat.OSTREAM,
        'scalar': Instance.Arg.Cat.SCALAR,
        'mmap': Instance.Arg.Cat.MMAP,
        'async_mmap': Instance.Arg.Cat.ASYNC_MMAP,
        'hmap': Instance.Arg.Cat.MMAP,
    }[obj['cat']]
    self.name = rtl.sanitize_array_name(obj['name'])
    self.ctype = obj['type']
    self.width = obj['width']
    self.chan_count = obj.get('chan_count')
    self.chan_size = obj.get('chan_size')

  def __str__(self) -> str:
    return ', '.join(f'{k}: {v}' for k, v in self.__dict__.items())
