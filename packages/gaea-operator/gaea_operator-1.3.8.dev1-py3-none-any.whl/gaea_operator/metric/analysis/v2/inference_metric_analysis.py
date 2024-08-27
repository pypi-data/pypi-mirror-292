#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/24
# @Author  : yanxiaodong
# @File    : inference.py
"""
from typing import List, Dict, Union
import os
from collections import defaultdict
import numpy as np
import math

import bcelogger

from gaea_operator.utils import write_file
from gaea_operator.metric.operator import PrecisionRecallF1score, Accuracy
from gaea_operator.metric.types.v2.inference_metric import \
    MetricCategory, \
    InferenceMetric, \
    InferenceSingleMetric, \
    LabelMetricResults, \
    LabelMetricResult, \
    InferenceLabelMetric
from gaea_operator.metric.types.v2.inference_metric import MetricDisplayName, MetricName, MetricDisplayType


class InferenceMetricAnalysis(object):
    """
    Inference metric analysis.
    """

    def __init__(self,
                 labels: List = None,
                 images: List[Dict] = None,
                 conf_threshold: Union[float, List] = 0,
                 iou_threshold: Union[float, List] = 0):
        self.iou_threshold = iou_threshold
        self.conf_threshold = conf_threshold

        self.labels = []

        self.image_dict: Dict[int, List] = defaultdict(list)
        self.img_id_str2int: Dict[str, int] = {}
        self.label_sum = 0
        self.label_ids: Dict[int, List] = defaultdict(list)
        self.label_id2index: Dict[int, int] = {}
        self.label_inner_id2index: Dict[int, Dict] = defaultdict(dict)
        self.label_id2name: Dict[int, str] = {}
        self.label_inner_id2name: Dict[int, Dict] = defaultdict(dict)
        self.metric: Dict[str, Dict] = defaultdict(dict)

        self.set_images(images)
        self.set_labels(labels)

    def reset(self):
        """
        Reset metric.
        """
        for _, metric_dict in self.metric.items():
            for _, metric_list in metric_dict.items():
                for metric in metric_list:
                    metric.reset()

    def set_images(self, images: List[Dict]):
        """
        Set images.
        """
        if images is None:
            return
        self.image_dict = {item["image_id"]: item for item in images}
        self.img_id_str2int = {key: idx + 1 for idx, key in enumerate(self.image_dict)}

    def set_labels(self, labels: List):
        """
        Set labels.
        """
        if labels is None:
            return

        index = 0
        for label in labels:
            label["id"] = int(label["id"])
            if "label" not in label or len(label["label"]) == 0:
                self.label_ids[label["id"]].append({"id": label["id"], "index": index, "parent_id": -1})
                self.label_id2index[label["id"]] = index
                index += 1
            else:
                for item in label["label"]:
                    item["id"] = int(item["id"])
                    self.label_ids[label["id"]].append({"id": item["id"], "index": index, "parent_id": label["id"]})
                    self.label_inner_id2index[label["id"]].update({item["id"]: index})
                    self.label_inner_id2name[label["id"]].update({item["id"]: item["name"]})
                    index += 1
                self.label_ids[label["id"]].append({"id": label["id"], "index": index, "parent_id": -1})
                self.label_id2index[label["id"]] = index
                index += 1
            self.label_id2name[label["id"]] = label["name"]
            self.labels.append(label)
        bcelogger.info(f"Set labels: {self.labels}")
        bcelogger.info(f"Set label ids: {self.label_ids}")

        self.set_metric()

    def set_metric(self):
        """
        Set metric.
        """
        for idx, label in self.label_ids.items():
            for item in label:
                if item["parent_id"] == -1 and len(label) >= 2:
                    _metric = [Accuracy(num_classes=len(label) - 1)]
                    self.metric[MetricCategory.category_image.value].update({item["index"]: _metric})
                    continue
                _metric = [Accuracy(num_classes=2), PrecisionRecallF1score(num_classes=2)]
                self.metric[MetricCategory.category_image.value].update({item["index"]: _metric})
        bcelogger.info(f"Set metric: {self.metric}")

    def update(self, predictions: List[Dict], references: List[Dict], **kwargs):
        """
        Update metric.
        """
        for category, metric_dict in self.metric.items():
            if category == MetricCategory.category_image.value:
                predictions, references = self._format_input_to_image(predictions, references)

            for index, metric_list in metric_dict.items():
                for metric in metric_list:
                    metric.update(predictions=predictions[:, index], references=references[:, index])

    def _format_input_to_image(self, predictions: List[Dict], references: List[Dict]):
        """
        Format to object detection metric.
        """
        self.label_sum = sum([len(label) for _, label in self.label_ids.items()])

        reference_dict: Dict[int, List] = defaultdict(list)
        for item in references:
            im_id = item["image_id"]
            im_id_int = self.img_id_str2int[im_id]
            array_item = np.zeros(self.label_sum, dtype=np.int8)

            if item.get("annotations") is None:
                reference_dict[im_id_int].append(array_item)
                continue

            for anno in item["annotations"]:
                for idx in range(len(anno["labels"])):
                    label = anno["labels"][idx]

                    if isinstance(label["id"], str):
                        label["id"] = int(label["id"])
                    # 如果标注标签id不在label,则跳过（修改了标签但是标注没有同步修改）
                    if "parent_id" not in label and label["id"] not in self.label_id2index:
                        continue
                    if "parent_id" in label and isinstance(label["parent_id"], str):
                        label["parent_id"] = int(label["parent_id"])
                    # 如果多属性标注属性id不在label,则跳过
                    if "parent_id" in label and label["id"] not in self.label_inner_id2index[label["parent_id"]]:
                        continue

                    if "parent_id" in label:
                        array_item[self.label_inner_id2index[label["parent_id"]][label["id"]]] = 1
                        array_item[self.label_id2index[label["parent_id"]]] = label["id"]
                        continue
                    array_item[self.label_id2index[label["id"]]] = 1
            reference_dict[im_id_int].append(array_item)
        bcelogger.info(f"The number of reference images {len(reference_dict)}")

        prediction_dict: Dict[int, List] = defaultdict(list)
        for item in predictions:
            im_id = item["image_id"]
            im_id_int = self.img_id_str2int[im_id]
            array_item = np.zeros(self.label_sum, dtype=np.int8)

            # 如果预测结果不在 gt里面，是一张未标注的图片，不参与指标计算
            if im_id_int not in reference_dict:
                continue
            if item.get("annotations") is None:
                prediction_dict[im_id_int].append(array_item)
                continue

            for anno in item["annotations"]:
                for idx in range(len(anno["labels"])):
                    label = anno["labels"][idx]

                    if isinstance(label["id"], str):
                        label["id"] = int(label["id"])
                    if math.isnan(label["confidence"]):
                        continue
                    # 如果标注标签id不在label,则跳过（修改了标签但是标注没有同步修改）
                    if "parent_id" not in label and label["id"] not in self.label_id2index:
                        continue
                    if "parent_id" in label and isinstance(label["parent_id"], str):
                        label["parent_id"] = int(label["parent_id"])
                    # 如果多属性标注属性id不在label,则跳过
                    if "parent_id" in label and label["id"] not in self.label_inner_id2index[label["parent_id"]]:
                        continue
                    if label["confidence"] < self.conf_threshold:
                        continue

                    if "parent_id" in label:
                        array_item[self.label_inner_id2index[label["parent_id"]][label["id"]]] = 1
                        array_item[self.label_id2index[label["parent_id"]]] = label["id"]
                        continue
                    array_item[self.label_id2index[label["id"]]] = 1
            prediction_dict[im_id_int].append(array_item)
        bcelogger.info(f"The number of prediction images {len(prediction_dict)}")

        reference_list = []
        prediction_list = []
        for img_id, anno in reference_dict.items():
            # 只有同时拥有gt和预测结果才参与指标计算
            if img_id in prediction_dict:
                reference_list.extend(anno)
                prediction_list.extend(prediction_dict[img_id])
        bcelogger.info(f"The number of prediction images {len(prediction_dict)}")
        bcelogger.info(f"The number of reference images {len(reference_dict)}")

        return np.array(prediction_list), np.array(reference_list)

    def _format_result(self, metric_result: Dict):
        metric = InferenceMetric(labels=self.labels, metrics=[])

        image_metric_result = metric_result[MetricCategory.category_image.value]

        image_accuracy_list = []
        image_label_list = []
        for idx, label in self.label_ids.items():
            _image_label_results = LabelMetricResults(precision=[], recall=[], accuracy=[])
            for item in label:
                result = image_metric_result[item["index"]]
                bcelogger.info(f"The label {item} result is {result}")

                if item["parent_id"] == -1 and len(label) >= 2:
                    image_accuracy_list.append(result[0])
                elif item["parent_id"] == -1 and len(label) == 1:
                    _image_label_results.label_name = self.label_id2name[item["id"]]
                    _image_label_results.precision = result[1][0]
                    _image_label_results.recall = result[1][1]
                    _image_label_results.accuracy = result[0]
                else:
                    _image_label_results.label_name = self.label_id2name[item["parent_id"]]

                    _image_label_result = LabelMetricResult()
                    _image_label_result.label_name = self.label_inner_id2name[item["parent_id"]][item["id"]]
                    _image_label_result.result = result[1][0]
                    _image_label_results.precision.append(_image_label_result)

                    _image_label_result = LabelMetricResult()
                    _image_label_result.label_name = self.label_inner_id2name[item["parent_id"]][item["id"]]
                    _image_label_result.result = result[1][1]
                    _image_label_results.recall.append(_image_label_result)

                    _image_label_result = LabelMetricResult()
                    _image_label_result.label_name = self.label_inner_id2name[item["parent_id"]][item["id"]]
                    _image_label_result.result = result[0]
                    _image_label_results.accuracy.append(_image_label_result)

            image_label_list.append(_image_label_results)

        if len(image_label_list) > 0:
            image_label = InferenceLabelMetric()
            image_label.category = MetricCategory.category_image.value
            image_label.display_type = MetricDisplayType.table.value
            image_label.column_annotation_specs = [MetricDisplayName.precision.value,
                                                   MetricDisplayName.recall.value,
                                                   MetricDisplayName.accuracy.value]
            image_label.result = image_label_list
            metric.metrics.append(image_label)

        if len(image_accuracy_list) > 0:
            image_accuracy = InferenceSingleMetric()
            image_accuracy.name = MetricName.image_accuracy.value
            image_accuracy.display_name = MetricDisplayName.accuracy.value
            image_accuracy.category = MetricCategory.category_image.value
            image_accuracy.display_type = MetricDisplayType.card.value
            image_accuracy.result = sum(image_accuracy_list) / len(image_accuracy_list)
            metric.metrics.append(image_accuracy)

        bcelogger.info(f"The metric is {metric.dict(by_alias=True)}")

        return metric.dict(by_alias=True)

    def compute(self):
        """
        Compute metric.
        """
        results: Dict[str, Dict] = defaultdict(dict)
        for category, metric_dict in self.metric.items():
            for index, metric_list in metric_dict.items():
                result_list = []
                for metric in metric_list:
                    result_list.append(metric.compute())
                results[category].update({index: result_list})

        metric_result = self._format_result(metric_result=results)

        return metric_result

    def save(self, metric_result: Dict, output_uri: str):
        """
        Save metric.
        """
        if os.path.splitext(output_uri)[1] == "":
            output_dir = output_uri
            file_name = "metric.json"
        else:
            output_dir = os.path.dirname(output_uri)
            file_name = os.path.basename(output_uri)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        write_file(obj=metric_result, output_dir=output_dir, file_name=file_name)

    def __call__(self, predictions: List[Dict], references: List[Dict], output_uri: str):
        self.update(predictions=predictions, references=references)
        metric_result = self.compute()

        self.save(metric_result=metric_result, output_uri=output_uri)
