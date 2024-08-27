import cv2
import numpy as np
import onnxruntime as ort
import onnx
import time
import requests
import glob
import os

# 업스테이지 OCR API
api_key = "Kwiy7yvVV2Ay62RlElxbAmDJW7tzXago"

# 모델, 이미지, class_dict 경로 설정
model_path = './model/SLANet_Pub_Gen_v1_Crowd_3rd_WCE.onnx'
character_dict_path = "./data/dict/table_structure_dict_filtered.txt"


class ImagePreprocessor:
    def __init__(self, table_max_len=976):
        self.table_max_len = table_max_len
        self.padding_size = [table_max_len, table_max_len]
        self.std = [0.229, 0.224, 0.225]
        self.mean = [0.485, 0.456, 0.406]
        self.scale = 1.0 / 255.0

    def preprocess_image(self, img):
        # image_resize
        height, width = img.shape[0:2]
        ratio = self.table_max_len / (max(height, width) * 1.0)
        resize_w, resize_h = int(width * ratio), int(height * ratio)
        resized_img = cv2.resize(img, (resize_w, resize_h))

        # image_normalize
        shape = (1, 1, 3)
        mean = np.array(self.mean).reshape(shape).astype('float32')
        std = np.array(self.std).reshape(shape).astype('float32')
        normalized_img = (resized_img.astype('float32') * self.scale - mean) / std

        # image_padding
        pad_h, pad_w = self.padding_size
        padding_img = np.zeros((pad_h, pad_w, 3), dtype=np.float32)
        resized_h, resized_w = normalized_img.shape[0:2]
        padding_img[0:resized_h, 0:resized_w, :] = normalized_img.copy()

        # image_transpose
        image_array = np.transpose(padding_img, [2, 0, 1])
        image_array = np.expand_dims(image_array, axis=0)
        return image_array, height, width


class ResultPostprocessor:
    def __init__(self, character_dict_path):
        # output class 정리
        dict_list = []
        with open(character_dict_path, "rb") as fin:
            lines = fin.readlines()
            for line in lines:
                line = line.decode('utf-8').strip("\n").strip("\r\n")
                dict_list.append(line)
        if "<td></td>" not in dict_list:
            dict_list.append("<td></td>")
        if "<td>" in dict_list:
            dict_list.remove("<td>")

        # 시작, 끝 char 추가
        self.beg_str = "sos"
        self.end_str = "eos"
        self.dict_character = self.add_special_char(dict_list)

        # 글자별 idx 정리
        self.dict = {}
        for i, char in enumerate(self.dict_character):
            self.dict[char] = i

        # 문장 시작, 문장 끝 기호 저장
        self.ignored_tokens = self.get_ignored_tokens()
        self.end_idx = self.dict[self.end_str]

        self.td_token = ['<td>', '<td', '<td></td>']

    def add_special_char(self, dict_character):
        dict_character = [self.beg_str] + dict_character + [self.end_str]
        return dict_character

    def get_ignored_tokens(self):
        beg_idx = self.get_beg_end_flag_idx("beg")
        end_idx = self.get_beg_end_flag_idx("end")
        return [beg_idx, end_idx]

    def _bbox_decode(self, bbox, img_h, img_w):
        bbox[0::2] *= img_w
        bbox[1::2] *= img_h
        return bbox

    def get_beg_end_flag_idx(self, beg_or_end):
        if beg_or_end == "beg":
            idx = np.array(self.dict[self.beg_str])
        elif beg_or_end == "end":
            idx = np.array(self.dict[self.end_str])
        else:
            assert False, "unsupport type %s in get_beg_end_flag_idx" % beg_or_end
        return idx

    def postprocess_result(self, outputs, img_h, img_w):
        # 모델 추론 결과 -> 텍스트 결과
        preds = {}
        preds['structure_probs'] = outputs[1]
        preds['loc_preds'] = outputs[0]

        structure_probs = preds['structure_probs'][0]
        bbox_preds = preds['loc_preds'][0]

        structure_idx = structure_probs.argmax(axis=1)
        structure_probs = structure_probs.max(axis=1)

        # 결과 정리
        structure_list = []
        bbox_list = []
        score_list = []
        for idx in range(len(structure_idx)):
            char_idx = int(structure_idx[idx])
            if idx > 0 and char_idx == self.end_idx:
                break
            if char_idx in self.ignored_tokens:
                continue
            text = self.dict_character[char_idx]
            # <td>가 나오면 bbox를 bbox_list에 추가
            if text in self.td_token:
                bbox = bbox_preds[idx]
                bbox = self._bbox_decode(bbox, img_h, img_w)
                bbox_list.append(bbox)
            structure_list.append(text)
            score_list.append(structure_probs[idx])

        # html 결과 정리
        structure_list = [
                             '<html>', '<body>', '<table>'
                         ] + structure_list + ['</table>', '</body>', '</html>']

        return structure_list, bbox_list, score_list


class ONNXModelHandler:
    def __init__(self, model_path):
        self.model_path = model_path
        self.session = self.load_model()

    def load_model(self):
        model = onnx.load(self.model_path)
        onnx.checker.check_model(model)
        return ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])

    def run_model(self, input_data):
        return self.session.run(None, {self.session.get_inputs()[0].name: input_data})


class TextTableMapping:
    def __call__(self, structure_list, bbox_list, dt_boxes, rec_res):
        pred_structures, pred_bboxes = structure_list, bbox_list
        # pred_bboxes(테이블 셀 박스)에 dt_boxes(텍스트 검출 결과) 매핑
        matched_index = self.match_result(dt_boxes if dt_boxes else [], pred_bboxes)
        # 매핑된 결과를 기준으로 최종 결과 출력
        cells = [''] * len(bbox_list)
        pred_html, pred, cell_result = self.get_pred_html(pred_structures, matched_index, rec_res, cells)
        return pred_html, cell_result

    def match_result(self, dt_boxes, pred_bboxes):
        matched = {}
        if dt_boxes is None:
            return matched
        elif pred_bboxes is None:
            return matched

        # 각 dt_box에 대해 수행
        for i, gt_box in enumerate(dt_boxes):
            min_inv_iou = float('inf')
            candidates = []  # 최소 inv_iou 값과 일치하는 pred_boxes의 인덱스를 저장

            for j, pred_box in enumerate(pred_bboxes):
                if len(pred_box) == 8:
                    pred_box = [
                        np.min(pred_box[0::2]), np.min(pred_box[1::2]),
                        np.max(pred_box[0::2]), np.max(pred_box[1::2])
                    ]
                iou = self.compute_iou(gt_box, pred_box)
                inv_iou = 1 - iou

                # 최소 inv_iou를 찾는다
                if inv_iou < min_inv_iou:
                    min_inv_iou = inv_iou
                    candidates = [j]  # 새로운 최소값이 나타나면 이전 후보를 삭제하고 업데이트
                elif inv_iou == min_inv_iou:
                    candidates.append(j)  # 같은 최소값을 가지는 후보 추가

            # 후보 중에서 거리를 기준으로 최종 선택
            min_distance = float('inf')
            min_index = None
            for index in candidates:
                distance = self.distance(gt_box, pred_bboxes[index])
                if distance < min_distance:
                    min_distance = distance
                    min_index = index

            # 결과 매칭 업데이트
            if min_index is not None:
                if min_index in matched:
                    matched[min_index].append(i)
                else:
                    matched[min_index] = [i]
        return matched

    def get_pred_html(self, pred_structures, matched_index, ocr_contents, cells):
        end_html = []
        td_index = 0
        # pred_structures 내 tag들을 하나씩 확인
        for tag in pred_structures:
            # tag가 <td> 일 때
            if '</td>' in tag:
                if '<td></td>' == tag:
                    end_html.extend('<td>')
                # 테이블 셀 하나씩 차례대로, 매핑된 텍스트 박스의 텍스트를 가져옴 
                if td_index in matched_index.keys():
                    for i, td_index_index in enumerate(matched_index[td_index]):
                        content = ocr_contents[td_index_index]

                        if len(matched_index[td_index]) > 1:
                            if len(content) == 0:
                                continue
                            if content[0] == ' ':
                                content = content[1:]
                            # 테이블 셀의 마지막 글자가 아니라면 띄어쓰기 추가
                            if i != len(matched_index[
                                            td_index]) - 1 and ' ' != content[-1]:
                                content += ' '
                        cells[td_index] += content

                        end_html.extend(content)
                if '<td></td>' == tag:
                    end_html.append('</td>')
                else:
                    end_html.append(tag)
                td_index += 1
            else:
                end_html.append(tag)
        return ''.join(end_html), end_html, cells

    def distance(self, box_1, box_2):
        x1, y1, x2, y2 = box_1
        x3, y3, x4, y4 = box_2
        dis = abs(x3 - x1) + abs(y3 - y1) + abs(x4 - x2) + abs(y4 - y2)
        dis_2 = abs(x3 - x1) + abs(y3 - y1)
        dis_3 = abs(x4 - x2) + abs(y4 - y2)
        return dis + min(dis_2, dis_3)

    def compute_iou(self, rec1, rec2):
        """
        computing IoU
        :param rec1: (y0, x0, y1, x1), which reflects
                (top, left, bottom, right)
        :param rec2: (y0, x0, y1, x1)
        :return: scala value of IoU
        """
        # computing area of each rectangles
        S_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
        S_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

        # computing the sum_area
        sum_area = S_rec1 + S_rec2

        # find the each edge of intersect rectangle
        left_line = max(rec1[1], rec2[1])
        right_line = min(rec1[3], rec2[3])
        top_line = max(rec1[0], rec2[0])
        bottom_line = min(rec1[2], rec2[2])

        # judge if there is an intersect
        if left_line >= right_line or top_line >= bottom_line:
            return 0.0
        else:
            intersect = (right_line - left_line) * (bottom_line - top_line)
            return (intersect / (sum_area - intersect)) * 1.0


def ocr_image_upstage(file_name, image_file, url, max_retries=10):
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"image": (file_name, image_file)}

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, files=files)
            ocr_response = response.json()

            # 'pages' 키가 있는지 확인
            if 'pages' in ocr_response:
                print("[Upstage] Upstage API requests success,", "Attempt:", attempt + 1)
                ocr_result = ocr_response['pages'][0]['words']

                dt_boxes = []
                rec_res = []
                for item in ocr_result:
                    vertices = item['boundingBox']['vertices']
                    coords = (vertices[0]['x'], vertices[0]['y'], vertices[2]['x'], vertices[2]['y'])
                    confidence_score = round(item['confidence'], 2)
                    text = item['text']

                    dt_boxes.append(coords)
                    rec_res.append((text, confidence_score))
                return dt_boxes, rec_res
            else:
                print("[Upstage] Upstage API requests error:", ocr_response, "Attempt:", attempt + 1)

        except Exception as e:
            print("[Upstage] Upstage API Exception:", e)

    print("[Upstage] Upstage API Exception:", e)
    return None, None
