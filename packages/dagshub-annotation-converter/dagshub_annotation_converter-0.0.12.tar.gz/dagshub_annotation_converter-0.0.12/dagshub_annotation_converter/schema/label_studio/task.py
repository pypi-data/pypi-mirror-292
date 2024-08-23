import datetime
import random
from typing import Any, Sequence, Type, Optional, Dict, List

from typing_extensions import Annotated

from pydantic import BaseModel, SerializeAsAny, Field, BeforeValidator

from dagshub_annotation_converter.schema.label_studio.abc import AnnotationResultABC
from dagshub_annotation_converter.schema.label_studio.keypointlabels import KeyPointLabelsAnnotation
from dagshub_annotation_converter.schema.label_studio.polygonlabels import PolygonLabelsAnnotation
from dagshub_annotation_converter.schema.label_studio.rectanglelabels import RectangleLabelsAnnotation

task_lookup: Dict[str, Type[AnnotationResultABC]] = {
    "polygonlabels": PolygonLabelsAnnotation,
    "rectanglelabels": RectangleLabelsAnnotation,
    "keypointlabels": KeyPointLabelsAnnotation,
}


def ls_annotation_validator(v: Any) -> List[AnnotationResultABC]:
    assert isinstance(v, list)

    annotations: List[AnnotationResultABC] = []

    for raw_annotation in v:
        assert isinstance(raw_annotation, dict)
        assert "type" in raw_annotation
        assert raw_annotation["type"] in task_lookup

        ann_class = task_lookup[raw_annotation["type"]]
        annotations.append(ann_class.parse_obj(raw_annotation))

    return annotations


AnnotationsList = Annotated[List[SerializeAsAny[AnnotationResultABC]], BeforeValidator(ls_annotation_validator)]


class AnnotationsContainer(BaseModel):
    completed_by: Optional[int] = None
    result: AnnotationsList = []
    ground_truth: bool = False


PosePointsLookupKey = "pose_points"
PoseBBoxLookupKey = "pose_boxes"


class LabelStudioTask(BaseModel):
    annotations: List[AnnotationsContainer] = Field(
        default_factory=lambda: [],
    )
    meta: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    project: int = 0
    created_at: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    updated_at: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    id: int = Field(default_factory=lambda: random.randint(0, 2**63 - 1))

    user_id: int = Field(exclude=True, default=1)

    def add_annotation(self, annotation: AnnotationResultABC):
        if len(self.annotations) == 0:
            self.annotations.append(AnnotationsContainer(completed_by=self.user_id))
        self.annotations[0].result.append(annotation)

    def add_annotations(self, annotations: Sequence[AnnotationResultABC]):
        for ann in annotations:
            self.add_annotation(ann)

    def log_pose_metadata(self, bbox: RectangleLabelsAnnotation, keypoints: List[KeyPointLabelsAnnotation]):
        if PosePointsLookupKey not in self.data:
            self.data[PosePointsLookupKey] = []
        if PoseBBoxLookupKey not in self.data:
            self.data[PoseBBoxLookupKey] = []

        self.data[PoseBBoxLookupKey].append(bbox.id)
        self.data[PosePointsLookupKey].append([point.id for point in keypoints])
