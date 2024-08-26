from __future__ import annotations

from json import dumps, loads
from typing import Self, TypedDict

from pydantic import BaseModel

from .enums import MsgType


type JsonVal = bool | int | float | str | Json | list | None
type Json = dict[str, JsonVal]


class MessageJson(TypedDict):
  type: MsgType
  content: JsonVal


class MetadataJson(TypedDict):
  state: int
  currentTime: float
  duration: float
  videoId: str


class WithJson(BaseModel):
  @property
  def json(self) -> Json:
    return self.model_dump()

  @property
  def jsons(self) -> str:
    return dumps(self.json)

  @classmethod
  def from_json(cls, json: str) -> Self:
    return cls(**loads(json))


class Message(WithJson):
  type: MsgType
  content: JsonVal | None = None


class PlaybackData(WithJson):
  state: int
  currentTime: float
  videoId: str
  duration: float

  @staticmethod
  def from_event(state: 'PlaybackState') -> PlaybackData:
    return PlaybackData(
      state=state.state,
      currentTime=state.currentTime,
      videoId=state.videoId,
      duration=state.duration
    )
