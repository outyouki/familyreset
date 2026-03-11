"""
画像認識モジュール - サポートテンプレートマッチと特徴マッチ
"""

import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional, Any
import json


logger = logging.getLogger(__name__)

class ImageRecognizer:
    """画像認識 - 基テキスト于テンプレートマッチ"""

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
        画像認識器を初期化

        Args:
            template_dir: テンプレート画像ディレクトリ
            threshold: マッチ閾値（0-1）
            match_method: マッチメソッド
        """
        self.template_dir = Path(template_dir)
        self.threshold = threshold
        self.match_method = self.MATCH_METHODS.get(match_method, cv2.TM_CCOEFF_NORMED)

        #読み込みみみモジュール
        self.templates = self._load_templates()

        logger.info(f"ImageRecognizer初期化完了した - テンプレート関数：{len(self.templates)},閾値：{threshold}")

    def _load_templates(self) -> Dict[str,Dict[str,Any]]:
        """
        からディレクトリ読み込みみみすべてテンプレート

        Returns:
            Dict: テンプレート辞書 {name: {image: ndarray, path: str}}
        """
        templates = {}

        if not self.template_dir.exists():
            logger.warning(f"テンプレートディレクトリ非保存に：{self.template_dir}")
            self.template_dir.mkdir(parents=True, exist_ok=True)
            return templates

        #サポート画像フォーマット
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
                    logger.warning(f"読み込みみめませんみ込みみみモジュール：{img_file}")

        logger.info(f"結合計読み込みみみみ込みみみ{len(templates)}つのモジュール")
        return templates

    def add_template(self,name:str,image:np.ndarray,
                     save:bool = True) -> bool :
        """
        追加テンプレート

        Args:
            name: テンプレート名前
            image: テンプレート画像
            save: かどうか保存へファイル

        Returns:
            bool: 成功したか
        """
        if image is None or image.size == 0:
            logger.error("モジュール画像にクリア")
            return False

        #追加へメモリ
        self.templates[name] = {
            'image':image,
            'path':str(self.template_dir / f"{name}.png"),
            'size':image.shape[:2]
        }

        if save:
            self.save_template(name,image)

        logger.info(f"追加モジュール：{name} - {image.shape}")
        return True

    def save_template(self,name:str,image:np.ndarray = None) -> bool:
        """
        保存テンプレートへファイル

        Args:
            name: テンプレート名前
            image: テンプレート画像、Noneはメモリ内のものを使用

        Returns:
            bool: 成功したか
        """
        try:
            if image is None:
                if name not in self.templates:
                    logger.error(f"モジュール非保存に{name}")
                    return False
                image = self.templates[name]['image']

            #正しいディレクトリ保存に
            self.template_dir.mkdir(parents=True, exist_ok=True)

            #保存画像
            filepath = self.template_dir / f"{name}.png"
            success = cv2.imwrite(str(filepath), image)

            if success:
                logger.info(f"モジュール保存に成功:{filepath}")
                if name in self.templates:
                    self.templates[name]['path'] = str(filepath)
                return True
            else:
                logger.error(f"モジュール保存に失敗：{filepath}")
                return False

        except Exception as e:
            logger.error(f"保存モジュールエラーが発生成:{e}")
            return False

    def remove_template(self,name:str,delete_file:bool=False) -> bool:
        """
        削除テンプレート

        Args:
            name: テンプレート名前
            delete_file: かどうかファイルを削除

        Returns:
            bool: 成功したか
        """

        if name not in self.templates:
            logger.warning(f"モジュール非保存に：{name}")
            return False

        #ファイルを削除
        if delete_file:
            try:
                filepath = Path(self.templates[name]['path'])
                if filepath.exists():
                    filepath.unlink()
                    logger.info(f"削除テンプレートファイル：{filepath}")
            except Exception as e:
                logger.error(f"削除テンプレートファイル失敗：{e}")

        #メモリから削除
        del self.templates[name]
        logger.info(f"削除モジュール：{name}")
        return True

    def find_template(self,template_name:str,screen_image:np.ndarray,
                      threshold:float = None, method:int= None)->Optional[Dict]:
        """
        にスクリーン画像内をテンプレートを検索

        Args:
            template_name: テンプレート名前
            screen_image: スクリーン画像
            threshold: マッチ閾値、None使用デフォルト値
            method: マッチメソッド、None使用デフォルト値

        Returns:
            Dict: マッチ結果、None見つからないことを
        """
        if template_name not in self.templates:
            logger.warning(f"モジュール非保存に：{template_name}")
            return None

        template = self.templates[template_name]['image']
        thresh = threshold if threshold is not None else self.threshold
        meth = method if method is not None else self.match_method

        #実行モジュールマッチ
        result = cv2.matchTemplate(screen_image,template,meth)

        if meth in [cv2.TM_SQDIFF,cv2.TM_SQDIFF_NORMED]:
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
            match_val = 1 - min_val if meth == cv2.TM_SQDIFF_NORMED else -min_val
            location = min_loc
        else:
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
            match_val = max_val
            location = max_loc


        #チェックかどうか達するへ閾値
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

            logger.debug(f"見つけたモジュール{template_name}:信頼度={match_val:.3f},位置={center}")
            return match_result
        else:
            logger.debug(f"に見つけたモジュール{template_name}:最高信頼度={match_val:.3f}")
            return None

    def find_all_templates(self,screen_image:np.ndarray,
                           threshold: float = None) -> Dict[str,Optional[Dict]] :
        """
        検索すべてテンプレート

        Args:
            screen_image: スクリーン画像
            threshold: マッチ閾値

        Returns:
            Dict: すべてテンプレート検索結果
        """
        results = {}

        for template_name in self.templates:
            result = self.find_template(template_name, screen_image,threshold)
            results[template_name] = result

        return results

    def capture_and_add_template(self,name:str,region:Tuple = None,
                                 from_capturer = None) -> bool:
        """
        からスクリーンキャプチャ、そして追加にテンプレート

        Args:
            name: テンプレート名前
            region: キャプチャ領域 (x, y, width, height)
            from_capturer: スクリーンキャプチャ器インスタンス

        Returns:
            bool: 成功したか
        """
        try:
            if from_capturer is None:
                #一時的なものを作成成キャプチャ器
                from src.core.capture import ScreenCapture
                capturer = ScreenCapture(region = region)
                template_img = capturer.capture()
            else:
                # 提供されたキャプチャ器を使用
                if region:
                    from_capturer.region = region
                template_img = from_capturer.capture()

            if template_img is None:
                logger.error("キャプチャモジュール画像の取得に失敗")
                return False

            return self.add_template(name,template_img)
        except Exception as e:
            logger.error(f"キャプチャ、そして追加モジュール失敗：{e}")
            return False

    def visualize_match(self,screen_image:np.ndarray,
                        match_result:Dict,window_name:str = "マッチング結果") -> None:
        """
        認可视フォーマットマッチ結果

        Args:
            screen_image: スクリーン画像
            match_result: マッチ結果
            window_name: ウィンドウ名前
        """
        if match_result is None or not match_result['found']:
            logger.warning("没既存マッチ結果認可リストデモ")
            return

        # 画像を表示ウィンドウに使用
        display_img = screen_image.copy()

        #取得マッチ情報
        top_left = match_result['location']
        bottom_right = match_result['bounding_box'][1]
        center = match_result['center']
        confidence = match_result['confidence']

        #矩形を描描画画像画像
        cv2.rectangle(display_img,top_left,bottom_right,(0,255,0),2)

        #中心ノードを描描画画像画像
        cv2.circle(display_img,center,5,(0,0,255),-1)

        #追加テキスト
        text = f"{match_result['template']}：{confidence:.3f}"
        cv2.putText(display_img,text,(top_left[0],top_left[1] -10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

        #テーブル画像をリストデモ
        cv2.imshow(window_name,display_img)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

class FeatureMatcher:
    """特徴マッチ器 - 特徴ノードに基テキストづくマッチ、変フォーマットのある画像に適している"""

    def __int__(self,nfeatures:int = 1000):
        """
        特徴を初期化マッチ器

        Args:
            nfeatures: 特徴ノードの抽エクスポート関数
        """
        self.orb = cv2.ORB_create(nfeatures=nfeatures)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
        self.features_cache = {}#キャッシュ特徴

        logger.info(f"FeatureMatcher初期化完了した - 特徴ノードの関数：{nfeatures}")

    def extract_features(self,image:np.ndarray)->Tuple[List,np.ndarray]:
        """
        画像特徴の抽エクスポート

        Args:
            image: 入力画像

        Returns:
            Tuple: (についてキーノード, 特徴記明子)
        """
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        keypoints , descriptors = self.orb.detectAndCompute(gray,None)
        return keypoints, descriptors

    def match_images(self,img1:np.ndarray,img2:np.ndarray,
                     min_matches:int =10) -> Optional[Dict]:
        """
        マッチ2つの画像

        Args:
            img1: 画像1（テンプレート）
            img2: 画像2（スクリーン）
            min_matches: 最小マッチ関数数量

        Returns:
            Dict: マッチ結果、Noneリストデモマッチ失敗
        """

        #抽エクスポート特徴
        kp1,desc1 = self.extract_features(img1)
        kp2,desc2 = self.extract_features(img2)

        if desc1 is None or desc2 is None:
            logger.warning("特徴記明子を抽エクスポートできません")
            return None

        #特徴マッチ
        matches = self.matcher.match(desc1,desc2)
        matches = sorted(matches,key=lambda x:x.distance)

        if len(matches) < min_matches:
            logger.debug(f"マッチポイントが非足：{len(matches)}<{min_matches}")
            return None

        #計算マッチ情報
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

        #単マッピング特徴性シリアル列を計算
        if len(matches) >= 4:
            M,mask = cv2.findHomography(src_pts,dst_pts,cv2.RANSAC,5.0)
            if M is None:
                #計算テンプレートにスクリーン中の位置
                h, w = img1.shape[:2]
                pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)

                #中心ノードを計算
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

                logger.debug(f"特徴マッチ失敗、位置を計算できません")
                return None

if __name__ == "__main__":
    #ログ設定
    logging.basicCofig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print("テスト画像認識モジュール...")
    print("1. テストテンプレートマッチ")
    print("2. テスト特徴マッチ")
    print("3. 追加新テンプレート")

    choice = input("ください選択テスト項目 (1-3): ").strip()

    if choice == "1":
        print("テンプレートマッチテスト...")
        print("確認してくださいに images/templates ディレクトリ以下にありますテンプレート画像")

        # 認識器を作成成
        recognizer = ImageRecognizer()

        if not recognizer.templates:
            print("見つかつかりませんでしたへテンプレート、最初に追加してくださいテンプレート（選択オプション3）")
        else:
            print(f"見つけた {len(recognizer.templates)} つのテンプレート:")
            for name in recognizer.templates.keys():
                print(f"  - {name}")

            # キャプチャ現在スクリーン
            from src.core.capture import ScreenCapturer

            capturer = ScreenCapturer()
            screen = capturer.capture()

            if screen is not None:
                # テスト検索すべてテンプレート
                results = recognizer.find_all_templates(screen)

                found_count = sum(1 for r in results.values() if r is not None)
                print(f"\nマッチ結果: 見つけた {found_count}/{len(results)} つのテンプレート")

                # テーブル見つかつかったものをテンプレート
                for name, result in results.items():
                    if result:
                        print(f"  ✓ {name}: 信頼度={result['confidence']:.3f}, 位置={result['center']}")
                        # 認可视フォーマットリストデモ
                        recognizer.visualize_match(screen, result)
                    else:
                        print(f"  ✗ {name}: 未見つけた")
            else:
                print("スクリーンショット失敗")

    elif choice == "2":
        print("特徴マッチテスト...")
        print("2枚の画像が必要うマッチテスト")

        # 実際の画像が必要ですファイル、一時的スキップ
        print("特徴マッチテスト実際の画像が必要、〜をに実際のを使用時テスト")

    elif choice == "3":
        print("追加新テンプレート...")
        recognizer = ImageRecognizer()

        template_name = input("ください入力テンプレート名前: ").strip()
        if not template_name:
            print("テンプレート名前をクリアにすることはできませんにクリア")
        else:
            print(f"〜をキャプチャスクリーン領域を作成成にテンプレート: {template_name}")
            print("くださいする予定キャプチャ画像リストデモにスクリーン上、そのその後Enterキーを押して継続...")
            input()

            # ユーザーが領域を選択してください
            print("ください入力キャプチャ領域（フォーマット: x,y,幅,高さささ）、直接続Enterキーを押すに全画面: ")
            region_input = input().strip()

            region = None
            if region_input:
                try:
                    x, y, w, h = map(int, region_input.split(','))
                    region = (x, y, w, h)
                except:
                    print("フォーマットエラー、使用全画面を使用")

            # キャプチャ、そして追加テンプレート
            success = recognizer.capture_and_add_template(template_name, region)
            if success:
                print(f"✓ テンプレート '{template_name}' 追加に成功！")
            else:
                print("✗ テンプレート追加に失敗")

    else:
        print("無効選択")





