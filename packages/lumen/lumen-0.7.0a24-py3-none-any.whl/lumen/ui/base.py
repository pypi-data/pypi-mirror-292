import panel as pn
import param  # type: ignore

from panel.reactive import ReactiveHTML
from panel.viewable import Viewable

from .fast import FastDivider


class Wizard(ReactiveHTML):

    items = param.List(precedence=-1)

    current = param.Parameter()

    previous_disable = param.Boolean(True)

    next_disable = param.Boolean(True)

    spec = param.Dict(precedence=-1)

    _template = """
    <div id="wizard-content" style="display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
    <div id="wizard" style="overflow: clip auto; padding-right: 1em; height: 100%;">${current}</div>
    <div id="wizard-footer" style="margin-top: auto;">
      <fast-divider style="margin: 1em 0;"></fast-divider>
      <div style="display: flex; flex-direction: row; justify-content: space-between; align-items: center;">
      <fast-flipper id="previous" onclick="${_previous}" direction="previous" disabled=${previous_disable}>
      </fast-flipper>
      <fast-flipper id="next" onclick="${_next}" disabled=${next_disable}>
      </fast-flipper>
      </div>
    </div>
    </div>
    """

    def __init__(self, **params):
        super().__init__(**params)
        for item in self.items:
            item.param.watch(self._ready, 'ready')
        self.items[0].active = True
        self._current = 0
        self.current = self.items[0]
        self.preview = pn.pane.JSON(self.spec, depth=-1, sizing_mode='stretch_both')
        self._modal_content = [
            '# Dashboard specification preview',
            FastDivider(),
            self.preview
        ]

    def _ready(self, event):
        self.next_disable = not event.obj.ready
        if event.obj.auto_advance:
            self._next()

    def open_modal(self):
        from .state import state
        self.preview.object = dict(state.spec)
        if state.modal.objects == [self.preview]:
            state.template.open_modal()
            return
        state.modal.loading = True
        state.template.open_modal()
        state.modal[:] = self._modal_content
        state.modal.loading = False

    def _previous(self, event=None):
        if self.previous_disable:
            return
        self._current -= 1
        self.current.active = False
        item = self.items[self._current]
        item.active = True
        self.current = item
        self.next_disable = False
        if self._current == 0:
            self.previous_disable = True

    def _next(self, event=None):
        if self.next_disable:
            return
        self.loading = True
        self._current += 1
        item = self.items[self._current]
        self.current.active = False
        item.active = True
        self.current = item
        self.previous_disable = False
        if self._current == (len(self.items)-1):
            self.next_disable = True
        self.loading = False

    def select(self, selector=None):
        items = super().select(selector)
        items += [o for v in self.items if isinstance(v, Viewable) for o in v.select(selector)]
        return items


class WizardItem(ReactiveHTML):

    active = param.Boolean(default=False)

    auto_advance = param.Boolean(default=False)

    sizing_mode = param.String(default='stretch_width', readonly=True)

    ready = param.Boolean(default=False)

    spec = param.Dict(precedence=-1)

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        spec_params = [p for p in self.param if self.param[p].precedence == 1]
        if spec_params:
            self.param.watch(self._update_spec, spec_params)

    def _update_spec(self, *events):
        pass

    def select(self, selector=None):
        items = super().select(selector)
        for values in self.param.objects().values():
            if isinstance(values, (list, dict)):
                values = values.values() if isinstance(values, dict) else values
                items += [o for v in values if isinstance(v, Viewable) for o in v.select(selector)]
            elif isinstance(values, Viewable):
                items += values.select(selector)
        return items
