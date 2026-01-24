"""
图像识别模块 - 支持模板匹配和特征匹配
"""

import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional, Any
import json


logger = logging.getLogger(__name__)

class ImageRecognizer:
    """图像识别 - 基于模板匹配"""

    MATCH_METHODS = {
        'TM_CCOEFF': cv2.TM_CCOEFF,
        'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
        'TM_CCORR': cv2.TM_CCORR,
        'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
        'TM_SQDIFF': cv2.TM_SQDIFF,
        'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED
    }

    def __init__(self, template_dir:str = "images/templates",
                 threshold:float = 0.8,
                 match_method:str = 'TM_CCOEFF_NORMED'
                 ):
        """
        初始化图像识别器

        Args:
            template_dir: 模板图像目录
            threshold: 匹配阈值（0-1）
            match_method: 匹配方法
        """
        self.template_dir = Path(template_dir)
        self.threshold = threshold
        self.match_method = self.MATCH_METHODS.get(match_method, cv2.TM_CCOEFF_NORMED)

        #加载模块
        self.templates = self._load_templates()

        logger.info(f"ImageRecognizer初始化完成 - 模板数：{len(self.templates)},阈值：{threshold}")

    def _load_templates(self) -> Dict[str,Dict[str,Any]]:
        """
        从目录加载所有模板

        Returns:
            Dict: 模板字典 {name: {image: ndarray, path: str}}
        """
        templates = {}

        if not self.template_dir.exists():
            logger.warning(f"模板目录不存在：{self.template_dir}")
            self.template_dir.mkdir(parents=True, exist_ok=True)
            return templates

        #支持的图像格式
        image_extensions = ('.png','.jpg','jpeg','.bmp','.tiff')

        for img_file in self.template_dir.glob('*'):
            if img_file.suffix.lower() in image_extensions:
                template_name = img_file.stem
                template_img = cv2.imread(str(img_file))

                if template_img is not None:
                    templates[template_name] = {
                        'image':template_img,
                        'path':str(img_file),
                        'size':template_img.shape[:2] #(height,width)
                    }
                else :
                    logger.warning(f"无法加载模块：{img_file}")

        logger.info(f"共加载{len(templates)}个模块")
        return templates

    def add_template(self,name:str,image:np.ndarray,
                     save:bool = True) -> bool :
        """
        添加模板

        Args:
            name: 模板名称
            image: 模板图像
            save: 是否保存到文件

        Returns:
            bool: 是否成功
        """
        if image is None or image.size == 0:
            logger.error("模块图像为空")
            return False

        #添加到内存
        self.templates[name] = {
            'image':image,
            'path':str(self.template_dir / f"{name}.png"),
            'size':image.shape[:2]
        }

        if save:
            self.save_template(name,image)

        logger.info(f"添加模块：{name} - {image.shape}")
        return True

    def save_template(self,name:str,image:np.ndarray = None) -> bool:
        """
        保存模板到文件

        Args:
            name: 模板名称
            image: 模板图像，None则使用内存中的

        Returns:
            bool: 是否成功
        """
        try:
            if image is None:
                if name not in self.templates:
                    logger.error(f"模块不存在{name}")
                    return False
                image = self.templates[name]['image']

            #确保目录存在
            self.template_dir.mkdir(parents=True, exist_ok=True)

            #保存图像
            filepath = self.template_dir / f"{name}.png"
            success = cv2.imwrite(str(filepath), image)

            if success:
                logger.info(f"模块保存成功:{filepath}")
                if name in self.templates:
                    self.templates[name]['path'] = str(filepath)
                return True
            else:
                logger.error(f"模块保存失败：{filepath}")
                return False

        except Exception as e:
            logger.error(f"保存模块出错:{e}")
            return False

    def remove_template(self,name:str,delete_file:bool=False) -> bool:
        """
        移除模板

        Args:
            name: 模板名称
            delete_file: 是否删除文件

        Returns:
            bool: 是否成功
        """

        if name not in self.templates:
            logger.warning(f"模块不存在：{name}")
            return False

        #删除文件
        if delete_file:
            try:
                filepath = Path(self.templates[name]['path'])
                if filepath.exists():
                    filepath.unlink()
                    logger.info(f"删除模板文件：{filepath}")
            except Exception as e:
                logger.error(f"删除模块文件失败：{e}")

        #从内存移除
        del self.templates[name]
        logger.info(f"移除模块：{name}")
        return True

    def find_template(self,template_name:str,screen_image:np.ndarray,
                      threshold:float = None, method:int= None)->Optional[Dict]:
        """
        在屏幕图像中查找模板

        Args:
            template_name: 模板名称
            screen_image: 屏幕图像
            threshold: 匹配阈值，None使用默认值
            method: 匹配方法，None使用默认值

        Returns:
            Dict: 匹配结果，None表示未找到
        """
        if template_name not in self.templates:
            logger.warning(f"模块不存在：{template_name}")
            return None

        template = self.templates[template_name]['image']
        thresh = threshold if threshold is not None else self.threshold
        meth = method if method is not None else self.match_method

        #执行模块匹配
        result = cv2.matchTemplate(screen_image,template,meth)

        if meth in [cv2.TM_SQDIFF,cv2.TM_SQDIFF_NORMED]:
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
            match_val = 1 - min_val if meth == cv2.TM_SQDIFF_NORMED else -min_val
            location = min_loc
        else:
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
            match_val = max_val
            location = max_loc


        #检查是否达到阈值
        if match_val >= thresh:
            h,w=template.shape[:2]
            top_left = location
            bottom_right = (top_left[0] + w, top_left[1] + h)
            center = (top_left[0] + w//2,top_left[1] + h//2)

            match_result = {
                'found':True,
                'template':template_name,
                'confidence':float(match_val),
                'location':top_left,
                'center':center,
                'size':(w,h),
                'bounding_box':(top_left,bottom_right)
            }

            logger.debug(f"找到模块{template_name}:置信度={match_val:.3f},位置={center}")
            return match_result
        else:
            logger.debug(f"为找到模块{template_name}:最高置信度={match_val:.3f}")
            return None

    def find_all_templates(self,screen_image:np.ndarray,
                           threshold: float = None) -> Dict[str,Optional[Dict]] :
        """
        查找所有模板

        Args:
            screen_image: 屏幕图像
            threshold: 匹配阈值

        Returns:
            Dict: 所有模板的查找结果
        """
        results = {}

        for template_name in self.templates:
            result = self.find_template(template_name, screen_image,threshold)
            results[template_name] = result

        return results

    def capture_and_add_template(self,name:str,region:Tuple = None,
                                 from_capturer = None) -> bool:
        """
        从屏幕捕获并添加为模板

        Args:
            name: 模板名称
            region: 捕获区域 (x, y, width, height)
            from_capturer: 屏幕捕获器实例

        Returns:
            bool: 是否成功
        """
        try:
            if from_capturer is None:
                #创建临时捕获器
                from src.core.capture import ScreenCapture
                capturer = ScreenCapture(region = region)
                template_img = capturer.capture()
            else:
                #使用提供的捕获器
                if region:
                    from_capturer.region = region
                template_img = from_capturer.capture()

            if template_img is None:
                logger.error("捕获模块图像失败")
                return False

            return self.add_template(name,template_img)
        except Exception as e:
            logger.error(f"捕获并添加模块失败：{e}")
            return False

    def visualize_match(self,screen_image:np.ndarray,
                        match_result:Dict,window_name:str = "普配结果") -> None:
        """
        可视化匹配结果

        Args:
            screen_image: 屏幕图像
            match_result: 匹配结果
            window_name: 窗口名称
        """
        if match_result is None or not match_result['found']:
            logger.warning("没有匹配结果可显示")
            return

        #复制图像用于绘制
        display_img = screen_image.copy()

        #获取匹配信息
        top_left = match_result['location']
        bottom_right = match_result['bounding_box'][1]
        center = match_result['center']
        confidence = match_result['confidence']

        #绘制矩形框
        cv2.rectangle(display_img,top_left,bottom_right,(0,255,0),2)

        #绘制中心点
        cv2.circle(display_img,center,5,(0,0,255),-1)

        #添加文本
        text = f"{match_result['template']}：{confidence:.3f}"
        cv2.putText(display_img,text,(top_left[0],top_left[1] -10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

        #显示图像
        cv2.imshow(window_name,display_img)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

class FeatureMatcher:
    """特征匹配器 - 基于特征点匹配，适合有变化的图像"""

    def __int__(self,nfeatures:int = 1000):
        """
        初始化特征匹配器

        Args:
            nfeatures: 提取的特征点数量
        """
        self.orb = cv2.ORB_create(nfeatures=nfeatures)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
        self.features_cache = {}#缓存特征

        logger.info(f"FeatureMatcher初始化完成 - 特征点数：{nfeatures}")

    def extract_features(self,image:np.ndarray)->Tuple[List,np.ndarray]:
        """
        提取图像特征

        Args:
            image: 输入图像

        Returns:
            Tuple: (关键点, 特征描述符)
        """
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        keypoints , descriptors = self.orb.detectAndCompute(gray,None)
        return keypoints, descriptors

    def match_images(self,img1:np.ndarray,img2:np.ndarray,
                     min_matches:int =10) -> Optional[Dict]:
        """
        匹配两个图像

        Args:
            img1: 图像1（模板）
            img2: 图像2（屏幕）
            min_matches: 最小匹配数量

        Returns:
            Dict: 匹配结果，None表示匹配失败
        """

        #提取特征
        kp1,desc1 = self.extract_features(img1)
        kp2,desc2 = self.extract_features(img2)

        if desc1 is None or desc2 is None:
            logger.warning("无法提取特征描述符")
            return None

        #特征匹配
        matches = self.matcher.match(desc1,desc2)
        matches = sorted(matches,key=lambda x:x.distance)

        if len(matches) < min_matches:
            logger.debug(f"匹配点不足：{len(matches)}<{min_matches}")
            return None

        #计算匹配信息
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

        #计算单应性矩阵
        if len(matches) >= 4:
            M,mask = cv2.findHomography(src_pts,dst_pts,cv2.RANSAC,5.0)
            if M is None:
                #计算模板在屏幕中的位置
                h, w = img1.shape[:2]
                pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)

                #计算中心点
                center_x = int(np.mean(dst[:,0,0]))
                center_y = int(np.mean(dst[:,0,1]))

                result = {
                    'found' : True,
                    'matches': len(matches),
                    'good_matches': len([m for m in matches if m.distance < 50]),
                    'avg_distance': np.mean([m.distance for m in matches[:min_matches]]),
                    'center': (center_x, center_y),
                    'corners': dst.astype(int)
                }

                logger.debug(f"特征匹配失败，无法计算位置")
                return None

if __name__ == "__main__":
    #配置日志
    logging.basicCofig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print("测试图像识别模块...")
    print("1. 测试模板匹配")
    print("2. 测试特征匹配")
    print("3. 添加新模板")

    choice = input("请选择测试项目 (1-3): ").strip()

    if choice == "1":
        print("模板匹配测试...")
        print("请确保在 images/templates 目录下有模板图像")

        # 创建识别器
        recognizer = ImageRecognizer()

        if not recognizer.templates:
            print("没有找到模板，请先添加模板（选择选项3）")
        else:
            print(f"找到 {len(recognizer.templates)} 个模板:")
            for name in recognizer.templates.keys():
                print(f"  - {name}")

            # 截取当前屏幕
            from src.core.capture import ScreenCapturer

            capturer = ScreenCapturer()
            screen = capturer.capture()

            if screen is not None:
                # 测试查找所有模板
                results = recognizer.find_all_templates(screen)

                found_count = sum(1 for r in results.values() if r is not None)
                print(f"\n匹配结果: 找到 {found_count}/{len(results)} 个模板")

                # 显示找到的模板
                for name, result in results.items():
                    if result:
                        print(f"  ✓ {name}: 置信度={result['confidence']:.3f}, 位置={result['center']}")
                        # 可视化显示
                        recognizer.visualize_match(screen, result)
                    else:
                        print(f"  ✗ {name}: 未找到")
            else:
                print("截图失败")

    elif choice == "2":
        print("特征匹配测试...")
        print("需要两张图像进行匹配测试")

        # 这里需要实际的图像文件，暂时跳过
        print("特征匹配测试需要实际图像，将在实际使用时测试")

    elif choice == "3":
        print("添加新模板...")
        recognizer = ImageRecognizer()

        template_name = input("请输入模板名称: ").strip()
        if not template_name:
            print("模板名称不能为空")
        else:
            print(f"将捕获屏幕区域作为模板: {template_name}")
            print("请将要捕获的图像显示在屏幕上，然后按回车继续...")
            input()

            # 让用户选择区域
            print("请输入捕获区域（格式: x,y,宽度,高度），直接回车为全屏: ")
            region_input = input().strip()

            region = None
            if region_input:
                try:
                    x, y, w, h = map(int, region_input.split(','))
                    region = (x, y, w, h)
                except:
                    print("格式错误，使用全屏")

            # 捕获并添加模板
            success = recognizer.capture_and_add_template(template_name, region)
            if success:
                print(f"✓ 模板 '{template_name}' 添加成功！")
            else:
                print("✗ 模板添加失败")

    else:
        print("无效选择")





