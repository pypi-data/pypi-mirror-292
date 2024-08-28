"""An example of a custom rule implemented through the plugin system.

This uses the rules API supported from 0.4.0 onwards.
"""

from sqlfluff.core.rules import (
    BaseRule,
    LintResult,
    RuleContext
)
from sqlfluff.utils.functional import FunctionalContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_EasyQL_L002(BaseRule):
    """JOIN and ON keyword should be in the same line.
    """
    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"join_clause"})

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)

    def _eval(self, context: RuleContext):
        """We should not JOIN .. ON differnet lines."""
        on_appeared = False
        for seg in context.segment.segments:
            if seg.raw.lower() == "on":
                on_appeared = True
            if seg.raw == "\n" and not on_appeared:
                desc = "Join and ON keyword should be at the same line."
                return LintResult(
                    anchor=seg,
                    description=desc
                )


class Rule_EasyQL_L003(BaseRule):
    """Prohibit the use of 'WHERE 1=1' in queries."""
    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"where_clause"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext):
        text_segments = (
            FunctionalContext(context)
            .segment.children()
        )

        for idx, seg in enumerate(text_segments):
            # Look for the pattern '1=1'
            if "1=1" in seg.raw_upper.replace(" ", ""):
                return LintResult(anchor=seg)
        return None
