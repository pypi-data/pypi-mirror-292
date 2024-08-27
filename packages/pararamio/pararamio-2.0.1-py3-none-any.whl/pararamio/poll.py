from typing import TYPE_CHECKING, Any, Callable, Dict, List

from pararamio.exceptions import (
    PararamioRequestException,
    PararamioServerResponseException,
    PararamioValidationException,
)

if TYPE_CHECKING:
    from pararamio.client import Pararamio
    from .chat import Chat

__all__ = ('Poll',)


ATTR_FORMATTERS: Dict[str, Callable[[dict, str], Any]] = {}


class PollOption:
    """
    Represents an option within a poll.

    :ivar id: The unique identifier for the poll option.
    :vartype id: int
    :ivar text: The text description of the poll option.
    :vartype text: str
    :ivar count: The number of votes received for this poll option.
    :vartype count: int
    :ivar vote_users: A list of user identifiers who voted for this option.
    :vartype vote_users: List[int]
    """
    id: int
    text: str
    count: int
    vote_users: List[int]

    def __init__(self, id: int, text: str, count: int, vote_users: List[int]) -> None:
        self.id = id
        self.text = text
        self.count = count
        self.vote_users = vote_users

    @classmethod
    def from_response_data(cls, data: Dict[str, Any]) -> 'PollOption':
        """
        Create a PollOption object from the response data.

        :param data: A dictionary containing the response data.
        :type data: Dict[str, Any]
        :return: An instance of PollOption class.
        :rtype: PollOption
        :raises PararamioServerResponseException: If any required field is missing in the response data.
        """
        for field in cls.__annotations__:
            if field not in data:
                raise PararamioServerResponseException(
                    f'invalid server vote option response, missing {field}',
                    data,
                )
        return cls(**data)


class Poll:
    """
    Represents a poll object.
    :ivar vote_uid: A unique identifier for the poll.
    :vartype vote_uid: str
    :ivar chat_id: The identifier of the chat where the poll is conducted.
    :vartype chat_id: int
    :ivar anonymous: A boolean indicating whether the poll is anonymous or not.
    :vartype anonymous: bool
    :ivar mode: Options select mode of the poll ('one' for single or 'more' for multi).
    :vartype mode: str
    :ivar options: A list of PollOption objects representing the available poll options.
    :vartype options: List[PollOption]
    :ivar question: The question of the poll.
    :vartype question: str
    :ivar total_user: The total number of users who participated in the poll.
    :vartype total_user: int
    :ivar total_answer: The total number of responses received in the poll.
    :vartype total_answer: int
    :ivar user_id: The identifier of the user who created the poll.
    :vartype user_id: int
    """
    _client: 'Pararamio'
    _data: Dict[str, Any]

    vote_uid: str
    chat_id: int
    anonymous: bool
    mode: str
    options: List[PollOption]
    question: str
    total_user: int
    total_answer: int
    user_id: int

    def __init__(self, client: 'Pararamio', vote_uid: str, **kwargs) -> None:
        self._client = client
        self.vote_uid = vote_uid
        self._data = {**kwargs, 'vote_uid': vote_uid}

    def __getattr__(self, name: str) -> Any:
        fmt_fnc = ATTR_FORMATTERS.get(name, None)
        if fmt_fnc:
            return fmt_fnc(self._data, name)
        return self._data[name]

    def __str__(self) -> str:
        return self.question

    @property
    def client(self) -> 'Pararamio':
        return self._client

    def _update(self, response: Dict[str, Any]) -> 'Poll':
        """
        Update the Poll object with the response data.

        :param response: A dictionary containing the response data.
        :type response: Dict[str, Any]
        :return: The updated Poll object.
        :rtype: Poll
        :raises PararamioServerResponseException: If 'vote' key is not present in the response.
        """
        if 'vote' not in response:
            raise PararamioServerResponseException(
                f'failed to load data for vote {self.vote_uid} in chat {self._chat.id}',
                response,
            )
        self._data = {
            k: v if k != 'options' else [PollOption.from_response_data(opt) for opt in v]
            for k, v in response['vote'].items()
        }
        return self

    def load(self) -> 'Poll':
        """
        Load the poll's data from the pararam server.

        :return: The updated instance of the poll.
        :rtype: Poll
        """
        res = self._client.api_get(f'/msg/vote/{self.vote_uid}')
        return self._update(res)

    @classmethod
    def create(cls, chat: 'Chat', question: str, mode: str, anonymous: bool, options: List[str]) -> 'Poll':
        """
        Create a new poll in the specified pararam chat.

        :param chat: The chat in which the poll will be created.
        :type chat: Chat
        :param question: The question for the poll.
        :type question: str
        :param mode: Options select mode of the poll ('one' for single or 'more' for multi).
        :type mode: str
        :param anonymous: Whether the poll should be anonymous or not.
        :type anonymous: bool
        :param options: The list of options for the poll.
        :type options: List[str]
        :return: The created Poll object.
        :rtype: Poll
        :raises PararamioRequestException: If the request to create the poll fails.
        """
        res = chat.client.api_post(
            '/msg/vote',
            {
                'chat_id': chat.id,
                'question': question,
                'options': options,
                'mode': mode,
                'anonymous': anonymous,
            }
        )
        if not res:
            raise PararamioRequestException('Failed to create post')
        return cls(chat.client, res['vote_uid']).load()

    def _vote(self, option_ids: List[int]) -> 'Poll':
        """
        Vote on the poll by selecting the given option IDs.

        :param option_ids: A list of integers representing the IDs of the options to vote for.
        :type option_ids: List[int]
        :return: The updated Poll object after voting.
        :rtype: Poll
        :raises PararamioValidationException: If any of the option IDs are incorrect.
        """
        ids_ = [opt.id for opt in self.options]
        if not all(opt_id in ids_ for opt_id in option_ids):
            raise PararamioValidationException('incorrect option')
        res = self._client.api_put(
            f'/msg/vote/{self.vote_uid}',
            {
                'variants': option_ids,
            }
        )
        return self._update(res)

    def vote(self, option_id: int) -> 'Poll':
        """
        Vote for a specific option in the poll.

        :param option_id: The ID of the option to vote for.
        :type option_id: int
        :return: The updated Poll object after voting.
        :rtype: Poll
        :raises PararamioValidationException: If the option_id is invalid.
        """
        return self._vote([option_id])

    def vote_multi(self, option_ids: List[int]) -> 'Poll':
        """
        Vote for multiple options in a poll.

        :param option_ids: A list of integers representing the IDs of the options to vote for.
        :type option_ids: List[int]
        :return: The updated instance of the poll.
        :rtype: Poll
        :raises PararamioValidationException: If the poll mode is not 'more' or if any of the option IDs are incorrect.
        """
        if self.mode != 'more':
            raise PararamioValidationException(f'incorrect poll mode ({self.mode}) for multi voting')
        return self._vote(option_ids)

    def retract(self) -> 'Poll':
        """
        Retracts the vote from the poll.

        :return: The updated instance of the poll.
        :rtype: Poll
        """
        return self._vote([])
