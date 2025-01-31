import os
import asyncio
import supervisor
import adafruit_logging as logging

from .behaviors import BaseAction, CompositeAction, TapDance, Transparent, LayerSwitchWithAction
from .utils import is_awaitable

logger = logging.getLogger("TapEngine")
if os.getenv('debug'):
	logger.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.WARNING)

try:
	from typing import Optional, List, Dict, Callable, Any
	from keypad import Event
except Exception:
	pass

try:
	from ticks_utils import ticks_diff
except ImportError:
	from micropython import const
	_TICKS_PERIOD = const(1<<29)
	_TICKS_MAX = const(_TICKS_PERIOD-1)
	_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

	def ticks_diff(ticks1, ticks2):
		"Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
		diff = (ticks1 - ticks2) & _TICKS_MAX
		diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
		return diff


# read from input queue and convert discret key events to semantical events
# the key timestamp is generated here for consistency, because the need of triggering long press actions(without release)
class TapEngine:
	def __init__(self,
				key_event_getter: Callable[[], Event],
				*,
				action_map: Optional[Dict[Any, List]] = None,
				default_layer: Any = 0,
				new_event_callback: Optional[Callable[[bool, Any], Any]] = None):
		"""TapEngine for complex key behavior handling

		Args:
			key_event_getter (Callable[[], Event]): A function that generates keypad.Event, and None if no new event(non-blocking)
			action_map (Optional[Dict[Hashable, List], optional): Aka the keymap, can be set later. Defaults to None.
			default_layer (Hashable, optional): The index of the default layer. Defaults to 0.
			new_event_callback (Optional[Callable[[bool, Any], Any]], optional): The function to call to pass the triggered action, can be async. Defaults to None.
		"""

		self.key_event_getter = key_event_getter

		# the default layer is layer 0, determined by `self.layer_tracker[0]`
		self.action_map = action_map

		# state for current undetermined key event
		self.undetermined_key_index = -1
		self.undetermined_key_timestamp = 0
		self.undetermined_key_action = None
		self.undetermined_tap_dance_action_index = 0
		self.undetermined_tap_dance_pressed = False

		self.key_actions = None  # currently triggered key actions
		self._default_layer = default_layer

		self.layer_tracker = None
		self._key_count = 0

		# using this callback to send event notification
		self.new_event_callback = new_event_callback

	def get_key_count(self):
		if self.action_map is None:
			return 0
		return max(map(len, self.action_map.values()))

	def prepare(self):
		key_count = self.get_key_count()

		# initialize/reset key_actions
		if self.key_actions is None:
			self.key_actions = [None] * key_count
		else:
			for i in range(len(self.key_actions)):
				self.key_actions[i] = None

		# initialize/reset layer_tracker
		if self.layer_tracker is None:
			self.layer_tracker = [0] * key_count
		self.layer_tracker.clear()
		self.layer_tracker.append(self._default_layer)

		self._key_count = key_count

		# There's only one undetermined key at most
		# The undetermined key has a special action defined by `Action' class
		self.undetermined_key_index = -1
		self.undetermined_key_timestamp = 0

	def cleanup(self):
		self.key_actions = None
		self.layer_tracker = None
		# TODO: how to clean up?

	def verify_action_map(self):
		if not isinstance(self.action_map, dict):
			raise ValueError('Action map must be a dict')
		key_count = self.get_key_count()
		for k, v in self.action_map.items():
			if not isinstance(v, list) and not isinstance(v, tuple):
				raise ValueError('Action map layers must be a list or tuple, however layer %s is not' % (k,))
			if len(v) != key_count:
				raise ValueError('Action map layers must strictly define %d key actions, however layer %s is not' % (key_count, k))
		if self._default_layer not in self.action_map.keys():
			raise ValueError("default layer(which now is `%s') must be defined in action map" % (self._default_layer,))
		# TODO: more comprehensive checks

	async def run(self):
		self.verify_action_map()
		self.prepare()

		try:
			while True:
				# remember to switch task, put it here so will never forget
				# this is the core task, poll as much as possible
				await asyncio.sleep(0)

				new_event = self.key_event_getter()

				while new_event is not None and new_event.key_number < self._key_count:

					logger.debug("KEY EVENT: index %d, %s", new_event.key_number, new_event.pressed)

					# here we process the undetermined action before the new key event
					if new_event.pressed:
						# triggered by a new different key *press* event
						await self.process_undetermined_action(new_event.timestamp, new_press_index=new_event.key_number)
					else:
						# process undetermined key by timeout
						await self.process_undetermined_action(new_event.timestamp)

					await self.process_new_key_event(new_event.key_number, new_event.pressed, new_event.timestamp)

					# prepare next event
					new_event = self.key_event_getter()

				# no key event or key index out of range
				# process undetermined key by timeout
				await self.process_undetermined_action(supervisor.ticks_ms())

		except asyncio.CancelledError:
			# task cancelled, stop directly, clean everything
			# NOTE: the keys might not released
			self.cleanup()

	async def process_new_key_event(self, key_index, pressed, current_timestamp, *, current_layer_id=-1, action_override=None) -> None:
		#logger.debug("Layer tracker: %s", self.layer_tracker)
		if pressed:
			current_layer = self.layer_tracker[current_layer_id]
			action = self.action_map[current_layer][key_index] if action_override is None else action_override
			if isinstance(action, CompositeAction):
				#logger.debug("CompositeAction pending")
				self.undetermined_key_index = key_index
				self.undetermined_key_timestamp = current_timestamp
				self.undetermined_key_action = action
			elif isinstance(action, TapDance):
				if self.undetermined_key_index == key_index:
					self.undetermined_tap_dance_action_index += 1
					#logger.debug("TapDance pending and index increased to %d", self.undetermined_tap_dance_action_index)
					if len(action) <= self.undetermined_tap_dance_action_index:
						#logger.debug("TapDance limit reached, trigger last keycode")
						await self.notify_key_action(key_index, pressed, action[-1])
						self.undetermined_key_index = -1
				else:
					#logger.debug("TapDance pending, this is first tap")
					self.undetermined_key_index = key_index
					self.undetermined_key_action = action
					self.undetermined_tap_dance_action_index = 0
				self.undetermined_key_timestamp = current_timestamp
				self.undetermined_tap_dance_pressed = True
			elif isinstance(action, Transparent):
				if -current_layer_id <= len(self.layer_tracker):
					# go to next layer
					await self.process_new_key_event(self, key_index, pressed, current_timestamp, current_layer_id=current_layer_id-1)
			else:
				#logger.debug("trigger key %d's action directly", key_index)
				await self.notify_key_action(key_index, pressed, action)
		else:
			#logger.debug("releasing key %d", key_index)
			if self.undetermined_key_index == key_index:
				if isinstance(self.undetermined_key_action, CompositeAction):
					#logger.debug("trigger CompositeAction")
					await self.process_undetermined_action(current_timestamp, pressed=pressed)
				if isinstance(self.undetermined_key_action, TapDance):
					#logger.debug("TapDance released")
					self.undetermined_tap_dance_pressed = False
					await self.process_undetermined_action(current_timestamp, pressed=pressed)
			else:
				await self.notify_key_action(key_index, pressed)

	async def process_undetermined_action(self, current_timestamp, *, new_press_index=-1, pressed=True) -> None:
		# this function will clear `undetermined_key_index` by setting it to -1 if the action is processed/triggered/notified
		if self.undetermined_key_index < 0:
			return  # no undetermined action
		action = self.undetermined_key_action
		time_delta = ticks_diff(current_timestamp, self.undetermined_key_timestamp)
		# TODO: maybe move implementation to each behavior, call with shared state
		if isinstance(action, CompositeAction):
			if new_press_index >= 0:
				# it's determined by a new key press
				if (time_delta < action.tap_term_ms
						and action.tap is not None
						and action.tap_preferred):
					# trigger tap action if defined and preferred
					#logger.debug("trigger CompositeAction tap")
					await self.notify_key_action(self.undetermined_key_index, pressed, action.tap)
					self.undetermined_key_index = -1
				elif time_delta < action.hold_term_ms:
					# switch layer and activate layer+hold action if they are defined
					# trigger hold action if layer is not defined
					# layer change only happens HERE and it's on-demand
					# layer change will be triggered here if action.tap is not defined
					layer_action = LayerSwitchWithAction(action.layer, action.hold)
					#logger.debug("trigger CompositeAction layer+hold")
					await self.notify_key_action(self.undetermined_key_index, pressed, layer_action)
					self.undetermined_key_index = -1
				elif time_delta < action.long_hold_start_ms:
					# no action for this key
					#logger.debug("no action for CompositeAction")
					self.undetermined_key_index = -1
				# long press action shouldn't be determined by a new key press
				# so not processed here
			else:
				# regularly check the time since key with composite action pressed
				if not pressed:
					# now key action determined by a release event
					if time_delta < action.tap_term_ms:
						# trigger tap action
						#logger.debug("trigger CompositeAction tap")
						await self.notify_key_action(self.undetermined_key_index, True, action.tap)
						await self.notify_key_action(self.undetermined_key_index, False)
						self.undetermined_key_index = -1
					elif time_delta < action.hold_term_ms:
						# trigger hold action
						# no need to change layer, since no combo key
						#logger.debug("trigger CompositeAction hold, no change layer")
						await self.notify_key_action(self.undetermined_key_index, True, action.hold)
						await self.notify_key_action(self.undetermined_key_index, False)
						self.undetermined_key_index = -1
					else:
						# simply no action
						#logger.debug("no action for CompositeAction")
						self.undetermined_key_index = -1
				else:
					# check if (long) hold action should be triggered
					if (action.long_hold is None) and (time_delta > action.tap_term_ms):
						#logger.debug("trigger Composite action hold+layer")
						layer_action = LayerSwitchWithAction(action.layer, action.hold)
						await self.notify_key_action(self.undetermined_key_index, pressed, layer_action)
						self.undetermined_key_index = -1
					elif time_delta > action.long_hold_start_ms:
						# trigger long hold action
						#logger.debug("trigger Composite action long hold")
						await self.notify_key_action(self.undetermined_key_index, pressed, action.long_hold)
						self.undetermined_key_index = -1
		elif isinstance(action, TapDance):
			if (new_press_index >= 0) and (new_press_index != self.undetermined_key_index):
				# determined by new press
				# use process_new_key_event instead of notify_key_action to allow wrapping other special actions like CompositeAction
				#logger.debug("trigger TapDance key #%d", self.undetermined_tap_dance_action_index)
				tap_dance_action = action[self.undetermined_tap_dance_action_index]
				last_undetermined = self.undetermined_key_index
				self.undetermined_key_index = -1 # must clear undetermined key
				if self.undetermined_tap_dance_pressed:
					# press down
					await self.process_new_key_event(last_undetermined, True, self.undetermined_key_timestamp, action_override=tap_dance_action)
					await self.process_undetermined_action(current_timestamp, new_press_index=new_press_index, pressed=pressed)
				else:
					# click once
					await self.process_new_key_event(last_undetermined, True, self.undetermined_key_timestamp, action_override=tap_dance_action)
					await self.process_new_key_event(last_undetermined, False, current_timestamp)
			else:
				# check regularly if time since last press exceeds tap_term_ms
				if time_delta > action.tap_term_ms:
					#logger.debug("trigger TapDance key #%d", self.undetermined_tap_dance_action_index)
					tap_dance_action = action[self.undetermined_tap_dance_action_index]
					last_undetermined = self.undetermined_key_index
					self.undetermined_key_index = -1 # must clear undetermined key
					# trigger action
					if self.undetermined_tap_dance_pressed:
						# press down
						await self.process_new_key_event(last_undetermined, True, self.undetermined_key_timestamp, action_override=tap_dance_action)
						await self.process_undetermined_action(current_timestamp, new_press_index=new_press_index, pressed=pressed)
					else:
						# click once
						await self.process_new_key_event(last_undetermined, True, self.undetermined_key_timestamp, action_override=tap_dance_action)
						await self.process_new_key_event(last_undetermined, False, current_timestamp)
		else:
			#logger.warning("Unknown undetermined action: `%s'", action)
			pass

	async def notify_key_action(self, key_index, pressed, action=None) -> None:
		# the specific action is passed/selected by other part of the code
		# this function maintains the following internal states:
		# - key_actions
		# - layer_tracker
		# Note: here all actions are raw actions(not BaseAction or subclass).
		# They are to be defined/processed by the callback owner.
		if pressed:
			if isinstance(action, LayerSwitchWithAction):
				if action.layer is not None:
					#logger.debug("Switching to layer: `%s'", action.layer)
					self._push_layer(action.layer)
				real_action = action.action
			else:
				real_action = action
			self.key_actions[key_index] = action
		else:
			if action is None:
				# use recorded action
				action = self.key_actions[key_index]
			if isinstance(action, LayerSwitchWithAction):
				if action.layer is not None:
					#logger.debug("Removing layer: `%s'", action.layer)
					self._pop_layer(action.layer)
				real_action = action.action
			else:
				real_action = action
			self.key_actions[key_index] = None

		# invoke callback, signal the new key event
		if callable(self.new_event_callback):
			try:
				result = self.new_event_callback(pressed, real_action)
				if is_awaitable(result):
					await result
			except Exception as e:
				logger.error("Action handler failed with exception(%s): %s", e.__class__.__name__, e)

	def _push_layer(self, layer):
		self.layer_tracker.append(layer)

	def _pop_layer(self, layer):
		# here the default layer/0 is kept
		for i in range(len(self.layer_tracker)-1, 0, -1):
			if layer == self.layer_tracker[i]:
				self.layer_tracker.pop(i)
				break

	@property
	def default_layer(self):
		return self._default_layer

	@default_layer.setter
	def default_layer(self, layer):
		if layer not in self.action_map:
			raise ValueError("layer name not in action map!")
		self._default_layer = layer
		if isinstance(self.layer_tracker, list):
			self.layer_tracker[0] = layer


__all__ = [
	"TapEngine",
	"BaseAction",
	"CompositeAction",
	"TapDance",
	"Transparent",
]
