from typing import TypedDict
from .apikey import APIKey
from .bloblist import BlobList
from .badtagquery import BadTagQuery
from .insufficientperms import InsufficientPerms
from .blobcount import BlobCount
from .blob import Blob
from .qrparseresponse import QRParseResponse
from .zipprogress import ZipProgress
from .blobdoesnotexisterror import BlobDoesNotExistError
from .book import Book
from .booklist import BookList
from .apifailederror import ApiFailedError
from .booktagdoesnotexisterror import BookTagDoesNotExistError
from .userbookcount import UserBookCount
from .bugreport import BugReport
from .issuelist import IssueList
from .repofetchfailed import RepoFetchFailed
from .feed import Feed
from .feeddoesnotexisterror import FeedDoesNotExistError
from .userdoesnotexisterror import UserDoesNotExistError
from .feeddocument import FeedDocument
from .subsonicsearch import SubsonicSearch
from .subsonicerror import SubsonicError
from .subsonictrack import SubsonicTrack
from .systeminfo import SystemInfo
from .item import Item
from .lastmutation import LastMutation
from .subscription import Subscription
from .subscriptionlist import SubscriptionList
from .notification import Notification
from .configlist import ConfigList
from .theme import Theme
from .schema import Schema
from .userdata import UserData
from .usermindata import UserMinData
from .weatheruser import WeatherUser
from .weatherexecution import WeatherExecution
from .weatheralert import WeatherAlert


class Query(TypedDict):
	_SRV_DUMMY_Q: bool
	getAPIKeys: list[APIKey | None]
	getBlobs: BlobList | BadTagQuery | InsufficientPerms
	countBlobs: BlobCount | BadTagQuery | InsufficientPerms
	getBlob: Blob | None
	totalBlobSize: BlobCount | BadTagQuery | InsufficientPerms
	getQRFromBlob: QRParseResponse | None
	countTagUses: int
	generateUID: str
	pollZipProgress: ZipProgress | BlobDoesNotExistError | InsufficientPerms
	getBooks: list[Book | None]
	countBooks: int
	searchBooks: BookList | ApiFailedError
	getBookByTag: Book | BookTagDoesNotExistError
	countAllUserBooks: list[UserBookCount | None]
	getBookDescription: str
	getBugReports: list[BugReport | None]
	countBugReports: int
	getBugReport: BugReport | None
	getOpenIssues: IssueList | RepoFetchFailed
	getPendingIssues: IssueList | RepoFetchFailed
	getFeed: Feed | FeedDoesNotExistError | UserDoesNotExistError | InsufficientPerms
	getFeeds: list[Feed | None]
	countFeeds: int
	getUserFeeds: list[Feed | None]
	getFeedDocuments: list[FeedDocument | None]
	countFeedDocuments: int
	searchSubsonic: SubsonicSearch | SubsonicError
	subsonicAlbumTrackList: list[SubsonicTrack | None]
	subsonicCoverArt: str
	getSystemInfo: SystemInfo | None
	getInventory: list[Item | None]
	countInventory: int
	getItemCategories: list[str]
	getItemTypes: list[str]
	getItemLocations: list[str]
	getLastMutation: LastMutation | None
	getVAPIDPublicKey: str
	getSubscription: Subscription | None
	getSubscriptions: SubscriptionList | UserDoesNotExistError | InsufficientPerms
	getNotifications: list[Notification | None]
	countNotifications: int
	getEnabledModules: list[str]
	getModules: list[str]
	getServerEnabledModules: list[str]
	getUserGroups: list[str]
	getConfigs: ConfigList | InsufficientPerms
	getConfig: str
	getThemes: list[Theme | None]
	getSchema: Schema | None
	getUser: UserData | UserDoesNotExistError | InsufficientPerms
	listUsers: list[UserMinData | None]
	countSessions: int
	getWeatherUser: WeatherUser | UserDoesNotExistError | InsufficientPerms
	getWeatherUsers: list[WeatherUser | None]
	getLastWeatherExec: WeatherExecution | None
	weatherAlertHistory: list[WeatherAlert | None]
	getWeatherAlerts: list[WeatherAlert | None]
	countWeatherAlerts: int
