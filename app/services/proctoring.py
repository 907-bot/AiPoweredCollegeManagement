"""AI-Powered Behavior Analysis Service.

This module provides advanced AI-based proctoring capabilities including:
- Face detection and recognition
- Gaze detection (looking away from screen)
- Multiple person detection
- Object detection (phones, books, etc.)
- Audio anomaly detection
- Behavioral pattern analysis
"""
import base64
import io
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np
import cv2
from PIL import Image


class EventType(str, Enum):
    """Types of behavioral events."""
    FACE_NOT_DETECTED = "face_not_detected"
    MULTIPLE_FACES = "multipleFaces"
    GAZE_AWAY = "gazeAway"
    SUSPICIOUS_MOVEMENT = "suspiciousMovement"
    OBJECT_DETECTED = "objectDetected"
    AUDIO_ANOMALY = "audioAnomaly"
    TAB_SWITCH = "tabSwitch"
    COPY_PASTE_ATTEMPT = "copyPasteAttempt"
    SCREEN_SHARE_DETECTED = "screenShareDetected"
    LOW_LIGHT = "lowLight"
    NO_FACE_CLEAR = "noFaceClear"


class SeverityLevel(float, Enum):
    """Severity levels for events."""
    INFO = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    CRITICAL = 1.0


@dataclass
class BehaviorEvent:
    """Single behavior event."""
    event_type: EventType
    severity: float
    details: dict = field(default_factory=dict)
    frame_data: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class BehaviorAnalysisResult:
    """Result of behavior analysis."""
    session_id: int
    frame_count: int
    events: list[BehaviorEvent]
    confidence_score: float
    behavior_score: float
    is_flagged: bool
    summary: dict


class FaceDetector:
    """Face detection using Haar Cascade or MediaPipe."""

    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect_faces(self, frame: np.ndarray) -> tuple[list, float]:
        """Detect faces in frame.

        Args:
            frame: RGB or BGR frame as numpy array

        Returns:
            Tuple of (bounding_boxes, avg_confidence)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Convert to list of bounding boxes
        boxes = []
        for (x, y, w, h) in faces:
            boxes.append({
                "bbox": [int(x), int(y), int(w), int(h)],
                "confidence": 0.8
            })

        avg_conf = sum(b["confidence"] for b in boxes) / len(boxes) if boxes else 0.0
        return boxes, avg_conf

    def count_faces(self, frame: np.ndarray) -> int:
        """Count number of faces in frame."""
        boxes, _ = self.detect_faces(frame)
        return len(boxes)


class GazeTracker:
    """Track eye gaze direction to detect looking away."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.history: list[bool] = []
        self.max_history = 30  # Track last 30 frames

    def analyze_gaze(self, frame: np.ndarray, face_bbox: Optional[dict] = None) -> dict:
        """Analyze gaze direction.

        Simple heuristic-based gaze detection using face position and size.
        In production, use MediaPipe FaceMesh for precise landmarks.

        Returns:
            Dict with gaze_direction and confidence
        """
        if face_bbox is None:
            return {"direction": "unknown", "confidence": 0.0}

        bbox = face_bbox.get("bbox", [0, 0, 0, 0])
        x, y, w, h = bbox

        # Simple heuristics based on face position and size
        # In reality, you'd use facial landmarks
        center_x = x + w / 2
        center_y = y + h / 2

        frame_height, frame_width = frame.shape[:2]

        # Determine general direction
        horizontal_pos = center_x / frame_width
        vertical_pos = center_y / frame_height

        if horizontal_pos < 0.4:
            direction = "left"
        elif horizontal_pos > 0.6:
            direction = "right"
        elif vertical_pos < 0.4:
            direction = "up"
        elif vertical_pos > 0.6:
            direction = "down"
        else:
            direction = "center"

        # Confidence based on face size (larger = more frontal = confident)
        face_ratio = (w * h) / (frame_width * frame_height)
        confidence = min(face_ratio * 10, 1.0)

        return {
            "direction": direction,
            "confidence": confidence,
            "looking_away": direction != "center" and confidence < self.threshold
        }

    def is_looking_away(self, frame: np.ndarray, face_bbox: Optional[dict] = None) -> bool:
        """Check if person is looking away."""
        gaze = self.analyze_gaze(frame, face_bbox)
        return gaze.get("looking_away", False)


class ObjectDetector:
    """Detect suspicious objects like phones, books, etc."""

    def __init__(self):
        # Simple color-based object detection
        # In production, use YOLO or similar object detection model
        self.suspicious_colors = {
            "phone": ([0, 0, 139], [100, 100, 255]),  # Blue-ish (common for phones)
            "book": ([0, 100, 0], [100, 200, 100]),  # Green-ish (books)
        }

    def detect_objects(self, frame: np.ndarray) -> list[dict]:
        """Detect suspicious objects in frame."""
        # Simplified - in production use ML model
        objects = []

        # This is a placeholder for actual object detection
        # Would use something like YOLOv8 in production

        return objects


class BehaviorAnalyzer:
    """Main behavior analyzer combining all detection systems."""

    def __init__(
        self,
        max_faces: int = 1,
        gaze_threshold: float = 0.5,
        absence_threshold: int = 30,
        severity_threshold: float = 0.5,
    ):
        self.max_faces = max_faces
        self.gaze_threshold = gaze_threshold
        self.absence_threshold = absence_threshold
        self.severity_threshold = severity_threshold

        # Initialize detectors
        self.face_detector = FaceDetector()
        self.gaze_tracker = GazeTracker(threshold=gaze_threshold)
        self.object_detector = ObjectDetector()

        # State tracking
        self.frames_not_present = 0
        self.frames_looking_away = 0
        self.events_buffer: list[BehaviorEvent] = []

    def analyze_frame(
        self,
        frame_data: bytes,
        session_id: int,
    ) -> BehaviorAnalysisResult:
        """Analyze a single frame for behavioral anomalies.

        Args:
            frame_data: Raw image bytes from webcam
            session_id: Current exam session ID

        Returns:
            BehaviorAnalysisResult with detected events and scores
        """
        # Decode frame
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return BehaviorAnalysisResult(
                session_id=session_id,
                frame_count=0,
                events=[],
                confidence_score=0.0,
                behavior_score=100.0,
                is_flagged=False,
                summary={},
            )

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        events = []

        # 1. Detect faces
        faces, confidence = self.face_detector.detect_faces(frame)

        if len(faces) == 0:
            # No face detected
            self.frames_not_present += 1
            if self.frames_not_present == self.absence_threshold:
                events.append(BehaviorEvent(
                    event_type=EventType.FACE_NOT_DETECTED,
                    severity=SeverityLevel.HIGH.value,
                    details={"frames_missing": self.frames_not_present},
                ))
        elif len(faces) > self.max_faces:
            # Multiple faces detected
            events.append(BehaviorEvent(
                event_type=EventType.MULTIPLE_FACES,
                severity=SeverityLevel.CRITICAL.value,
                details={
                    "faces_count": len(faces),
                    "max_allowed": self.max_faces,
                },
                frame_data=self._encode_frame_thumbnail(frame),
            ))
            self.frames_not_present = 0
        else:
            self.frames_not_present = max(0, self.frames_not_present - 1)

            # 2. Analyze gaze for single face
            face_bbox = faces[0]
            looking_away = self.gaze_tracker.is_looking_away(frame, face_bbox)

            if looking_away:
                self.frames_looking_away += 1
                if self.frames_looking_away >= 10:
                    events.append(BehaviorEvent(
                        event_type=EventType.GAZE_AWAY,
                        severity=SeverityLevel.MEDIUM.value,
                        details={"consecutive_frames": self.frames_looking_away},
                    ))
            else:
                self.frames_looking_away = max(0, self.frames_looking_away - 1)

        # 3. Check for suspicious objects
        objects = self.object_detector.detect_objects(frame)
        if objects:
            events.append(BehaviorEvent(
                event_type=EventType.OBJECT_DETECTED,
                severity=SeverityLevel.MEDIUM.value,
                details={"objects": objects},
            ))

        # Buffer events
        self.events_buffer.extend(events)

        # Calculate behavior score
        total_severity = sum(e.severity for e in self.events_buffer)
        behavior_score = max(0, 100 - total_severity * 10)

        is_flagged = any(
            e.severity >= self.severity_threshold
            for e in self.events_buffer
        )

        # Generate summary
        summary = {
            "total_events": len(self.events_buffer),
            "face_detected": len(faces) > 0,
            "confidence": confidence,
            "absence_frames": self.frames_not_present,
            "gaze_away_frames": self.frames_looking_away,
        }

        return BehaviorAnalysisResult(
            session_id=session_id,
            frame_count=1,
            events=events,
            confidence_score=confidence,
            behavior_score=behavior_score,
            is_flagged=is_flagged,
            summary=summary,
        )

    def _encode_frame_thumbnail(self, frame: np.ndarray, size: tuple[int, int] = (160, 120)) -> str:
        """Encode frame as base64 thumbnail."""
        # Resize
        thumbnail = cv2.resize(frame, size)
        thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_RGB2BGR)

        # Encode
        _, buffer = cv2.imencode('.jpg', thumbnail)
        return base64.b64encode(buffer).decode()

    def get_cumulative_analysis(self) -> dict:
        """Get cumulative analysis of all buffered events."""
        events_by_type = {}

        for event in self.events_buffer:
            etype = event.event_type.value
            if etype not in events_by_type:
                events_by_type[etype] = []
            events_by_type[etype].append(event)

        return {
            "total_events": len(self.events_buffer),
            "events_by_type": {k: len(v) for k, v in events_by_type.items()},
            "avg_severity": np.mean([e.severity for e in self.events_buffer]) if self.events_buffer else 0,
            "max_severity": max([e.severity for e in self.events_buffer]) if self.events_buffer else 0,
            "is_flagged": any(e.severity >= self.severity_threshold for e in self.events_buffer),
        }

    def reset(self):
        """Reset analyzer state."""
        self.frames_not_present = 0
        self.frames_looking_away = 0
        self.events_buffer = []


# Singleton instance
_analyzer: Optional[BehaviorAnalyzer] = None


def get_analyzer(**kwargs) -> BehaviorAnalyzer:
    """Get or create behavior analyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = BehaviorAnalyzer(**kwargs)
    return _analyzer


async def analyze_webcam_frame(
    frame_data: bytes,
    session_id: int,
) -> dict:
    """Async wrapper for frame analysis."""
    analyzer = get_analyzer()
    result = analyzer.analyze_frame(frame_data, session_id)
    return {
        "session_id": result.session_id,
        "events": [
            {
                "type": e.event_type.value,
                "severity": e.severity,
                "details": e.details,
            }
            for e in result.events
        ],
        "score": result.behavior_score,
        "flagged": result.is_flagged,
        "summary": result.summary,
    }