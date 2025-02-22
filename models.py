from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# Daily Challenge Models
class AuthorCreator(BaseModel):
    id: str
    name: str
    avatarImage: str
    customName: Optional[str]
    customAvatarImage: Optional[str]
    signupAssetIds: List[str]
    signupCoins: int
    youtubeLink: str
    twitchLink: str
    twitterLink: str
    instagramLink: str
    program: Optional[str]

class LeaderboardEntry(BaseModel):
    id: str
    nick: str
    pinUrl: str
    totalScore: int
    totalTime: int
    totalDistance: float
    isOnLeaderboard: bool
    isVerified: bool
    flair: int
    countryCode: str
    currentStreak: int
    totalStepsCount: int

class DailyChallengeResponse(BaseModel):
    authorCreator: AuthorCreator
    date: datetime
    description: Optional[str]
    participants: int
    token: str
    pickedWinner: bool
    leaderboard: List[LeaderboardEntry]
    friends: List[LeaderboardEntry]
    country: List[LeaderboardEntry]

# Game Models
class Round(BaseModel):
    score: int
    distance: float
    roundNumber: int

class DailyChallengeGame(BaseModel):
    token: str
    totalScore: int
    totalDistance: float
    rounds: List[Round]
    date: date

class GameRound(BaseModel):
    lat: float
    lng: float
    panoId: str
    heading: float
    pitch: float
    zoom: float
    streakLocationCode: Optional[str]
    startTime: datetime

class ScoreUnit(BaseModel):
    amount: str
    unit: str
    percentage: Optional[float]

class Distance(BaseModel):
    meters: Dict[str, str]
    miles: Dict[str, str]

class PlayerGuess(BaseModel):
    lat: float
    lng: float
    timedOut: bool
    timedOutWithGuess: bool
    skippedRound: bool
    roundScore: ScoreUnit
    roundScoreInPercentage: float
    roundScoreInPoints: int
    distance: Distance
    distanceInMeters: float
    stepsCount: int
    streakLocationCode: Optional[str]
    time: int

class Player(BaseModel):
    totalScore: ScoreUnit
    totalDistance: Distance
    totalDistanceInMeters: float
    totalStepsCount: int
    totalTime: int
    totalStreak: int
    guesses: List[PlayerGuess]
    isLeader: bool
    currentPosition: int
    pin: Dict[str, str]
    newBadges: List
    explorer: Optional[Dict[str, Any]]
    id: str
    nick: str
    isVerified: bool
    flair: int
    countryCode: str

class GameResponse(BaseModel):
    token: str
    type: str
    mode: str
    state: str
    roundCount: int
    timeLimit: int
    forbidMoving: bool
    forbidZooming: bool
    forbidRotating: bool
    streakType: str
    map: str
    mapName: str
    panoramaProvider: int
    bounds: Dict[str, Dict[str, float]]
    round: int
    rounds: List[GameRound]
    player: Player 