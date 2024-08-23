from abc import abstractmethod
from typing import Callable, override

from polymat.sparserepr.sparsereprmixin import SparseReprMixin
from polymat.state import State
from polymat.expressiontree.expressiontreemixin import SingleChildExpressionTreeMixin
from polymat.utils.getstacklines import FrameSummaryMixin, to_operator_exception

class AssertShapeMixin(FrameSummaryMixin, SingleChildExpressionTreeMixin):

    @property
    @abstractmethod
    def fn(self) -> Callable[[int, int], bool]: ...

    @property
    @abstractmethod
    def msg(self) -> Callable[[int, int], str]: ...

    def __str__(self):
        return str(self.child)

    @override
    def apply(self, state: State) -> tuple[State, SparseReprMixin]:
        state, child = self.child.apply(state=state)

        if not self.fn(*child.shape):
            raise AssertionError(
                to_operator_exception(
                    message=self.msg(*child.shape),
                    stack=self.stack,
                )
            )

        return state, child
