import collections
import os
from typing import Any, Dict, Generator, List, Optional, Protocol, AsyncGenerator
from fast_depends import inject
import httpx
import requests
from loguru import logger
import jsonlines

# from genson import SchemaBuilder
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from good_intel import BaseProvider

# from edgepath.sources.base import Cursor, datetime_to_milliseconds
from ._models import (
    Batch,
    BatchResults,
    Destination,
    ResultRecord,
    ResultSet,
    S3Object,
    SearchParameters,
    ResultItems,
)

from ._s3 import S3Bucket, S3BucketProvider

# from requests.packages.urllib3.util.retry import Retry


# from edgepath.sources.google_serp.s3 import S3Bucket, S3Object


class S3BucketProto(Protocol):
    def get_object(self, key): ...

    def iter_items(
        self, prefix: str | None = None
    ) -> Generator[S3Object, None, None]: ...


class ValueSerp:
    base_path = "https://api.valueserp.com/"

    @inject
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("VALUESERP_API_KEY")
        self._bucket = S3BucketProvider().get(
            bucket_name="edgepath-serp-results",
            aws_access_key_id=os.getenv("AWS_ACCESS_TOKEN"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )

        self._session = requests.Session()

        retries = Retry(
            total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )

        self._session.mount("http://", HTTPAdapter(max_retries=retries))

        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        self._batches = {}
        self._batch_searches = collections.defaultdict(dict)
        self._batch_results = collections.defaultdict(list)

    # def update_index(self):
    #     for batch in self.get_batches():
    #         if not batch.id:
    #             continue
    #         self._batches[batch.id] = batch
    #         for search in self.iter_batch_searches(batch_id=batch.id):
    #             self._batch_searches[batch.id][search.id] = search

    #         for result in self.iter_batch_results(batch_id=batch.id):
    #             self._batch_results[batch.id].append(result)
    #     return self._batch_results

    @property
    def bucket(self) -> S3Bucket:
        if not self._bucket:
            raise ValueError("Bucket is not defined")
        return self._bucket

    def _build_url(self, *paths) -> str:
        return self.base_path + "/".join(map(str, paths))

    def _get(self, *paths, **parameters) -> Dict[str, Any]:
        url = self._build_url(*paths)
        # logger.debug((url, parameters))
        parameters["api_key"] = self._api_key
        response = self._session.get(url, params=parameters)
        response.raise_for_status()
        return response.json()

    def _get_auto_paginate(
        self, data_key: str, *paths, **parameters
    ) -> Generator[Dict[str, Any], None, None]:
        results = self._get(*paths, **parameters)
        data = results.get(data_key, [])
        # logger.debug(results.get("total_pages", 1))
        for item in data:
            yield item
        while results.get("current_page", 1) < results.get("total_pages", 1):
            parameters["page"] = results.get("current_page", 1) + 1
            results = self._get(*paths, **parameters)
            # data += results.get(data_key, [])
            for item in results.get(data_key, []):
                yield item
        # return data

    def _post(self, *paths, params: Dict = {}, body: Dict):
        url = self._build_url(*paths)
        params["api_key"] = self._api_key
        response = self._session.post(url, params=params, json=body)
        response.raise_for_status()
        return response.json()

    def _put(self, *paths, params: Dict = {}, body: Dict):
        url = self._build_url(*paths)
        params["api_key"] = self._api_key
        response = None
        try:
            response = self._session.put(url, params=params, json=body)
            if response.status_code > 299:
                logger.error(response.text)
            response.raise_for_status()
        except Exception as e:
            logger.error(e)
            if response:
                logger.error(response.text)
            raise e
        return response.json()

    def _delete(self, *paths, **parameters) -> dict:
        url = self._build_url(*paths)
        parameters["api_key"] = self._api_key
        response = self._session.delete(url, params=parameters)
        response.raise_for_status()
        return response.json()

    def search(self, query: SearchParameters):
        return ResultItems.model_validate(
            self._get("search", **query.model_dump(exclude_none=True, mode="json"))
        )

    def get_batches(
        self, name: Optional[str] = None, contains: Optional[str] = None
    ) -> List[Batch]:
        batches = []
        # for batch in self._get("batches", page_size=1000).get("batches", []):
        for batch in self._get_auto_paginate("batches", "batches", page_size=500):
            obj = Batch(**batch)
            if name:
                if obj.name == name:
                    batches.append(obj)
            elif contains:
                if contains in obj.name:
                    batches.append(obj)
            else:
                batches.append(obj)
        return batches

    def list_destinations(self) -> List[Destination]:
        destinations = []
        for destination in self._get("destinations").get("destinations", []):
            destinations.append(Destination(**destination))
        return destinations

    def iter_batch_searches(
        self, batch_id: str
    ) -> Generator[SearchParameters, None, None]:
        page = 1
        while True:
            try:
                response = self._get("batches", batch_id, "searches", page)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 500:
                    break
                raise e
            for search in response.get("searches", []):
                yield SearchParameters(
                    **{
                        **search,
                        "batch_id": batch_id,  # type: ignore
                    }
                )

            searches_page_count = response.get("searches_page_count", 0)
            searches_page_current = response.get("searches_page_current", 0)

            if searches_page_current >= searches_page_count:
                break

            page += 1

    def get_batch_results(
        self,
        *,
        batch_id: Optional[str] = None,
        batch: Optional[Batch] = None,
        fetch_s3_links: bool = True,
        fetch_jsonlines_links: bool = True,
    ) -> BatchResults:
        if not batch_id and batch:
            batch_id = batch.id

        if not batch_id:
            raise ValueError("Must provide batch_id or batch")

        results = self._get("batches", batch_id, "results")

        # logger.info(results)

        if fetch_s3_links and not fetch_jsonlines_links:
            for i, _result in enumerate(results.get("results", [])):
                s3_objects = self.get_batch_s3_objects(batch_id, _result.get("id"))
                results["results"][i]["s3_object_keys"] = [o.key for o in s3_objects]

        batch_results = BatchResults(**results)

        if not batch_results or batch_results.results is None:
            raise ValueError(f"Batch {batch_id} has no results")

        if fetch_jsonlines_links and batch_id:
            download_results = []
            for result in batch_results.results:
                _result: dict[str, dict[str, Any]] = self._get(
                    "batches", batch_id, "results", result.id, "jsonlines"
                )
                s3_objects = self.get_batch_s3_objects(batch_id, result.id)
                download_results.append(
                    dict(
                        **_result.get("result"),
                        s3_object_keys=[o.key for o in s3_objects],
                    )
                )

            batch_results = BatchResults(
                request_info=batch_results.request_info,
                batch_id=batch_results.batch_id,
                results=download_results,
            )

        return batch_results

    def download_result_records(self, *, result: ResultSet):
        for link in result.get_download_links(filetype="jsonl"):
            response = self._session.get(link)
            with jsonlines.Reader(response.iter_lines()) as reader:
                for line in reader:
                    yield ResultRecord(
                        **line, result_id=result.id, batch_id=result.batch_id
                    )

    def stream_result_records(
        self,
        *,
        result: ResultSet,
    ):
        if result.s3_object_keys:
            # check if duplicate keys (with both json and jsonl files)

            s3_object_keys = []

            if len(
                set(map(lambda x: x.split(".json")[0], result.s3_object_keys))
            ) != len(result.s3_object_keys):
                s3_object_keys = [
                    f for f in result.s3_object_keys if f.endswith(".jsonl")
                ]
            else:
                s3_object_keys = result.s3_object_keys

            for key in s3_object_keys:
                if key.endswith(".jsonl"):
                    obj = self.bucket.get_object(key)
                    if not obj:
                        logger.error(f"Object not found: {key}")
                        continue
                    for line in obj.read_jsonlines():
                        yield ResultRecord(
                            **line,
                            result_id=obj.result_id,
                            batch_id=result.batch_id,
                        )
                elif key.endswith(".json"):
                    obj = self.bucket.get_object(key)
                    if not obj:
                        logger.error(f"Object not found: {key}")
                        continue
                    yield ResultRecord(
                        **obj.read(),
                        result_id=obj.result_id,
                        batch_id=result.batch_id,
                    )

    def get_batch(self, batch_id: str) -> Batch:
        return Batch(**self._get("batches", batch_id).get("batch", {}))

    def get_batch_s3_objects(
        self,
        batch_id: str,
        result_id: int,
    ) -> List[S3Object]:
        if not self.bucket:
            raise ValueError("Bucket is not defined")
        objects = []
        for obj in self.bucket.iter_items(
            prefix=f"Batch_Results_{batch_id}_{result_id}"
        ):
            objects.append(obj)
        return objects

    @classmethod
    def serialize(cls, obj: BaseModel, remove_attributes: List[str] = []):
        d = obj.model_dump()
        return {
            k: v for k, v in d.items() if v is not None and k not in remove_attributes
        }

    def create_batch(self, batch: Batch):
        response = self._post("batches", body=self.serialize(batch))
        try:
            if response.get("request_info", {}).get("success") is True:
                return Batch(**response.get("batch"))
        except Exception as e:
            logger.error(e)

    def update_batch(self, batch: Batch):
        if not batch.id:
            raise ValueError("Batch must have an id")
        response = self._put("batches", batch.id, body=self.serialize(batch))
        try:
            if response.get("request_info", {}).get("success") is True:
                return Batch(**response.get("batch"))
        except Exception as e:
            logger.error(e)

    def delete_batch(
        self, batch_id: Optional[str] = None, batch: Optional[Batch] = None
    ):
        if not batch_id and not batch:
            raise ValueError("Batch id or Batch object must be provided")
        if batch:
            if not batch.id:
                raise ValueError("Batch must have an id")
            batch_id = batch.id

        response = self._delete("batches", batch_id)

        assert response.get("request_info", {}).get("success") is True

    def start_batch(
        self, batch_id: Optional[str] = None, batch: Optional[Batch] = None
    ):
        if not batch_id and not batch:
            raise ValueError("Batch id or Batch object must be provided")
        if batch:
            if not batch.id:
                raise ValueError("Batch must have an id")
            batch_id = batch.id
        response = self._get("batches", batch_id, "start")
        assert response.get("request_info", {}).get("success") is True

    def stop_batch(self, batch_id: Optional[str] = None, batch: Optional[Batch] = None):
        if not batch_id and not batch:
            raise ValueError("Batch id or Batch object must be provided")
        if batch:
            if not batch.id:
                raise ValueError("Batch must have an id")
            batch_id = batch.id
        response = self._get("batches", batch_id, "stop")
        assert response.get("request_info", {}).get("success") is True

    def stop_all(self):
        response = self._get("batches", "stop_all")
        assert response.get("request_info", {}).get("success") is True

    def add_searches(self, batch_id: str, searches: List[SearchParameters]):
        response = self._put(
            "batches",
            batch_id,
            body={"searches": [self.serialize(search) for search in searches]},
        )
        if response.get("request_info", {}).get("success") is True:
            return Batch(**response.get("batch"))
        else:
            raise ValueError(f"Failed to add searches to batch [{response.text}]")

    def update_search(self, batch_id: str, search: SearchParameters):
        response = self._post(
            "batches", batch_id, "searches", search.id, body=self.serialize(search)
        )
        if response.get("request_info", {}).get("success") is True:
            return SearchParameters(**response.get("search"))
        else:
            raise ValueError("Failed to update search")

    def iter_logs(self):
        page = 1
        while True:
            response = self._get("errorlogs", page=page)
            for error in response.get("logs", []):
                yield error

            errors_page_count = response.get("page_count_total", 0)
            errors_page_current = response.get("page", page)

            if errors_page_current >= errors_page_count:
                break

            page += 1


class ValueSerpProvider(BaseProvider[ValueSerp], ValueSerp):
    pass


class AsyncValueSerp:
    base_path = "https://api.valueserp.com/"

    @inject
    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        self._api_key = api_key or os.getenv("VALUESERP_API_KEY")
        self._bucket = S3BucketProvider().get(
            bucket_name="edgepath-serp-results",
            aws_access_key_id=os.getenv("AWS_ACCESS_TOKEN"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(120, connect=60.0),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        self._batches = {}
        self._batch_searches = collections.defaultdict(dict)
        self._batch_results = collections.defaultdict(list)

    @property
    def bucket(self) -> S3Bucket:
        if not self._bucket:
            raise ValueError("Bucket is not defined")
        return self._bucket

    def _build_url(self, *paths) -> str:
        return self.base_path + "/".join(map(str, paths))

    async def _get(self, *paths, **parameters) -> Dict[str, Any]:
        url = self._build_url(*paths)
        parameters["api_key"] = self._api_key
        async with self._client as client:
            response = await client.get(url, params=parameters)
            if response.status_code != 200:
                logger.error(response.text)
            response.raise_for_status()
            return response.json()

    async def _post(self, *paths, params: Dict = {}, body: Dict):
        url = self._build_url(*paths)
        params["api_key"] = self._api_key
        async with self._client as client:
            response = await client.post(url, params=params, json=body)
            if response.status_code != 200:
                logger.error(response.text)
            response.raise_for_status()
            return response.json()

    async def _put(self, *paths, params: Dict = {}, body: Dict):
        url = self._build_url(*paths)
        params["api_key"] = self._api_key
        try:
            async with self._client as client:
                response = await client.put(url, params=params, json=body)
                if response.status_code != 200:
                    logger.error(response.text)
                response.raise_for_status()

        except Exception as e:
            logger.error(e)
            logger.error(response.text)
            raise e
        return response.json()

    async def _delete(self, *paths, **parameters) -> dict:
        url = self._build_url(*paths)
        parameters["api_key"] = self._api_key
        async with self._client as client:
            response = await client.delete(url, params=parameters)
            response.raise_for_status()
            return response.json()

    async def search(self, query: SearchParameters):
        return ResultItems.model_validate(
            await self._get(
                "search", **query.model_dump(exclude_none=True, mode="json")
            )
        )

    async def get_batches(self, name: Optional[str] = None) -> List[Batch]:
        batches = []
        response = await self._get("batches")
        for batch in response.get("batches", []):
            obj = Batch(**batch)
            if name:
                if obj.name == name:
                    batches.append(obj)
            else:
                batches.append(obj)
        return batches

    async def list_destinations(self) -> List[Destination]:
        destinations = []
        response = await self._get("destinations")
        for destination in response.get("destinations", []):
            destinations.append(Destination(**destination))
        return destinations

    async def iter_batch_searches(
        self, batch_id: str
    ) -> AsyncGenerator[SearchParameters, None]:
        page = 1
        while True:
            try:
                response = await self._get("batches", batch_id, "searches", page)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 500:
                    break
                raise e
            for search in response.get("searches", []):
                yield SearchParameters(
                    **{
                        **search,
                        "batch_id": batch_id,
                    }
                )

            searches_page_count = response.get("searches_page_count", 0)
            searches_page_current = response.get("searches_page_current", 0)

            if searches_page_current >= searches_page_count:
                break

            page += 1

    async def get_batch_results(
        self,
        *,
        batch_id: Optional[str] = None,
        batch: Optional[Batch] = None,
        fetch_s3_links: bool = True,
        fetch_jsonlines_links: bool = True,
    ) -> BatchResults:
        if not batch_id and batch:
            batch_id = batch.id

        if not batch_id:
            raise ValueError("Must provide batch_id or batch")

        results = await self._get("batches", batch_id, "results")

        if fetch_s3_links and not fetch_jsonlines_links:
            for i, _result in enumerate(results.get("results", [])):
                s3_objects = await self.get_batch_s3_objects(
                    batch_id, _result.get("id")
                )
                results["results"][i]["s3_object_keys"] = [o.key for o in s3_objects]

        batch_results = BatchResults(**results)

        if not batch_results or batch_results.results is None:
            raise ValueError(f"Batch {batch_id} has no results")

        if fetch_jsonlines_links and batch_id:
            download_results = []
            for result in batch_results.results:
                _result: dict[str, dict[str, Any]] = await self._get(
                    "batches", batch_id, "results", result.id, "jsonlines"
                )
                s3_objects = await self.get_batch_s3_objects(batch_id, result.id)
                download_results.append(
                    dict(
                        **_result.get("result"),
                        s3_object_keys=[o.key for o in s3_objects],
                    )
                )

            batch_results = BatchResults(
                request_info=batch_results.request_info,
                batch_id=batch_results.batch_id,
                results=download_results,
            )

        return batch_results

    async def download_result_records(self, *, result: ResultSet):
        for link in result.get_download_links(filetype="jsonl"):
            async with self._client as client:
                async with client.stream("GET", link) as response:
                    with jsonlines.Reader(response.text) as reader:
                        for line in reader:
                            yield ResultRecord(
                                **line, result_id=result.id, batch_id=result.batch_id
                            )

    async def stream_result_records(
        self,
        *,
        result: ResultSet,
    ) -> AsyncGenerator[ResultRecord, None]:
        if result.s3_object_keys:
            s3_object_keys = [
                f for f in result.s3_object_keys if f.endswith(".jsonl")
            ] or result.s3_object_keys

            for key in s3_object_keys:
                obj = self.bucket.get_object(key)
                if not obj:
                    logger.error(f"Object not found: {key}")
                    continue
                if key.endswith(".jsonl"):
                    async for line in obj.read_jsonlines_async():
                        yield ResultRecord(
                            **line,
                            result_id=obj.result_id,
                            batch_id=result.batch_id,
                        )
                elif key.endswith(".json"):
                    data = await obj.read_async()
                    yield ResultRecord(
                        **data,
                        result_id=obj.result_id,
                        batch_id=result.batch_id,
                    )

    async def get_batch(self, batch_id: str) -> Batch:
        response = await self._get("batches", batch_id)
        return Batch(**response.get("batch", {}))

    async def get_batch_s3_objects(
        self,
        batch_id: str,
        result_id: int,
    ) -> List[S3Object]:
        if not self.bucket:
            raise ValueError("Bucket is not defined")
        objects = []
        async for obj in self.bucket.iter_items_async(
            prefix=f"Batch_Results_{batch_id}_{result_id}"
        ):
            objects.append(obj)
        return objects

    @classmethod
    def serialize(cls, obj: BaseModel, remove_attributes: List[str] = []):
        d = obj.model_dump(mode="json", exclude_none=True)
        return {
            k: v for k, v in d.items() if v is not None and k not in remove_attributes
        }

    async def create_batch(self, batch: Batch):
        response = await self._post("batches", body=self.serialize(batch))
        try:
            if response.get("request_info", {}).get("success") is True:
                return Batch(**response.get("batch"))
        except Exception as e:
            logger.error(e)

    async def update_batch(self, batch: Batch):
        if not batch.id:
            raise ValueError("Batch must have an id")
        response = await self._put("batches", batch.id, body=self.serialize(batch))
        try:
            if response.get("request_info", {}).get("success") is True:
                return Batch(**response.get("batch"))
        except Exception as e:
            logger.error(e)

    async def delete_batch(
        self, batch_id: Optional[str] = None, batch: Optional[Batch] = None
    ):
        if not batch_id and not batch:
            raise ValueError("Batch id or Batch object must be provided")
        if batch:
            if not batch.id:
                raise ValueError("Batch must have an id")
            batch_id = batch.id

        response = await self._delete("batches", batch_id)

        assert response.get("request_info", {}).get("success") is True

    async def start_batch(
        self, batch_id: Optional[str] = None, batch: Optional[Batch] = None
    ):
        if not batch_id and not batch:
            raise ValueError("Batch id or Batch object must be provided")
        if batch:
            if not batch.id:
                raise ValueError("Batch must have an id")
            batch_id = batch.id
        response = await self._get("batches", batch_id, "start")
        assert response.get("request_info", {}).get("success") is True

    async def stop_batch(
        self, batch_id: Optional[str] = None, batch: Optional[Batch] = None
    ):
        if not batch_id and not batch:
            raise ValueError("Batch id or Batch object must be provided")
        if batch:
            if not batch.id:
                raise ValueError("Batch must have an id")
            batch_id = batch.id
        response = await self._get("batches", batch_id, "stop")
        assert response.get("request_info", {}).get("success") is True

    async def stop_all(self):
        response = await self._get("batches", "stop_all")
        assert response.get("request_info", {}).get("success") is True

    async def add_searches(self, batch_id: str, searches: List[SearchParameters]):
        response = await self._put(
            "batches",
            batch_id,
            body={"searches": [self.serialize(search) for search in searches]},
        )
        if response.get("request_info", {}).get("success") is True:
            return Batch(**response.get("batch"))
        else:
            raise ValueError(f"Failed to add searches to batch [{response.text}]")

    async def update_search(self, batch_id: str, search: SearchParameters):
        response = await self._post(
            "batches", batch_id, "searches", search.id, body=self.serialize(search)
        )
        if response.get("request_info", {}).get("success") is True:
            return SearchParameters(**response.get("search"))
        else:
            raise ValueError("Failed to update search")

    async def iter_logs(self):
        page = 1
        while True:
            response = await self._get("errorlogs", page=page)
            for error in response.get("logs", []):
                yield error

            errors_page_count = response.get("page_count_total", 0)
            errors_page_current = response.get("page", page)

            if errors_page_current >= errors_page_count:
                break

            page += 1


class AsyncValueSerpProvider(BaseProvider[AsyncValueSerp], AsyncValueSerp):
    pass
