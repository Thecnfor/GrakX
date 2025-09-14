"""
此模块实现了验证码识别的功能，封装了验证码的预处理、识别和后处理逻辑。
支持从文件路径或字节流中识别验证码，可配置调试模式和多种预处理方法。
增加了多进程优化，支持批量并行识别，提高性能。
"""
import os
import re
import cv2
import numpy as np
from PIL import Image
from multiprocessing import Pool, cpu_count

# 使用多种方法尝试禁用ONNX Runtime警告日志
os.environ['ORT_LOGGING_LEVEL'] = '3'  # 3表示ERROR级别，不显示WARNING
try:
    import onnxruntime as ort
    ort.set_default_logger_severity(3)
except ImportError:
    pass

# 解决PIL.Image.ANTIALIAS兼容性问题
try:
    if hasattr(Image, 'Resampling') and hasattr(Image.Resampling, 'LANCZOS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    try:
        from PIL import ImageResampling
        if hasattr(ImageResampling, 'LANCZOS'):
            Image.ANTIALIAS = ImageResampling.LANCZOS
    except (ImportError, AttributeError):
        Image.ANTIALIAS = 1

# 尝试导入ddddocr库
ocr_available = False
try:
    import ddddocr
    ocr_available = True
except ImportError:
    print("请安装ddddocr库: pip install ddddocr")


class CaptchaRecognizer:
    """验证码识别器类，封装验证码识别的所有功能"""

    def __init__(self, debug=False):
        self.debug = debug
        self.ocr = None
        if ocr_available:
            try:
                # 优先使用show_ad=False参数来禁用广告输出
                self.ocr = ddddocr.DdddOcr(show_ad=False)
            except (TypeError, ValueError):
                # 对于不支持show_ad参数的旧版本，回退到默认初始化
                self.ocr = ddddocr.DdddOcr()
        else:
            print("ddddocr库不可用，无法进行验证码识别")

    def preprocess(self, img_path, method=1):
        try:
            img = cv2.imread(img_path)
            if img is None:
                raise Exception("无法读取图片")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if method == 1:
                thresh = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    15, 10
                )
                kernel_small = cv2.getStructuringElement(
                    cv2.MORPH_RECT, (1, 1))
                result = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_small)

            elif method == 2:
                thresh = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    15, 10
                )
                result = thresh

            else:
                thresh = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    15, 10
                )
                kernel_small = cv2.getStructuringElement(
                    cv2.MORPH_RECT, (2, 2))
                open_img = cv2.morphologyEx(
                    thresh, cv2.MORPH_OPEN, kernel_small)

                kernel_line = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
                closed_img = cv2.morphologyEx(
                    open_img, cv2.MORPH_CLOSE, kernel_line)

                median_blur = cv2.medianBlur(closed_img, 3)
                kernel_sharpen = np.array(
                    [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]
                )
                sharpened = cv2.filter2D(median_blur, -1, kernel_sharpen)

                result = sharpened

            if self.debug:
                os.makedirs("./tmp", exist_ok=True)
                cv2.imwrite(f"./tmp/preprocessed_method{method}.png", result)

            return result
        except Exception as e:
            print(f"图片预处理失败: {e}")
            return None

    def postprocess_result(self, result, preserve_case=False):
        if not result:
            return ""
        clean_result = re.sub(r'[^a-zA-Z0-9]', '', result)
        return clean_result if preserve_case else clean_result

    def recognize(self, img_path=None, max_attempts=2):
        if img_path is None:
            img_path = "./test/captcha.jpg"

        if not os.path.exists(img_path):
            print(f"图片文件不存在: {img_path}")
            return ""

        attempts = 0
        while attempts < max_attempts:
            try:
                attempts += 1
                for method in [2, 1]:
                    clean_img = self.preprocess(img_path, method)
                    if clean_img is None:
                        continue
                    _, img_encoded = cv2.imencode('.png', clean_img)
                    img_bytes = img_encoded.tobytes()
                    res = self.ocr.classification(img_bytes)
                    processed_result = self.postprocess_result(
                        res, preserve_case=True)
                    if processed_result and len(processed_result) == 4:
                        if self.debug:
                            print(f"方法{method}识别结果: {processed_result}")
                        return processed_result

                with open(img_path, "rb") as f:
                    original_bytes = f.read()
                res_original = self.ocr.classification(original_bytes)
                processed_original = self.postprocess_result(
                    res_original, preserve_case=True
                )
                if processed_original and len(processed_original) == 4:
                    if self.debug:
                        print(f"原图识别结果: {processed_original}")
                    return processed_original

            except Exception as e:
                if self.debug:
                    print(f"OCR识别失败 (尝试 {attempts}/{max_attempts}): {e}")
                if attempts < max_attempts:
                    continue
                return ""

        print(f"达到最大尝试次数({max_attempts})，识别失败")
        return ""


# 多进程封装
def _worker_recognize(img_path):
    worker = CaptchaRecognizer(debug=False)
    return worker.recognize(img_path)


class CaptchaRecognizerPool:
    """基于进程池的验证码识别器"""

    def __init__(self, processes=None):
        self.processes = processes or max(1, cpu_count() - 1)
        self.pool = Pool(processes=self.processes)

    def recognize_batch(self, img_paths):
        """批量并行识别验证码"""
        results = self.pool.map(_worker_recognize, img_paths)
        return results

    def close(self):
        self.pool.close()
        self.pool.join()


# 创建全局识别器实例
captcha_recognizer = CaptchaRecognizer(debug=False)


def verify_code(img_path=None, img_bytes=None):
    if img_bytes is not None:
        try:
            res = captcha_recognizer.ocr.classification(img_bytes)
            processed_result = captcha_recognizer.postprocess_result(
                res, preserve_case=True
            )
            return processed_result
        except Exception as e:
            print(f"直接识别字节流失败: {e}")
            return ""
    return captcha_recognizer.recognize(img_path)
