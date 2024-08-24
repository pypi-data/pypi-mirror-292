
from pydantic import BaseModel


class WordnikAudio(BaseModel):
    attributionText: str
    attributionUrl: str
    audioType: str
    commentCount: int
    createdAt: str
    createdBy: str
    description: str | None = None
    duration: float
    fileUrl: str
    id: int
    voteAverage: int | None = None
    voteCount: int | None = None
    voteWeightedAverage: int | None = None
    word: str
