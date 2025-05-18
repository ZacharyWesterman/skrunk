from typing import TypedDict
from .blob import Blob
from .blobdoesnotexisterror import BlobDoesNotExistError
from .insufficientperms import InsufficientPerms
from .badtagquery import BadTagQuery
from .userdoesnotexisterror import UserDoesNotExistError
from .insufficientdiskspace import InsufficientDiskSpace
from .zipprogress import ZipProgress
from .booktag import BookTag
from .booktagexistserror import BookTagExistsError
from .apifailederror import ApiFailedError
from .booktagdoesnotexisterror import BookTagDoesNotExistError
from .book import Book
from .bookcannotbeshared import BookCannotBeShared
from .notification import Notification
from .missingconfig import MissingConfig
from .webpushexception import WebPushException
from .invalidsubscriptiontoken import InvalidSubscriptionToken
from .badnotification import BadNotification
from .bugreport import BugReport
from .bugreportcreationfailederror import BugReportCreationFailedError
from .bugreportdoesnotexisterror import BugReportDoesNotExistError
from .feed import Feed
from .feeddoesnotexisterror import FeedDoesNotExistError
from .invalidfeedkinderror import InvalidFeedKindError
from .feeddocument import FeedDocument
from .feeddocumentdoesnotexisterror import FeedDocumentDoesNotExistError
from .item import Item
from .invalidfields import InvalidFields
from .itemexistserror import ItemExistsError
from .itemdoesnotexisterror import ItemDoesNotExistError
from .theme import Theme
from .userdata import UserData
from .badusernameerror import BadUserNameError
from .userexistserror import UserExistsError
from .weatheruser import WeatherUser
from .logresult import LogResult


class Mutation(TypedDict):
	_SRV_DUMMY_M: bool
	createAPIKey: str
	deleteAPIKey: bool
	deleteBlob: Blob | BlobDoesNotExistError | InsufficientPerms
	setBlobTags: Blob | BlobDoesNotExistError | InsufficientPerms
	createZipArchive: Blob | BadTagQuery | UserDoesNotExistError | InsufficientDiskSpace | InsufficientPerms | BlobDoesNotExistError
	getBlobFromQR: Blob | InsufficientPerms
	setBlobHidden: Blob | BlobDoesNotExistError | InsufficientPerms
	setBlobEphemeral: Blob | BlobDoesNotExistError | InsufficientPerms
	cancelZipArchive: ZipProgress | BlobDoesNotExistError | InsufficientPerms
	linkBookTag: BookTag | BookTagExistsError | ApiFailedError | InsufficientPerms | UserDoesNotExistError
	unlinkBookTag: BookTag | BookTagDoesNotExistError | InsufficientPerms
	borrowBook: Book | BookTagDoesNotExistError | BookCannotBeShared | UserDoesNotExistError | InsufficientPerms
	requestToBorrowBook: Notification | MissingConfig | UserDoesNotExistError | WebPushException | InvalidSubscriptionToken | BadNotification | InsufficientPerms
	shareBook: Book | BookTagDoesNotExistError | BookCannotBeShared | UserDoesNotExistError | InsufficientPerms
	shareBookNonUser: Book | BookTagDoesNotExistError | BookCannotBeShared | UserDoesNotExistError | InsufficientPerms
	returnBook: Book | BookTagDoesNotExistError | BookCannotBeShared | UserDoesNotExistError | InsufficientPerms
	setBookOwner: Book | BookTagDoesNotExistError | UserDoesNotExistError | InsufficientPerms
	editBook: Book | BookTagDoesNotExistError | UserDoesNotExistError | InsufficientPerms
	createBook: BookTag | BookTagExistsError | ApiFailedError | InsufficientPerms | UserDoesNotExistError
	appendEBook: Book | BookTagDoesNotExistError | UserDoesNotExistError | InsufficientPerms
	reportBug: BugReport | BugReportCreationFailedError | InsufficientPerms
	deleteBug: BugReport | BugReportDoesNotExistError | InsufficientPerms
	setBugStatus: BugReport | BugReportDoesNotExistError | InsufficientPerms
	commentOnBug: BugReport | BugReportDoesNotExistError | InsufficientPerms
	createFeed: Feed | FeedDoesNotExistError | UserDoesNotExistError | InsufficientPerms | InvalidFeedKindError
	deleteFeed: Feed | FeedDoesNotExistError | UserDoesNotExistError | InsufficientPerms | InvalidFeedKindError
	updateFeedNotify: Feed | FeedDoesNotExistError | UserDoesNotExistError | InsufficientPerms | InvalidFeedKindError
	createFeedDocument: FeedDocument | FeedDoesNotExistError | InsufficientPerms
	updateFeedDocument: FeedDocument | FeedDocumentDoesNotExistError | InsufficientPerms
	markDocumentRead: FeedDocument | FeedDocumentDoesNotExistError | InsufficientPerms
	setFeedInactive: Feed | FeedDoesNotExistError | UserDoesNotExistError | InsufficientPerms | InvalidFeedKindError
	setFeedNavigation: Feed | FeedDoesNotExistError | UserDoesNotExistError | InsufficientPerms | InvalidFeedKindError
	createInventoryItem: Item | InsufficientPerms | InvalidFields | ItemExistsError | UserDoesNotExistError
	deleteInventoryItem: Item | InsufficientPerms | ItemDoesNotExistError
	createSubscription: Notification | MissingConfig | UserDoesNotExistError | WebPushException | InvalidSubscriptionToken | BadNotification | InsufficientPerms
	deleteSubscription: int
	deleteSubscriptions: int
	sendNotification: Notification | MissingConfig | UserDoesNotExistError | WebPushException | InvalidSubscriptionToken | BadNotification | InsufficientPerms
	sendNotificationAsRead: Notification | MissingConfig | UserDoesNotExistError | WebPushException | InvalidSubscriptionToken | BadNotification | InsufficientPerms
	markNotifAsRead: bool
	markAllNotifsAsRead: bool
	setModuleEnabled: list[str]
	setConfig: bool
	createTheme: Theme | MissingConfig | InsufficientPerms
	deleteTheme: Theme | MissingConfig | InsufficientPerms
	createUser: UserData | BadUserNameError | UserExistsError | InsufficientPerms
	deleteUser: UserData | UserDoesNotExistError | InsufficientPerms
	updateUserTheme: UserData | UserDoesNotExistError | InsufficientPerms
	deleteUserTheme: UserData | UserDoesNotExistError | InsufficientPerms
	updateUserPerms: UserData | UserDoesNotExistError | InsufficientPerms
	revokeSessions: int
	updateUserPassword: UserData | UserDoesNotExistError | InsufficientPerms
	updateUsername: UserData | BadUserNameError | UserDoesNotExistError | UserExistsError | InsufficientPerms
	updateUserDisplayName: UserData | UserDoesNotExistError | InsufficientPerms
	updateUserGroups: UserData | UserDoesNotExistError | InsufficientPerms
	updateUserModule: UserData | UserDoesNotExistError | InsufficientPerms
	updateUserEmail: UserData | UserDoesNotExistError | InsufficientPerms
	exportUserData: Blob | BadTagQuery | UserDoesNotExistError | InsufficientDiskSpace | InsufficientPerms | BlobDoesNotExistError
	createWeatherUser: WeatherUser | UserExistsError | UserDoesNotExistError | InsufficientPerms
	deleteWeatherUser: WeatherUser | UserDoesNotExistError | InsufficientPerms
	enableWeatherUser: WeatherUser | UserDoesNotExistError | InsufficientPerms
	disableWeatherUser: WeatherUser | UserDoesNotExistError | InsufficientPerms
	updateWeatherUser: WeatherUser | UserDoesNotExistError | InsufficientPerms
	logWeatherAlert: LogResult | InsufficientPerms
	logUserWeatherAlert: LogResult | InsufficientPerms
