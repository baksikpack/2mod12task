import dataclasses
import datetime


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


@dataclasses.dataclass
class Ad:
    pk: int
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    body: str
    deleted: bool = False


class AdStore:
    def __init__(self):
        self.ads = []
        self.create(author="foo", body="first")
        self.create(author="foo", body="second")
        self.create(author="bar", body="third")

    def all(self) -> list[Ad]:
        return [x for x in self.ads if not x.deleted]

    def create(self, author: str, body: str):
        self.ads.append(Ad(pk=len(self.ads), created_by=author, body=body, created_at=now(), updated_at=now()))

    def read(self, pk) -> Ad:
        return self.ads[pk]

    def update(self, pk: int, body: str):
        self.ads[pk].body = body
        self.ads[pk].updated_at = now()

    def delete(self, pk: int):
        self.ads[pk].updated_at = now()
        self.ads[pk].deleted = True

    def delete_old(self, seconds: int) -> list[Ad]:
        current = now()
        deleted = []
        for ad in self.all():
            if ad.created_at + datetime.timedelta(seconds=seconds) < current:
                self.delete(ad.pk)
                deleted.append(ad)
        return deleted


ad_store = AdStore()
