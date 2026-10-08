"""Transactional SQLAlchemy repository; store each search as an immutable snapshot."""

from pathlib import Path
from typing import Protocol

from sqlalchemy import ForeignKey, Integer, JSON, String, create_engine, event, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .models import DiscoveryResult


class DiscoveryRepository(Protocol):
    def save(self, result: DiscoveryResult) -> None: ...
    def load(self, search_id: str) -> DiscoveryResult | None: ...


class Base(DeclarativeBase):
    pass


class SearchRecord(Base):
    __tablename__ = "searches"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)


class BusinessRecord(Base):
    __tablename__ = "businesses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    search_id: Mapped[str] = mapped_column(ForeignKey("searches.id"), index=True)
    internal_id: Mapped[str] = mapped_column(String, index=True)
    data: Mapped[dict] = mapped_column(JSON)


class ObservationRecord(Base):
    __tablename__ = "observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    scope: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSON)


class EnrichmentRecord(Base):
    __tablename__ = "enrichment_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    data: Mapped[dict] = mapped_column(JSON)


class ScoreRecord(Base):
    __tablename__ = "scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class SQLiteRepository:
    def __init__(self, path: Path):
        path = Path(path)
        if path.is_symlink() or path.suffix not in {".sqlite", ".sqlite3", ".db"}:
            raise ValueError("Database must be a regular .sqlite, .sqlite3 or .db file")
        if path.exists():
            with path.open("rb") as stream:
                if stream.read(16) != b"SQLite format 3\x00":
                    raise ValueError("Refusing to use an existing non-SQLite file as database")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(URL.create("sqlite", database=str(path)), connect_args={"timeout": 5})

        @event.listens_for(self.engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)

    def close(self):
        self.engine.dispose()

    def save(self, result: DiscoveryResult):
        data = result.model_dump(mode="json", exclude={"qualifications"})
        with Session(self.engine) as session, session.begin():
            session.add(SearchRecord(id=result.search_id, data=data))
            session.flush()
            for qualification in result.qualifications:
                business = qualification.business
                record = BusinessRecord(search_id=result.search_id, internal_id=business.internal_id,
                                        data=business.model_dump(mode="json", exclude={"observations"}))
                session.add(record)
                session.flush()
                for scope, items in (("business", business.observations), ("enrichment", qualification.enrichment.observations)):
                    for item in items:
                        session.add(ObservationRecord(business_id=record.id, scope=scope, data=item.model_dump(mode="json")))
                session.add(EnrichmentRecord(id=qualification.enrichment.id, business_id=record.id,
                                             data=qualification.enrichment.model_dump(mode="json", exclude={"observations"})))
                for name, score in qualification.scores.model_dump(mode="json").items():
                    session.add(ScoreRecord(business_id=record.id, name=name, data=score))

    def load(self, search_id):
        with Session(self.engine) as session:
            search = session.get(SearchRecord, search_id)
            if search is None:
                return None
            qualifications = []
            records = session.scalars(select(BusinessRecord).where(BusinessRecord.search_id == search_id).order_by(BusinessRecord.id))
            for record in records:
                business = dict(record.data)
                enrichment = dict(session.scalars(select(EnrichmentRecord).where(
                    EnrichmentRecord.business_id == record.id)).one().data)
                business["observations"], enrichment["observations"] = [], []
                for item in session.scalars(select(ObservationRecord).where(
                        ObservationRecord.business_id == record.id).order_by(ObservationRecord.id)):
                    (business if item.scope == "business" else enrichment)["observations"].append(item.data)
                scores = {item.name: item.data for item in session.scalars(select(ScoreRecord).where(ScoreRecord.business_id == record.id))}
                qualifications.append({"business": business, "enrichment": enrichment, "scores": scores})
            return DiscoveryResult.model_validate({**search.data, "qualifications": qualifications})
