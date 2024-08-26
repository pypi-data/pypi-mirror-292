from __future__ import annotations

from enum import IntEnum, StrEnum, auto


class Event(StrEnum):
  adPlaying = auto()
  autoplayUpNext = auto()
  nowAutoplaying = auto()
  onAdStateChange = auto()
  onAudioTrackChanged = auto()
  onAutoplayModeChanged = auto()
  onHasPreviousNextChanged = auto()
  onPlaylistModeChanged = auto()
  onSubtitlesTrackChanged = auto()
  onVideoQualityChanged = auto()
  onVolumeChanged = auto()
  playlistModified = auto()

  loungeScreenDisconnected = auto()
  noop = auto()
  loungeStatus = auto()
  nowPlaying = auto()
  onStateChange = auto()


class MsgType(StrEnum):
  REFRESH = auto()
  PAIR = auto()
  LINK = auto()

  PAIRED = auto()
  LINKED = auto()

  BEGIN_AD = auto()
  END_AD = auto()
  SKIP_AD = auto()
  MUTE_AD = auto()

  GOT_ART = auto()
  GOT_TITLE = auto()
  GOT_AUTH_STATE = auto()
  LOAD_AUTH_STATE = auto()

  CONNECTED = auto()
  DISCONNECTED = auto()

  PREVIOUS = auto()
  NEXT = auto()
  PLAY = auto()
  PAUSE = auto()
  STOP = auto()
  SET_VOLUME = auto()
  SEEK = auto()

  PAUSED = auto()
  PLAYING = auto()
  STOPPED = auto()
  BUFFERING = auto()
  STARTING = auto()

  AUTOPLAY_UP_NEXT = auto()
  LOUNGE_STATUS = auto()
  NOW_AUTOPLAYING = auto()
  NOW_PLAYING = auto()
  AD_STATE_CHANGE = auto()
  AUDIO_TRACK_CHANGE = auto()
  AUTOPLAY_MODE_CHANGE = auto()
  HAS_PREV_NEXT_CHANGE = auto()
  PLAYLIST_MODE_CHANGE = auto()
  STATE_CHANGE = auto()
  SUBTITLES_TRACK_CHANGE = auto()
  VIDEO_QUALITY_CHANGE = auto()
  VOLUME_CHANGE = auto()
  PLAYLIST_MODIFIED = auto()

  DEVICE_INFO = auto()


class LoungeState(IntEnum):
  AD = 1081
  BUFFERING = 0
  PAUSED = 2
  PLAYING = 1
  STARTING = 3
  STOPPED = -1

  STATE4 = 4
  STATE5 = 5
