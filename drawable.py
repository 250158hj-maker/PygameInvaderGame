from random import randint
import pygame
from pygame.locals import Rect

# ======= 描画クラス =======
class Drawable:
    # クラス変数
    surface = None         # 描画する対象
    window_size = None     # ウィンドウのサイズ
    
    # Ａ－１最初）クラスメソッド：ウィンドウ情報の設定
    @classmethod
    def set_window_info(cls, surface, window_size):
        # Ａ－２）描画対象の画面を設定
        cls.surface = surface
        # Ａ－３）描画対象の画面のサイズを設定
        cls.window_size = window_size
    
    # Ａ－４）コンストラクタ
    # offset1, 2は、２種類（自機は１種類）の画像の位置
    def __init__(self, rect, offset0, offset1):
        # Ａ－５）横に繋がった画像ファイルを読み込む
        wide_image = pygame.image.load('./image/characters.png')
        # Ａ－６）画像用の小さな描画領域を作成する
        # pygame.SRCALPHAを指定すると、背景を透過することができる
        self.images = (pygame.Surface((24, 24), pygame.SRCALPHA),
                       pygame.Surface((24, 24), pygame.SRCALPHA))
        
        # Ａ－７）描画用の四角
        self.rect = rect
        # Ａ－８）描画用のカウンタ
        self.count = 0
        # Ａ－９）描画フラグ（Falseでは描画しない）
        self.on_draw = True
        # Ａ－１０）画像１
        self.images[0].blit(wide_image, (0, 0), Rect(offset0, 0, 24, 24))
        # Ａ－１１）画像２
        self.images[1].blit(wide_image, (0, 0), Rect(offset1, 0, 24, 24))

    # Ａ－１２）描画処理
    def draw(self):
        # Ａ－１３）描画フラグがFalseの場合は描画しない
        if self.on_draw:
            # Ａ－１４）countの値によって、描画する画像を入れ替える
            if self.count % 2 == 0:
                self.surface.blit(self.images[0], self.rect.topleft)
            else:
                self.surface.blit(self.images[1], self.rect.topleft)

    # Ｂ－１９最初）移動処理
    def move(self, diff_x, diff_y):
        # Ｂ－２０）移動時に、カウンタを１増やす
        self.count += 1
        # Ｂ－２１）移動方向へと移動する
        self.rect.move_ip(diff_x, diff_y)

# 自機クラス
class Ship(Drawable):
    # Ａ－１５mainへ）コンストラクタ
    def __init__(self):
        super().__init__(Rect(300, 550, 24, 24), 192, 192)

        
    # Ｂ－２２）移動処理（親クラスのオーバーライド）
    def move(self, diff_x, diff_y):
        # Ｂ－２３）移動後の位置が画面外に行かない場合
        if 12 <= self.rect.centerx + diff_x < self.window_size[0] - 12:
            # Ｂ－２４）移動距離を設定して、親クラスの移動処理を実行
            super().move(diff_x, diff_y)
        # Ｂ－２５）画面外に行ってしまう場合
        else:
            # Ｂ－２６mainへ）移動距離を０にするが、親クラスの移動処理は行う→画面は時でも時機のアニメーションが動くようにする
            super().move(0, 0)

# エイリアンクラス
class Alien(Drawable):
    # Ｃ－３６最初）コンストラクタ
    def __init__(self, rect, offset, score):
        super().__init__(rect, offset, offset + 24)
        # Ｃ－３７mainへ）倒した時のスコアを設定
        self.score = score

# 自機ショットクラス
class Shot(Drawable):
    # Ｄ－４７最初）コンストラクタ
    def __init__(self):
        super().__init__(Rect(0, 0, 24, 24), 0, 24)
        # Ｄ－４８mainへ）初期状態では描画しない
        self.on_draw = False

# 敵ビームクラス
class Beam(Drawable):
    # Ｇ－８２最初）コンストラクタ
    def __init__(self):
        super().__init__(Rect(0, 0, 24, 24), 48, 72)
        # Ｇ－８３）敵ビームが撃たれるタイミングをランダムで決定する
        self.fire_timing = randint(5, 220)
        # Ｇ－８４mainへ）初期状態では描画しない
        self.on_draw = False
