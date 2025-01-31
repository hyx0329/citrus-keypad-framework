from collections import namedtuple


try:
	from typing import Any, Optional, Hashable
except ImportError:
	pass


class UndeterminedKeyState:
	def __init__(self) -> None:
		self.key_index = -1
		self.key_timestamp = 0
		self.key_action = None
		self.tap_dance_action_index = 0
		self.tap_dance_pressed = False
	
	def reset(self) -> None:
		self.key_index = -1
		self.key_timestamp = 0


# for easier keymap verification
class BaseAction: pass


class CompositeAction(BaseAction):
	"""Composite key behavior. Used in keymaps for complex behaviors with hold & tap differences or layer changes.
	"""

	def __init__(
			self,
			tap: Any = None, # tap
			hold: Any = None, # hold
			layer: Optional[Hashable] = None, # hold
			long_hold: Any = None, # long hold
			tap_term_ms: int = 220, # NOTE: make it a little bigger than TapDance's tap_term_ms is better
			hold_term_ms: int = 2000,
			long_hold_start_ms: int = 5000,
			tap_preferred: bool = False,
		) -> None:
		"""Composite key behavior. All actions will be directly passed to the callback with the pressing state.
		All pressing & releasing events are emitted. `None` is also a valid user-defined action. Tap, Hold and
		Long Hold are mutually exclusive and only one of them will be triggered.

		Args:
			tap (Any, optional): Action when key is tapped, can be anything. Defaults to None.
			hold (Any, optional): Action when key is held, can be anything. Defaults to None.
			layer (Hashable, optional): The layer changed to, must match keymap layer index. Defaults to None, means no change.
			long_hold (Any, optional): Action when key is held for a looooong time. Defaults to None.
			tap_term_ms (int, optional): Before this time, the tap action is triggered. Defaults to 200(ms).
			hold_term_ms (int, optional): Before this time, the hold action is triggered. Defaults to 2000(ms).
			long_hold_start_ms (int, optional): After this time, the long hold action is triggered. Defaults to 5000(ms).
			tap_preferred (bool, optional): Whether tap has priority over hold action when multiple keys pressed. Defaults to False. Note if tap is defined and hold is not, the tap is always prefered, vice-versa.

		Raises:
			ValueError: When tap_term_ms < hold_term_ms <= long_hold_start_ms is not satisfied.
		"""		
		if not (tap_term_ms < hold_term_ms <= long_hold_start_ms):
			raise ValueError("tap_term_ms < hold_term_ms <= long_hold_start_ms must be satisfied")
		self.tap = tap
		self.hold = hold
		self.layer = layer
		self.long_hold = long_hold
		self.tap_term_ms = tap_term_ms
		self.hold_term_ms = hold_term_ms
		self.long_hold_start_ms = long_hold_start_ms
		self.tap_preferred = tap_preferred
		# short path
		if self.tap is not None and self.layer is None and self.hold is None:
			self.tap_preferred = True
		elif self.tap is None:
			self.tap_preferred = False


class TapDance(tuple, BaseAction):
	def __init__(self, *args, tap_term_ms: int = 200):
		"""TapDance behavior. The action is determined by the tap count of the key.

		Args:
			*args (Iterable): The sequence of actions.
			tap_term_ms (int, optional): Maximum interval between taps, the actual action is determined if time exceeded. Defaults to 200(ms).
		"""		
		super().__init__(args)
		self.tap_term_ms = tap_term_ms


# A special one for exposing layers under current layer
class Transparent(BaseAction):

	_instance = None

	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance


# This is used internally, users should ONLY use CompositeAction for complex actions
LayerSwitchWithAction = namedtuple("LayerAction", ["layer", "action"])
