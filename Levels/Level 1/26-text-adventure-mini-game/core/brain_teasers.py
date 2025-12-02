"""Brain teaser puzzle system for standalone puzzles."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from .logging_utils import log_warning

if TYPE_CHECKING:
    from .world import World
    from .entities.player import Player


class BrainTeaserType(Enum):
    """Types of brain teaser puzzles."""

    RIDDLE = "riddle"
    WORD_SCRAMBLE = "word_scramble"
    NUMBER_SEQUENCE = "number_sequence"
    PATTERN_MATCH = "pattern_match"
    SIMON_SAYS = "simon_says"
    LOCK_COMBINATION = "lock_combination"
    SLIDING_TILES = "sliding_tiles"


@dataclass
class Riddle:
    """A text riddle with answer."""

    riddle_id: str
    question: str
    answer: str  # Correct answer (case-insensitive match)
    alternatives: List[str] = field(default_factory=list)  # Also accepted
    hint: str = ""
    difficulty: int = 1  # 1-5


@dataclass
class WordScramble:
    """Unscramble letters to form a word."""

    puzzle_id: str
    word: str
    scrambled: str  # Pre-scrambled version
    hint: str = ""
    category: str = ""  # "animal", "item", "place"


@dataclass
class NumberSequence:
    """Find the next number in a sequence."""

    puzzle_id: str
    sequence: List[int]  # Numbers shown
    answer: int  # Next number
    pattern_description: str = ""  # For solution reveal


@dataclass
class PatternMatch:
    """Visual pattern matching - find the odd one out or complete pattern."""

    puzzle_id: str
    grid: List[List[str]]  # Symbols or sprite IDs
    answer_position: Tuple[int, int]  # Correct selection
    puzzle_type: str = "odd_one_out"  # "odd_one_out" or "complete_sequence"


@dataclass
class SimonSays:
    """Memory sequence game."""

    puzzle_id: str
    sequence_length: int
    colors: List[str] = field(default_factory=lambda: ["red", "blue", "green", "yellow"])
    generated_sequence: List[str] = field(default_factory=list)


@dataclass
class LockCombination:
    """Dial-based combination lock."""

    puzzle_id: str
    combination: List[int]  # e.g., [3, 7, 2]
    num_dials: int = 3
    max_value: int = 9
    clues: List[str] = field(default_factory=list)


@dataclass
class BrainTeaser:
    """Wrapper for any brain teaser type."""

    teaser_id: str
    teaser_type: BrainTeaserType
    name: str
    data: Any  # Riddle, WordScramble, etc.
    rewards: Dict[str, Any] = field(default_factory=dict)  # gold, items, flags
    attempts_allowed: int = 3  # 0 = unlimited
    solved: bool = False


class BrainTeaserManager:
    """Manages all brain teaser puzzles.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "brain_teasers"

    def __init__(self, teasers: Dict[str, BrainTeaser]):
        """Initialize manager with brain teaser definitions.

        Args:
            teasers: Dictionary mapping teaser_id to BrainTeaser objects
        """
        self.teasers = teasers
        self.solved_teasers: Set[str] = set()
        self.attempts: Dict[str, int] = {}  # teaser_id -> attempts used

    def get_teaser(self, teaser_id: str) -> Optional[BrainTeaser]:
        """Get a brain teaser by ID.

        Args:
            teaser_id: ID of the teaser to retrieve

        Returns:
            BrainTeaser if found, None otherwise
        """
        return self.teasers.get(teaser_id)

    def check_answer(self, teaser_id: str, answer: Any) -> Tuple[bool, str]:
        """Check if answer is correct.

        Args:
            teaser_id: ID of the teaser
            answer: Player's answer (type depends on puzzle type)

        Returns:
            Tuple of (is_correct, feedback_message)
        """
        teaser = self.get_teaser(teaser_id)
        if not teaser:
            return (False, "Puzzle not found.")

        if teaser.solved:
            return (True, "This puzzle is already solved.")

        # Check attempts
        if teaser.attempts_allowed > 0:
            attempts_used = self.attempts.get(teaser_id, 0)
            if attempts_used >= teaser.attempts_allowed:
                return (False, "No attempts remaining.")

        # Type-specific validation
        if teaser.teaser_type == BrainTeaserType.RIDDLE:
            return self._check_riddle(teaser, answer)
        elif teaser.teaser_type == BrainTeaserType.WORD_SCRAMBLE:
            return self._check_word_scramble(teaser, answer)
        elif teaser.teaser_type == BrainTeaserType.NUMBER_SEQUENCE:
            return self._check_number_sequence(teaser, answer)
        elif teaser.teaser_type == BrainTeaserType.PATTERN_MATCH:
            return self._check_pattern_match(teaser, answer)
        elif teaser.teaser_type == BrainTeaserType.SIMON_SAYS:
            return self._check_simon_says(teaser, answer)
        elif teaser.teaser_type == BrainTeaserType.LOCK_COMBINATION:
            return self._check_lock_combination(teaser, answer)
        elif teaser.teaser_type == BrainTeaserType.SLIDING_TILES:
            return self._check_sliding_tiles(teaser, answer)
        else:
            return (False, "Unknown puzzle type.")

    def _check_riddle(self, teaser: BrainTeaser, answer: str) -> Tuple[bool, str]:
        """Check riddle answer."""
        if not isinstance(answer, str):
            return (False, "Answer must be text.")
        riddle: Riddle = teaser.data
        answer_lower = answer.strip().lower()
        correct_lower = riddle.answer.lower()
        if answer_lower == correct_lower:
            return (True, "Correct!")
        for alt in riddle.alternatives:
            if answer_lower == alt.lower():
                return (True, "Correct!")
        # Increment attempts
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect. Try again.")

    def _check_word_scramble(self, teaser: BrainTeaser, answer: str) -> Tuple[bool, str]:
        """Check word scramble answer."""
        if not isinstance(answer, str):
            return (False, "Answer must be text.")
        scramble: WordScramble = teaser.data
        if answer.strip().lower() == scramble.word.lower():
            return (True, "Correct!")
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect. Try again.")

    def _check_number_sequence(self, teaser: BrainTeaser, answer: int) -> Tuple[bool, str]:
        """Check number sequence answer."""
        if not isinstance(answer, int):
            return (False, "Answer must be a number.")
        sequence: NumberSequence = teaser.data
        if answer == sequence.answer:
            return (True, "Correct!")
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect. Try again.")

    def _check_pattern_match(self, teaser: BrainTeaser, answer: Tuple[int, int]) -> Tuple[bool, str]:
        """Check pattern match answer."""
        if not isinstance(answer, tuple) or len(answer) != 2:
            return (False, "Answer must be a position (x, y).")
        pattern: PatternMatch = teaser.data
        if answer == pattern.answer_position:
            return (True, "Correct!")
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect. Try again.")

    def _check_simon_says(self, teaser: BrainTeaser, answer: List[str]) -> Tuple[bool, str]:
        """Check Simon Says sequence."""
        if not isinstance(answer, list):
            return (False, "Answer must be a sequence.")
        simon: SimonSays = teaser.data
        if not simon.generated_sequence:
            self._increment_attempts(teaser.teaser_id)
            return (False, "Sequence not ready.")
        if len(answer) != len(simon.generated_sequence):
            self._increment_attempts(teaser.teaser_id)
            return (False, "Incorrect sequence.")
        if answer == simon.generated_sequence:
            return (True, "Correct!")
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect sequence.")

    def _check_lock_combination(self, teaser: BrainTeaser, answer: List[int]) -> Tuple[bool, str]:
        """Check lock combination."""
        if not isinstance(answer, list):
            return (False, "Answer must be a list of numbers.")
        lock: LockCombination = teaser.data
        if answer == lock.combination:
            return (True, "Correct! The lock opens.")
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect combination. Try again.")

    def _check_sliding_tiles(self, teaser: BrainTeaser, answer: List[List[str]]) -> Tuple[bool, str]:
        """Check sliding tiles solution."""
        if not isinstance(answer, list):
            return (False, "Answer must be a grid.")
        target = None
        if isinstance(teaser.data, dict):
            target = teaser.data.get("solution")
        if target is None and hasattr(teaser.data, "solution"):
            target = getattr(teaser.data, "solution")
        if target is None:
            self._increment_attempts(teaser.teaser_id)
            return (False, "No solution defined.")
        if answer == target:
            return (True, "Correct!")
        self._increment_attempts(teaser.teaser_id)
        return (False, "Incorrect arrangement.")

    def _increment_attempts(self, teaser_id: str) -> None:
        """Increment attempt counter for a teaser."""
        self.attempts[teaser_id] = self.attempts.get(teaser_id, 0) + 1

    def mark_solved(self, teaser_id: str) -> None:
        """Mark teaser as solved.

        Args:
            teaser_id: ID of the teaser to mark as solved
        """
        teaser = self.get_teaser(teaser_id)
        if teaser:
            teaser.solved = True
            self.solved_teasers.add(teaser_id)

    def get_remaining_attempts(self, teaser_id: str) -> int:
        """Get remaining attempts for a teaser.

        Args:
            teaser_id: ID of the teaser

        Returns:
            Number of remaining attempts, or -1 if unlimited
        """
        teaser = self.get_teaser(teaser_id)
        if not teaser:
            return 0
        if teaser.attempts_allowed == 0:
            return -1  # Unlimited
        attempts_used = self.attempts.get(teaser_id, 0)
        return max(0, teaser.attempts_allowed - attempts_used)

    def serialize(self) -> Dict:
        """Serialize state for saving.

        Returns:
            Dictionary containing solved teasers and attempt counts
        """
        return {
            "solved_teasers": list(self.solved_teasers),
            "attempts": self.attempts.copy(),
        }

    @classmethod
    def deserialize(cls, data: Dict, teaser_definitions: Dict[str, BrainTeaser]) -> "BrainTeaserManager":
        """Deserialize from save data.

        Args:
            data: Serialized data dictionary
            teaser_definitions: Dictionary of BrainTeaser definitions

        Returns:
            BrainTeaserManager instance with restored state
        """
        manager = cls(teaser_definitions)
        manager.solved_teasers = set(data.get("solved_teasers", []))
        manager.attempts = data.get("attempts", {})

        # Restore solved state on teasers
        for teaser_id in manager.solved_teasers:
            if teaser_id in manager.teasers:
                manager.teasers[teaser_id].solved = True

        return manager

    def deserialize_into(self, data: Dict) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.solved_teasers = set(data.get("solved_teasers", []))
        self.attempts = data.get("attempts", {})

        # Restore solved state on teasers
        for teaser_id in self.solved_teasers:
            if teaser_id in self.teasers:
                self.teasers[teaser_id].solved = True
