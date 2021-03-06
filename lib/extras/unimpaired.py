# https://github.com/tpope/vim-unimpaired

from sublime_plugin import TextCommand

from NeoVintageous.lib.api.plugin import inputs
from NeoVintageous.lib.api.plugin import NORMAL_MODE
from NeoVintageous.lib.api.plugin import register
from NeoVintageous.lib.api.plugin import ViOperatorDef
from NeoVintageous.lib.api.plugin import VISUAL_MODE


__all__ = [
    '_neovintageous_unimpaired_command'
]


@register(seq='[l', modes=(NORMAL_MODE, VISUAL_MODE))
class _UnimpairedContextPrevious(ViOperatorDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'mode': state.mode,
                'count': state.count,
                'action': 'context_previous'
            }
        }


@register(seq=']l', modes=(NORMAL_MODE, VISUAL_MODE))
class _UnimpairedContextNext(ViOperatorDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'mode': state.mode,
                'count': state.count,
                'action': 'context_next'
            }
        }


@register(seq='[<space>', modes=(NORMAL_MODE,))
class _UnimpairedBlankUp(ViOperatorDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'mode': state.mode,
                'count': state.count,
                'action': 'blank_up'
            }
        }


@register(seq=']<space>', modes=(NORMAL_MODE,))
class _UnimpairedBlankDown(ViOperatorDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'mode': state.mode,
                'count': state.count,
                'action': 'blank_down'
            }
        }


@register(seq='[e', modes=(NORMAL_MODE,))
class _UnimpairedMoveUp(ViOperatorDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'mode': state.mode,
                'count': state.count,
                'action': 'move_up'
            }
        }


@register(seq=']e', modes=(NORMAL_MODE,))
class _UnimpairedMoveDown(ViOperatorDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'mode': state.mode,
                'count': state.count,
                'action': 'move_down'
            }
        }


class _BaseToggleDef(ViOperatorDef):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scroll_into_view = True
        self.updates_xpos = True
        self.input_parser = inputs.parser_def(
            command=inputs.one_char,
            interactive_command=None,
            input_param=None,
            on_done=None,
            type=inputs.input_types.INMEDIATE
        )

    @property
    def accept_input(self):
        return self.inp == ''

    def accept(self, key):
        self._inp = key

        return True


@register(seq='co', modes=(NORMAL_MODE,))
class _UnimpairedToggle(_BaseToggleDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'action': 'toggle_option',
                'key': self.inp
            }
        }


@register(seq='[o', modes=(NORMAL_MODE,))
class _UnimpairedToggleOn(_BaseToggleDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'action': 'toggle_option',
                'key': self.inp,
                'on': True
            }
        }


@register(seq=']o', modes=(NORMAL_MODE,))
class _UnimpairedToggleOff(_BaseToggleDef):
    def translate(self, state):
        return {
            'action': '_neovintageous_unimpaired',
            'action_args': {
                'action': 'toggle_option',
                'key': self.inp,
                'off': True
            }
        }


def _context_previous(view, count):
    for i in range(count):
        view.run_command('sublimelinter_goto_error', {
            'direction': 'previous'
        })


def _context_next(view, count):
    for i in range(count):
        view.run_command('sublimelinter_goto_error', {
            'direction': 'next'
        })


def _move_down(view, count):
    for i in range(count):
        view.run_command('swap_line_down')


def _move_up(view, count):
    for i in range(count):
        view.run_command('swap_line_up')


def _blank_down(view, edit, count):
    end_point = view.size()
    new_sels = []
    for sel in view.sel():
        line = view.line(sel)
        new_sels.append(view.find('[^\\s]', line.begin()).begin())
        view.insert(
            edit,
            line.end() + 1 if line.end() < end_point else end_point,
            '\n' * count
        )

    if new_sels:
        view.sel().clear()
        view.sel().add_all(new_sels)


def _blank_up(view, edit, count):
    new_sels = []
    for sel in view.sel():
        line = view.line(sel)
        new_sels.append(view.find('[^\\s]', line.begin()).begin() + count)
        view.insert(
            edit,
            line.begin() - 1 if line.begin() > 0 else 0,
            '\n' * count
        )

    if new_sels:
        view.sel().clear()
        view.sel().add_all(new_sels)


def _toggle_bool(settings, key, on=False, off=False):
    value = settings.get(key)

    if on:
        if not value:
            settings.set(key, True)
    elif off:
        if value:
            settings.set(key, False)
    else:
        settings.set(key, not value)


def _toggle_value(settings, key, on_value, off_value, on=False, off=False):
    value = settings.get(key)

    if on:
        if value != on_value:
            settings.set(key, on_value)
    elif off:
        if value != off_value:
            settings.set(key, off_value)
    else:
        settings.set(key, off_value if value == on_value else on_value)


def _toggle_list(settings, on=False, off=False):
    # TODO instead of toggle between "all" and "selection" toggle between "all"
    # and whatever the user default is Set to "none" to turn off drawing white
    # space, "selection" to draw only the white space within the selection, and
    # "all" to draw all white space.
    _toggle_value(settings, 'draw_white_space', 'all', 'selection', on, off)


# None = Not implemented
# string = bool toggle
# callable = invoked toggle
_OPTION_TOGGLES = {
    'background': None,
    'crosshairs': None,
    'cursorcolumn': None,
    'cursorline': 'highlight_line',
    'diff': None,
    'hlsearch': None,
    'ignorecase': None,
    'list': _toggle_list,
    'number': 'line_numbers',
    'relativenumber': None,
    'spell': 'spell_check',
    'virtualedit': None,
    'wrap': 'word_wrap',
}


_OPTION_ALIASES = {
    'b': 'background',
    'c': 'cursorline',
    'd': 'diff',
    'h': 'hlsearch',
    'i': 'ignorecase',
    'l': 'list',
    'n': 'number',
    'r': 'relativenumber',
    's': 'spell',
    'u': 'cursorcolumn',
    'v': 'virtualedit',
    'w': 'wrap',
    'x': 'crosshairs',
}


def _toggle_option(view, key, on, off):
    if key in _OPTION_ALIASES:
        key = _OPTION_ALIASES[key]

    if key not in _OPTION_TOGGLES:
        raise ValueError('unknown toggle')

    toggle = _OPTION_TOGGLES[key]

    if not toggle:
        raise ValueError('toggle not implemented')

    settings = view.settings()

    if isinstance(toggle, str):
        _toggle_bool(settings, toggle, on, off)
    else:
        toggle(settings, on, off)


class _neovintageous_unimpaired_command(TextCommand):
    def run(self, edit, action, key=None, on=False, off=False, mode=None, count=1):
        if action == 'move_down':
            # Exchange the current line with [count] lines below it
            _move_down(self.view, count)
        elif action == 'move_up':
            # Exchange the current line with [count] lines above it
            _move_up(self.view, count)
        elif action == 'blank_down':
            # Add [count] blank lines below the cursor
            _blank_down(self.view, edit, count)
        elif action == 'blank_up':
            # Add [count] blank lines above the cursor
            _blank_up(self.view, edit, count)
        elif action == 'context_next':
            # Go to the next [count]  SCM conflict marker or diff/patch hunk
            _context_next(self.view, count)
        elif action == 'context_previous':
            # Go to the previous [count] SCM conflict marker or diff/patch hunk
            _context_previous(self.view, count)
        elif action == 'toggle_option':
            _toggle_option(self.view, key, on, off)
        else:
            raise ValueError('Unknown action')
