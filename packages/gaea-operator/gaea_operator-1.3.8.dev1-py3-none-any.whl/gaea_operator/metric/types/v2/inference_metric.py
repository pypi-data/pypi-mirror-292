#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/8/21
# @Author  : yanxiaodong
# @File    : inference_metric.py
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

from windmillmodelv1.client.model_api_model import Label

from ..metric import BaseMetric


class MetricName(Enum):
    """
    Image metric
    """
    image_accuracy = "imageAccuracy"
    image_precision = "imagePrecision"
    image_recall = "imageRecall"
    image_label_metric = "imageLabelMetric"


class MetricDisplayName(Enum):
    """
    Image metric display name
    """
    accuracy = "Accuracy(准确率)"
    precision = "Precision(精确率)"
    recall = "Recall(召回率)"
    label_metric = "图像级别评估结果"


class MetricCategory(Enum):
    """
    Metric category
    """
    category_image = "Image/Image"
    category_bbox = "Image/BBox"


class MetricDisplayType(Enum):
    """
    Metric display type
    """
    table = "table"  # 表格展示
    chart = "chart"  # 曲线图展示
    card = "card"  # 卡片展示


class LabelMetricResult(BaseModel):
    """
    Metric result
    """
    label_name: Optional[str] = Field(None, alias="labelName")
    result: Optional[float] = None


class LabelMetricResults(BaseModel):
    """
    Inference label metric result
    """
    label_name: Optional[str] = Field(None, alias="labelName")
    precision: Optional[Union[float, List[LabelMetricResult]]] = None
    recall: Optional[Union[float, List[LabelMetricResult]]] = None
    accuracy: Optional[Union[float, List[LabelMetricResult]]] = None


class InferenceLabelMetric(BaseModel):
    """
    Inference label metric
    """
    name: Optional[str] = MetricName.image_label_metric.value
    display_name: Optional[str] = Field(MetricDisplayName.label_metric.value, alias="displayName")
    column_annotation_specs: Optional[List[str]] = Field(None, alias="columnAnnotationSpecs")
    category: Optional[str] = None
    display_type: Optional[str] = Field(None, alias="displayType")
    result: Optional[List[LabelMetricResults]] = None


class InferenceSingleMetric(BaseModel):
    """
    Inference image metric
    """
    name: Optional[str] = None
    display_name: Optional[str] = Field(None, alias="displayName")
    category: Optional[str] = None
    display_type: Optional[str] = Field(None, alias="displayType")
    result: Optional[float] = None


class InferenceMetric(BaseMetric):
    """
    Object Detection Metric
    """
    labels: Optional[List[Label]] = None
    metrics: Optional[List[Union[InferenceLabelMetric, InferenceSingleMetric]]] = None