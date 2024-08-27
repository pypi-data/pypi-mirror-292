import logging
import mimetypes
import os
from http.cookiejar import CookieJar, FileCookieJar, LoadError, MozillaCookieJar
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, Iterable, List, Optional, Tuple, Union

from pararamio._types import ProfileTypeT, SecondStepFnT
from pararamio.chat import Chat
from pararamio.constants import XSRF_HEADER_NAME
from pararamio.exceptions import PararamioAuthenticationException, PararamioHTTPRequestException, PararamioValidationException
from pararamio.file import File
from pararamio.group import Group
from pararamio.post import Post
from pararamio.user import User
from pararamio.utils.authentication import authenticate, do_second_step, do_second_step_with_code, get_xsrf_token
from pararamio.utils.helpers import check_login_opts, get_empty_vars, lazy_loader, unescape_dict
from pararamio.utils.requests import api_request, delete_file, download_file, xupload_file

__all__ = ('Pararamio',)
log = logging.getLogger('pararamio.client')


class Pararamio:
    _login: Optional[str]
    _password: Optional[str]
    _key: Optional[str]
    _authenticated: bool
    _cookie: Union[CookieJar, FileCookieJar]
    __profile: Optional[dict]
    __headers: Dict[str, str]
    __user: dict

    def __init__(self, login: str = None, password: str = None, key: str = None, cookie: CookieJar = None, cookie_path: str = None,
                 ignore_broken_cookie: bool = False):
        self._login = login
        self._password = password
        self._key = key
        self.__headers = {}
        self.__profile = None
        self.__user = {}
        self._authenticated = False
        if cookie is not None:
            self._cookie = cookie
        elif cookie_path is not None:
            self._cookie = MozillaCookieJar(cookie_path)
            if os.path.exists(cookie_path):
                if not os.path.isfile(cookie_path):
                    raise OSError(f'path {cookie_path} is directory')
                if not os.access(cookie_path, os.R_OK):
                    raise OSError(f'file {cookie_path} is not readable')
                if not os.access(cookie_path, os.W_OK):
                    raise OSError(f'file {cookie_path} is not writable')
                try:
                    self._cookie.load(ignore_discard=True)
                    self._authenticated = True
                except LoadError as e:
                    log.error('failed to load cookie from file %s', cookie_path)
                    if not ignore_broken_cookie:
                        raise OSError(e)
        else:
            self._cookie = CookieJar()
        for cj in self._cookie:
            if cj.name == '_xsrf':
                self.__headers[XSRF_HEADER_NAME] = str(cj.value)
                break

    @property
    def cookies(self) -> Union[CookieJar, FileCookieJar]:
        if not self._authenticated:
            self.authenticate()
        return self._cookie

    @property
    def headers(self) -> Dict[str, str]:
        if not self._authenticated:
            self.authenticate()
        return self.__headers

    def _save_cookie(self) -> None:
        if isinstance(self._cookie, FileCookieJar):
            self._cookie.save(ignore_discard=True)

    def _profile(self, raise_on_error: bool = False) -> 'ProfileTypeT':
        return unescape_dict(self.api_get('/user/me', raise_on_error=raise_on_error), keys=['name'])

    def _do_auth(
        self, login: str, password: str, cookie_jar: CookieJar, headers: Dict[str, str], second_step_fn: SecondStepFnT,
        second_step_arg: str, ) -> None:
        self._authenticated, user, xsrf = authenticate(login, password, cookie_jar, headers, second_step_fn, second_step_arg)
        if self._authenticated:
            self.__user = user
            self.__headers[XSRF_HEADER_NAME] = xsrf
            self._save_cookie()

    def _authenticate(self, second_step_fn: SecondStepFnT, second_step_arg: str, login: str = None, password: str = None) -> bool:
        login = login or self._login
        password = password or self._password
        if not check_login_opts(login, password):
            raise PararamioAuthenticationException(f'{get_empty_vars(login=login, password=password)} must be set and not empty')
        if not self._cookie:
            self._do_auth(login, password, self._cookie, self.__headers, second_step_fn, second_step_arg)
        try:
            self._authenticated = True
            self._profile(raise_on_error=True)
        except PararamioHTTPRequestException:
            self._authenticated = False
            self._do_auth(login, password, self._cookie, self.__headers, second_step_fn, second_step_arg)
        return self._authenticated

    def authenticate(self, login: str = None, password: str = None, key: str = None) -> bool:
        """
        Authenticate client with totp key
        :param login: pararam login
        :param password: pararam password
        :param key: 16 chars second factor key to generate one time code
        :return: True if authentication success
        """
        key = key or self._key
        if not key:
            raise PararamioAuthenticationException('key must be set and not empty')
        return self._authenticate(do_second_step, key, login, password)

    def authenticate_with_code(self, code: str, login: str = None, password: str = None) -> bool:
        """
        Authenticate client with generated TFA code
        :param login: pararam login
        :param password: pararam password
        :param code: 6 digits code
        :return: True if authentication success
        """
        if not code:
            raise PararamioAuthenticationException('code must be set and not empty')
        return self._authenticate(do_second_step_with_code, code, login, password)

    def _api_request(self, url: str, method: str = 'GET', data: dict = None, callback: Callable = lambda rsp: rsp, raise_on_error: bool = False) -> Any:
        if not self._authenticated:
            self.authenticate()
        if not self.__headers.get(XSRF_HEADER_NAME, None):
            self.__headers[XSRF_HEADER_NAME] = get_xsrf_token(self._cookie)
            self._save_cookie()
        try:
            return callback(api_request(url, method, data, cookie_jar=self._cookie, headers=self.__headers))
        except PararamioHTTPRequestException as e:
            if raise_on_error:
                raise
            if e.code == 401:
                self._authenticated = False
                return self._api_request(url=url, method=method, data=data, callback=callback, raise_on_error=True)
            message = e.message
            if message == 'xsrf':
                log.info('xsrf is expire, invalid or was not set, trying to get new one')
                self.__headers[XSRF_HEADER_NAME] = ''
                return self._api_request(url=url, method=method, data=data, callback=callback, raise_on_error=True)
            raise

    def api_get(self, url: str, raise_on_error: bool = False) -> dict:
        return self._api_request(url, raise_on_error=raise_on_error)

    def api_post(self, url: str, data: Dict[Any, Any] = None, raise_on_error: bool = False) -> dict:
        return self._api_request(url, method='POST', data=data, raise_on_error=raise_on_error)

    def api_put(self, url: str, data: Dict[Any, Any] = None, raise_on_error: bool = False) -> dict:
        return self._api_request(url, method='PUT', data=data, raise_on_error=raise_on_error)

    def api_delete(self, url: str, data: Dict[Any, Any] = None, raise_on_error: bool = False) -> dict:
        return self._api_request(url, method='DELETE', data=data, raise_on_error=raise_on_error)

    def _upload_file(
        self,
        file: BinaryIO,
        chat_id: int,
        filename: str = None,
        type_: str = None,
        organization_id: int = None,
        reply_no: int = None,
        quote_range: str = None
    ) -> Tuple[dict, dict]:
        if type_ is None and not filename:
            raise PararamioValidationException('filename must be set when type is None')
        if not self._authenticated:
            self.authenticate()
        if not self.__headers.get(XSRF_HEADER_NAME, None):
            self.__headers[XSRF_HEADER_NAME] = get_xsrf_token(self._cookie)
        if type_ == 'organization_avatar' and organization_id is None:
            raise PararamioValidationException('organization_id must be set when type is organization_avatar')
        if type_ == 'chat_avatar' and chat_id is None:
            raise PararamioValidationException('chat_id must be set when type is chat_avatar')
        if type_ is None:
            if not mimetypes.inited:
                mimetypes.init(files=os.environ.get('PARARAMIO_MIME_TYPES_PATH', None))
            type_ = mimetypes.guess_type(filename)[0]
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0, 0)
        fields = [
            ('type', type_),
            ('filename', filename),
            ('size', file_size),
            ('chat_id', chat_id),
            ('organization_id', organization_id),
            ('reply_no', reply_no),
            ('quote_range', quote_range)
        ]
        return xupload_file(fp=file, fields=fields, headers=self.__headers, cookie_jar=self._cookie), dict(fields)

    def upload_file(
        self,
        file: Union[str, BytesIO, Path],
        chat_id: int,
        filename: str = None,
        reply_no: int = None,
        quote_range: str = None
    ) -> File:
        if isinstance(file, (str, Path)):
            filename = filename or os.path.basename(file)
            with open(file, 'rb') as f:
                res, extra = self._upload_file(file=f, chat_id=chat_id, filename=filename, reply_no=reply_no, quote_range=quote_range)
        else:
            res, extra = self._upload_file(file=file, chat_id=chat_id, filename=filename, reply_no=reply_no, quote_range=quote_range)
        return File(self, guid=res['guid'], mime_type=extra['type'], **extra)

    def delete_file(self, guid: str) -> dict:
        return delete_file(guid, headers=self.__headers, cookie_jar=self._cookie)

    def download_file(self, guid: str, filename: str) -> BytesIO:
        return download_file(guid, filename, headers=self.__headers, cookie_jar=self._cookie)

    @property
    def profile(self) -> dict:
        if not self.__profile:
            self.__profile = self._profile()
        return self.__profile

    def search_user(self, query: str) -> List[User]:
        return User.search(self, query)

    def search_group(self, query: str) -> List[Group]:
        return Group.search(self, query)

    def search_posts(self, query: str, order_type: str = 'time', page: int = 1, chat_id: int = None, limit: Optional[int] = None) -> Tuple[int, Iterable[Post]]:
        return Chat.post_search(self, query, order_type=order_type, page=page, chat_id=chat_id, limit=limit)

    def list_chats(self) -> Iterable:
        url = '/core/chat/sync'
        chats_per_load = 50
        ids = self.api_get(url).get('chats', [])
        return lazy_loader(self, ids, Chat.load_chats, per_load=chats_per_load)

    def post_private_message_by_user_email(self, email: str, text: str) -> Post:
        url = '/msg/post/private'
        resp = self._api_request(url, method='POST', data={'text': text, 'user_email': email})
        return Post(Chat(self, resp['chat_id']), resp['post_no'])

    def post_private_message_by_user_id(self, user_id: int, text: str) -> Post:
        url = '/msg/post/private'
        resp = self._api_request(url, method='POST', data={'text': text, 'user_id': user_id})
        return Post(Chat(self, resp['chat_id']), resp['post_no'])

    def post_private_message_by_user_unique_name(self, unique_name: str, text: str) -> Post:
        url = '/msg/post/private'
        resp = self._api_request(url, method='POST', data={'text': text, 'user_unique_name': unique_name})
        return Post(Chat(self, resp['chat_id']), resp['post_no'])
