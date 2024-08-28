from __future__ import annotations

import datetime
import typing
from enum import StrEnum, auto
from loguru import logger
import jsonlines
import orjson
import parse
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    ConfigDict,
    model_validator,
    BeforeValidator,
)
from urllib.parse import urljoin

from good_common.utilities import parse_timestamp
from good_common.types.web import URL


def absolute_url(url: str) -> str:
    return urljoin("https://www.google.com", url)


AbsoluteURL = typing.Annotated[URL, BeforeValidator(absolute_url)]


class SearchesPerTypeCount(BaseModel):
    model_config = ConfigDict(extra="allow")
    web: int = 0
    news: int = 0
    videos: int = 0
    images: int = 0
    places: int = 0
    shopping: int = 0


class SearchesType(StrEnum):
    MIXED = auto()
    WEB = auto()
    NEWS = auto()
    IMAGES = auto()
    VIDEOS = auto()
    PLACES = auto()
    PLACE_DETAILS = auto()
    SHOPPING = auto()
    PRODUCTS = auto()
    PRODUCT_SELLERS_ONLINE = auto()
    PRODUCT_REVIEWS = auto()
    PRODUCT_SPECIFICATIONS = auto()


class BatchPriority(StrEnum):
    HIGHEST = auto()
    HIGH = auto()
    NORMAL = auto()
    LOW = auto()
    LOWEST = auto()


class ScheduleType(StrEnum):
    MANUAL = auto()
    MINUTES = auto()
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    YEARLY = auto()


class ScheduleMinutes(StrEnum):
    EVERY_MINUTE = auto()
    EVERY_5_MINUTES = auto()
    EVERY_10_MINUTES = auto()
    EVERY_15_MINUTES = auto()
    EVERY_25_MINUTES = auto()
    EVERY_30_MINUTES = auto()
    EVERY_HOUR = auto()


class BatchStatus(StrEnum):
    ALL = auto()
    IDLE = auto()
    QUEUED = auto()
    RUNNING = auto()


class Batch(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: typing.Optional[str] = None
    created_at: typing.Optional[datetime.datetime] = None
    last_run: typing.Optional[datetime.datetime] = None
    name: str
    schedule_type: ScheduleType = Field(default=ScheduleType.MANUAL)
    enabled: typing.Optional[bool] = None
    status: typing.Optional[BatchStatus] = None
    api_requests_required: typing.Optional[int] = None
    searches_total_count: typing.Optional[int] = None
    searches_page_count: typing.Optional[int] = None
    credits_required: typing.Optional[int] = None
    next_result_set_id: typing.Optional[int] = None
    results_count: typing.Optional[int] = None
    priority: BatchPriority = Field(default=BatchPriority.NORMAL)
    destination_ids: typing.Optional[list[str]] = None
    notification_email: typing.Optional[str] = None
    notification_as_json: typing.Optional[bool] = None
    notification_as_jsonlines: typing.Optional[bool] = True
    notification_as_csv: typing.Optional[bool] = None
    searches_type: typing.Optional[SearchesType] = None
    searches_per_type_count: typing.Optional[SearchesPerTypeCount] = None
    searches_type_locked: typing.Optional[bool] = None
    schedule_hours: typing.Optional[list[int]] = None
    schedule_minutes: typing.Optional[ScheduleMinutes] = None
    schedule_days_of_week: typing.Optional[list[int]] = None
    schedule_days_of_month: typing.Optional[list[int]] = None


class Destination(BaseModel):
    id: str
    name: str
    type: str
    enabled: bool
    used_by: int
    s3_bucket_name: typing.Optional[str] = None


class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float
    altitude: typing.Optional[int] = None


class Location(BaseModel):
    id: typing.Optional[int] = None
    name: typing.Optional[str] = None
    type: typing.Optional[str] = None
    full_name: typing.Optional[str] = None
    parent_id: typing.Optional[int] = None
    country_code: typing.Optional[str] = None
    reach: typing.Optional[int] = None
    gps_coordinates: GPSCoordinates


class RequestInfo(BaseModel):
    success: bool
    type: typing.Optional[str] = None


class WebhookStatus(BaseModel):
    status: str
    log: list


class LogItem(BaseModel):
    date_time: datetime.datetime
    text: str


class DestinationStatus(BaseModel):
    status: str
    log: list[LogItem] = Field(default_factory=list)


class DownloadLinks(BaseModel):
    pages: list[str] = Field(default_factory=list)
    all_pages: str


class ResultSet(BaseModel):
    id: int
    batch_id: typing.Optional[str] = None
    started_at: typing.Optional[datetime.datetime] = None
    ended_at: typing.Optional[datetime.datetime] = None
    expires_at: typing.Optional[datetime.datetime] = None
    results_page_count: typing.Optional[int] = None
    searches_completed: typing.Optional[int] = None
    searches_failed: typing.Optional[int] = None
    searches_total: typing.Optional[int] = None
    webhook_status: typing.Optional[WebhookStatus] = None
    destination_status: dict[str, DestinationStatus] = Field(default_factory=dict)
    download_links: typing.Optional[DownloadLinks | dict[str, DownloadLinks]] = None
    s3_object_keys: typing.Optional[typing.Any] = None

    def get_download_links(self, filetype: str = "jsonl"):
        links = []
        if isinstance(self.download_links, dict):
            for _, _links in self.download_links.items():
                for link in _links.pages:
                    if filetype in link:
                        links.append(link)
        else:
            for link in self.download_links.pages:
                logger.info(link)
                if filetype in link:
                    links.append(link)
        return links


class BatchResult(BaseModel):
    request_info: typing.Optional[RequestInfo] = None
    batch_id: typing.Optional[str] = None
    result: typing.Optional[ResultSet] = None
    s3_file_keys: list[str] = Field(default_factory=list)


class WebhookResponse(BaseModel):
    request_info: typing.Optional[RequestInfo] = None
    result_set: typing.Optional[ResultSet] = None
    batch: typing.Optional[Batch] = None


class BatchResults(BaseModel):
    def __init__(self, **data):
        results = []
        for result in data.get("results", []):
            result["batch_id"] = data.get("batch_id")
            results.append(result)
        data["results"] = results
        super().__init__(**data)

    request_info: typing.Optional[RequestInfo] = None
    batch_id: typing.Optional[str] = None
    results: list[ResultSet] = Field(default_factory=list)


class SearchParameters(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    # def __init__(self, search_type: typing.Optional[SearchesType] = None, **data):

    #     super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def init_model(cls, data):
        if "time_period_min" in data and "time_period_max" in data:
            data["time_period"] = "custom"

        return data

    q: typing.Optional[str] = None
    url: typing.Optional[AbsoluteURL] = None
    location: typing.Optional[str] = None
    google_domain: typing.Optional[str] = None
    gl: typing.Optional[str] = None
    hl: typing.Optional[str] = None
    custom_id: typing.Optional[str] = None
    time_period: typing.Optional[str] = None
    time_period_min: typing.Optional[datetime.date] = None
    time_period_max: typing.Optional[datetime.date] = None

    @field_validator("time_period_min", "time_period_max", mode="before")
    @classmethod
    def validate_time_period(cls, v: str | datetime.date):
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%m/%d/%Y").date()
        return v

    @field_serializer("time_period_min", "time_period_max")
    def date_to_string(self, value) -> str | None:
        if value is None:
            return value
        return value.strftime("%m/%d/%Y")

    page: typing.Optional[int] = None
    max_page: typing.Optional[typing.Union[int, str]] = None
    num: typing.Optional[typing.Union[int, str]] = None
    include_answer_box: typing.Optional[bool] = None

    @field_serializer("include_answer_box", "include_advertiser_info")
    def boolean_to_strings(self, value) -> str:
        if value is True:
            return "true"
        elif value is False:
            return "false"
        else:
            return value

    include_advertiser_info: typing.Optional[bool] = None

    # @field_serializer('include_advertiser_info')
    # def boolean_to_strings(self, value) -> str:
    #     if value is True:
    #         return 'true'
    #     elif value is False:
    #         return 'false'
    #     else:
    #         return value

    engine: typing.Optional[str] = None
    id: typing.Optional[str] = None
    news_type: typing.Optional[str] = None
    search_type: typing.Optional[SearchesType] = None

    @field_serializer("search_type")
    def search_type_to_string(self, value: SearchesType | None) -> str | None:
        if not value:
            return None
        if value.name.lower() == "web":
            return None
        return value.name.lower()

    @field_validator("search_type", mode="before")
    @classmethod
    def search_type_to_enum(cls, value: str | SearchesType) -> SearchesType:
        if isinstance(value, SearchesType):
            return value
        return SearchesType[value.upper()]

    batch_id: typing.Optional[str] = None
    hide_base64_images: typing.Optional[str] = None
    filter: typing.Optional[str] = None
    knowledge_graph_id: typing.Optional[str] = None


class Page(BaseModel):
    created_at: typing.Optional[str] = None
    processed_at: typing.Optional[str] = None
    total_time_taken: typing.Optional[float] = None
    engine_url: typing.Optional[str] = None
    html_url: typing.Optional[str] = None
    json_url: typing.Optional[str] = None
    location_auto_message: typing.Optional[str] = None


class SearchMetadata(BaseModel):
    created_at: typing.Optional[str] = None
    processed_at: typing.Optional[str] = None
    total_time_taken: typing.Optional[float] = None
    pages: typing.Optional[list[Page]] = None
    engine_url: typing.Optional[str] = None
    html_url: typing.Optional[str] = None
    json_url: typing.Optional[str] = None
    location_auto_message: typing.Optional[str] = None


class SearchTab(BaseModel):
    position: typing.Optional[int] = None
    text: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None


class SearchInformation(BaseModel):
    did_you_mean: typing.Optional[str] = None
    original_query_yields_zero_results: typing.Optional[bool] = None
    query_displayed: typing.Optional[str] = None
    search_tabs: typing.Optional[list[SearchTab]] = None
    showing_results_for: typing.Optional[str] = None
    time_taken_displayed: typing.Optional[float] = None
    total_results: typing.Optional[int] = None


class ExpandedItem(BaseModel):
    title: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    snippet: typing.Optional[str] = None
    date_raw: typing.Optional[str] = None
    date: typing.Optional[str] = None


class InlineItem(BaseModel):
    title: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None


class SiteLinks(BaseModel):
    expanded: typing.Optional[list[ExpandedItem]] = None
    inline: typing.Optional[list[InlineItem]] = None


class ParsedItem(BaseModel):
    raw: typing.Optional[str] = None
    parsed: typing.Optional[float] = None


class Source(BaseModel):
    first_indexed: typing.Optional[ParsedItem] = None
    link: typing.Optional[AbsoluteURL] = None
    description: typing.Optional[str] = None


class AboutThisResult(BaseModel):
    your_search_and_this_result: typing.Optional[list[str]] = None
    search_terms: typing.Optional[list[str]] = None
    related_terms: typing.Optional[list[str]] = None
    source: typing.Optional[Source] = None
    connection_secure: typing.Optional[ParsedItem] = None


class ResultItem(BaseModel):
    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    date: typing.Optional[str] = None
    displayed_link: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    position: typing.Optional[int] = None
    title: typing.Optional[str] = None


class LocalResult(BaseModel):
    block_position: typing.Optional[int] = None
    data_cid: typing.Optional[str] = None
    extensions: typing.Optional[list[str]] = None
    link: typing.Optional[AbsoluteURL] = None
    phone: typing.Optional[str] = None
    position: typing.Optional[int] = None
    rating: typing.Optional[float] = None
    reviews: typing.Optional[int] = None
    title: typing.Optional[str] = None


class Currency(BaseModel):
    name: typing.Optional[str] = None
    code: typing.Optional[str] = None
    symbol: typing.Optional[str] = None


class DetectedExtensions(BaseModel):
    answers: typing.Optional[int] = None
    currency: typing.Optional[Currency] = None
    date: typing.Optional[str] = None
    in_stock: typing.Optional[bool] = None
    price: typing.Optional[float] = None
    rating: typing.Optional[float] = None
    reviews: typing.Optional[int] = None
    symbol: typing.Optional[str] = None


class Attribute(BaseModel):
    name: typing.Optional[str] = None
    value: typing.Optional[typing.Union[int, str]] = None


class Top(BaseModel):
    detected_extensions: typing.Optional[DetectedExtensions] = None
    extensions: typing.Optional[list[str]] = None
    attributes: typing.Optional[list[Attribute]] = None
    attributes_flat: typing.Optional[str] = None


class RichSnippet(BaseModel):
    top: typing.Optional[Top] = None


class FaqItem(BaseModel):
    question: typing.Optional[str] = None
    answer: typing.Optional[str] = None


class OrganicResult(BaseModel):
    about_this_result: typing.Optional[AboutThisResult] = None
    answer_box: typing.Optional[bool] = None
    block_position: typing.Optional[int] = None
    cached_page_link: typing.Optional[str] = None
    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    date: typing.Optional[str] = None
    displayed_link: typing.Optional[str] = None
    domain: typing.Optional[str] = None
    faq: typing.Optional[list[FaqItem]] = None
    link: typing.Optional[AbsoluteURL] = None
    missing_words: typing.Optional[list[str]] = None
    nested_results: typing.Optional[list[ResultItem]] = None
    page: typing.Optional[typing.Union[int, str]] = None
    position_overall: typing.Optional[int] = None
    position: typing.Optional[int] = None
    prefix: typing.Optional[str] = None
    prerender: typing.Optional[bool] = None
    related_page_link: typing.Optional[str] = None
    rich_snippet: typing.Optional[RichSnippet] = None
    sitelinks_search_box: typing.Optional[bool] = None
    sitelinks: typing.Optional[SiteLinks] = None
    snippet_matched: typing.Optional[list[str]] = None
    snippet: typing.Optional[str] = None
    thumbnail_image: typing.Optional[str] = None
    thumbnail: typing.Optional[bool] = None
    title: typing.Optional[str] = None


class RelatedSearch(BaseModel):
    query: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    type: typing.Optional[str] = None
    group_name: typing.Optional[str] = None


class AnswerlistItem(BaseModel):
    text: typing.Optional[str] = None


class Search(BaseModel):
    link: typing.Optional[AbsoluteURL] = None
    title: typing.Optional[str] = None


class RelatedQuestion(BaseModel):
    question: typing.Optional[str] = None
    answer: typing.Optional[str] = None
    source: typing.Optional[ResultItem] = None
    search: typing.Optional[Search] = None
    block_position: typing.Optional[int] = None
    answer_list: typing.Optional[list[AnswerlistItem]] = None


class InlineImage(BaseModel):
    block_position: typing.Optional[int] = None
    image: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    title: typing.Optional[str] = None


class OtherPage(BaseModel):
    page: typing.Optional[int] = None
    link: typing.Optional[AbsoluteURL] = None


class ApiPagination(BaseModel):
    next: typing.Optional[str] = None
    other_pages: typing.Optional[list[OtherPage]] = None


class PaginationPage(BaseModel):
    current: typing.Optional[int] = None
    next: typing.Optional[str] = None
    other_pages: typing.Optional[list[OtherPage]] = None
    api_pagination: typing.Optional[ApiPagination] = None


class Pagination(BaseModel):
    pages: typing.Optional[list[PaginationPage]] = None


class NewsResult(BaseModel):
    position: typing.Optional[int] = None
    title: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    domain: typing.Optional[str] = None
    source: typing.Optional[str] = None
    date: typing.Optional[str] = None

    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    snippet: typing.Optional[str] = None
    page: typing.Optional[typing.Union[int, str]] = None
    position_overall: typing.Optional[int] = None


class TopStory(BaseModel):
    link: typing.Optional[AbsoluteURL] = None
    title: typing.Optional[str] = None
    visible_initially: typing.Optional[bool] = None
    source: typing.Optional[str] = None
    date: typing.Optional[str] = None

    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    block_position: typing.Optional[int] = None


class TopStoriesExtra(BaseModel):
    more_news_link: typing.Optional[str] = None


class InlineVideo(BaseModel):
    position: typing.Optional[int] = None
    title: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    length: typing.Optional[str] = None
    source: typing.Optional[str] = None
    date: typing.Optional[str] = None

    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    block_position: typing.Optional[int] = None


class InlineImageSuggestion(BaseModel):
    title: typing.Optional[str] = None


class InlineTweet(BaseModel):
    link: typing.Optional[AbsoluteURL] = None
    status_link: typing.Optional[str] = None
    title: typing.Optional[str] = None
    date: typing.Optional[str] = None

    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    snippet: typing.Optional[str] = None
    block_position: typing.Optional[int] = None


class SiteLink(BaseModel):
    title: typing.Optional[str] = None
    description: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None


class Ad(BaseModel):
    block_position: typing.Optional[str] = None
    description: typing.Optional[str] = None
    domain: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    position: typing.Optional[int] = None
    sitelinks: typing.Optional[list[SiteLink]] = None
    title: typing.Optional[str] = None
    tracking_link: typing.Optional[str] = None


class Answer(BaseModel):
    source: typing.Optional[ResultItem] = None
    answer: typing.Optional[str] = None
    classification: typing.Optional[str] = None
    category: typing.Optional[str] = None
    sub_category: typing.Optional[str] = None


class AnswerBox(BaseModel):
    answer_box_type: typing.Optional[int] = None
    answers: typing.Optional[list[Answer]] = None
    block_position: typing.Optional[int] = None


class LocalMap(BaseModel):
    link: typing.Optional[AbsoluteURL] = None
    gps_coordinates: typing.Optional[GPSCoordinates] = None


class ParsedHours(BaseModel):
    open: typing.Optional[str] = None
    close: typing.Optional[str] = None


class PerDayItem(BaseModel):
    name: typing.Optional[str] = None
    value: typing.Optional[str] = None
    day_number: typing.Optional[int] = None
    parsed: typing.Optional[list[ParsedHours]] = None


class OpeningHours(BaseModel):
    per_day: typing.Optional[list[PerDayItem]] = None


class KnownAttribute(BaseModel):
    attribute: typing.Optional[str] = None
    value: typing.Optional[str] = None
    name: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    author: typing.Optional[str] = None


class PeopleAlsoSearchForItem(BaseModel):
    name: typing.Optional[str] = None
    category: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None


class ReviewsFromTheWebItem(BaseModel):
    title: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None
    reviews: typing.Optional[int] = None
    rating: typing.Optional[float] = None
    rating_out_of: typing.Optional[int] = None


class Reference(BaseModel):
    name: typing.Optional[str] = None
    link: typing.Optional[AbsoluteURL] = None


class Post(BaseModel):
    title: typing.Optional[str] = None
    date: typing.Optional[str] = None

    date_utc: typing.Optional[datetime.datetime] = None

    @field_validator("date_utc", mode="before")
    @classmethod
    def parse_date_utc(cls, v):
        return parse_timestamp(v)

    post_id: typing.Optional[str] = None
    image: typing.Optional[str] = None


class GooglePosts(BaseModel):
    name: typing.Optional[str] = None
    posts: typing.Optional[list[Post]] = None


class Product(BaseModel):
    title: typing.Optional[str] = None
    subtitle: typing.Optional[str] = None


class HoursItem(BaseModel):
    hour: typing.Optional[int] = None
    percent: typing.Optional[int] = None
    hour_text: typing.Optional[str] = None
    description: typing.Optional[str] = None


class KnowledgeGraph(BaseModel):
    id: typing.Optional[str] = None
    title: typing.Optional[str] = None
    type: typing.Optional[str] = None
    unclaimed: typing.Optional[bool] = None
    category: typing.Optional[str] = None
    website: typing.Optional[str] = None
    local_map: typing.Optional[LocalMap] = None
    gps_coordinates: typing.Optional[GPSCoordinates] = None
    address: typing.Optional[list[KnownAttribute] | str] = None
    phone: typing.Optional[str] = None
    hours: typing.Optional[list[Attribute]] = None
    opening_hours: typing.Optional[OpeningHours] = None
    known_attributes: typing.Optional[list[KnownAttribute]] = None
    block_position: typing.Optional[int] = None
    people_also_search_for: typing.Optional[list[PeopleAlsoSearchForItem]] = None
    people_also_search_for_view_more_link: typing.Optional[str] = None
    place_id: typing.Optional[str] = None
    data_cid: typing.Optional[str] = None
    data_id: typing.Optional[str] = None
    description: typing.Optional[str] = None
    reviews_from_the_web: typing.Optional[list[ReviewsFromTheWebItem]] = None
    source: typing.Optional[Reference] = None
    born: typing.Optional[list[KnownAttribute] | str] = None
    profiles: typing.Optional[list[Reference]] = None
    rating: typing.Optional[float] = None
    reviews: typing.Optional[int] = None
    spouse: typing.Optional[typing.Union[str, list[Reference]]] = None
    education: typing.Optional[typing.Union[str, list[Reference]]] = None
    height: typing.Optional[str | typing.Any] = None
    permanently_closed: typing.Optional[bool] = None
    residence: typing.Optional[typing.Union[str, list[Reference]]] = None
    children: typing.Optional[typing.Union[str, list[Reference]]] = None
    parents: typing.Optional[typing.Union[str, list[Reference]]] = None
    organization_founded: typing.Optional[str] = None
    google_posts: typing.Optional[GooglePosts] = None
    products: typing.Optional[list[Product]] = None
    time_typically_spent: typing.Optional[str] = None
    busyness_hours: typing.Optional[dict[str, list[HoursItem]]] = None


class ResultItems(BaseModel):
    ads: typing.Optional[list[Ad]] = None
    answer_box: typing.Optional[AnswerBox] = None
    inline_image_suggestions: typing.Optional[list[InlineImageSuggestion]] = None
    inline_images: typing.Optional[list[InlineImage]] = None
    inline_tweets: typing.Optional[list[InlineTweet]] = None
    inline_videos: typing.Optional[list[InlineVideo]] = None
    knowledge_graph: typing.Optional[KnowledgeGraph] = None
    local_map: typing.Optional[LocalMap] = None
    local_results_more_link: typing.Optional[str] = None
    local_results: typing.Optional[list[LocalResult]] = None
    news_results: typing.Optional[list[NewsResult]] = None
    organic_results: typing.Optional[list[OrganicResult]] = None
    pagination: typing.Optional[Pagination] = None
    related_questions: typing.Optional[list[RelatedQuestion]] = None
    related_searches: typing.Optional[list[RelatedSearch]] = None
    search_information: typing.Optional[SearchInformation] = None
    search_metadata: typing.Optional[SearchMetadata] = None
    search_parameters: typing.Optional[SearchParameters] = None
    top_stories_extra: typing.Optional[TopStoriesExtra] = None
    top_stories: typing.Optional[list[TopStory]] = None


class ResultRecord(BaseModel):
    id: str
    result_id: typing.Optional[int] = None
    batch_id: typing.Optional[str] = None
    success: bool
    result: ResultItems
    total_time_taken: float
    search: SearchParameters


class ResultRecordCollection(BaseModel):
    items: list[ResultRecord]


class S3Object:
    def __init__(self, client, obj):
        self._client = client
        self._obj = obj

        properties = parse.parse(
            "Batch_Results_{batch_id}_{result_id}_Page_{page_id}.jsonl", self.key
        )
        if properties:
            self.batch_id = properties["batch_id"]
            self.result_id = properties["result_id"]
            self.page_id = properties["page_id"]

    @property
    def obj(self):
        return self._obj

    @property
    def key(self):
        return self.obj.key

    def read(self):
        return self._obj.get()["Body"].read()

    def read_jsonlines(self):
        # iter_lines
        # return jsonlines.Reader(io.BytesIO(self.read()), loads=orjson.loads)
        return jsonlines.Reader(
            self._obj.get()["Body"].iter_lines(), _loads=orjson.loads
        )

    def __repr__(self):
        return f"<S3Object key={self.key}>"
