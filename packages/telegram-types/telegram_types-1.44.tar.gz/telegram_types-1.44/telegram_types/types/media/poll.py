from typing import List, Optional

from .base_media import BaseMedia

from telegram_types.enums.poll_type import PollType


class PollOption(BaseMedia):
    text: str
    voter_count: int
    data: str


class Poll(BaseMedia):
    id: str
    question: str
    options: List[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: Optional[bool] = None
    type: Optional[PollType] = None
    allows_multiple_answers: Optional[bool] = None
    chosen_option: Optional[int] = None
