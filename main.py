import sys
from random import randint
import pygame
from pygame.locals import (
    Rect,
    QUIT,
    KEYUP,
    KEYDOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_a,
    K_d,
    K_LSHIFT,
)
from drawable import Drawable, Ship, Beam, Shot, Alien

# ウィンドウ
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
SCREEN_LEFT_BOUNDARY = 10
SCREEN_RIGHT_BOUNDARY = 590
ALIEN_GAMEOVER_LINE = 550
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_WIDTH)
# キャプション
GAME_CAPTION = "*** Invader Game ***"
# 色
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (0, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_GRAY = (60, 60, 60)
COLOR_ORANGE = (255, 165, 0)

pygame.init()
# キー押下判定を 5ミリ秒単位にする
pygame.key.set_repeat(5, 5)
surface = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_CAPTION)

# Drawableクラスのクラス変数に、ゲームの画面情報を設定する
Drawable.set_window_info(surface, WINDOW_SIZE)

# ゲームメッセージ文字列
CLEAR_MESSAGE = "CLEAR!!"
GAMEOVER_MESSAGE = "GAME OVER!!"
TITLE_MESSAGE = "INVADER GAME"
START_MESSAGE = "PRESS SPACE TO START"
RETRY_MESSAGE = "PRESS SPACE TO RETRY"
LEVEL_UP_MESSAGE = "LEVEL UP!!"
DASH_MESSAGE = "DASH!!"
# フォント
FONT_SIZE_LARGE = 72
FONT_SIZE_SMALL = 36
LARGE_FONT = pygame.font.SysFont(None, FONT_SIZE_LARGE)
SMALL_FONT = pygame.font.SysFont(None, FONT_SIZE_SMALL)
# 描画用画像（文字列を画像に変換）
CLEAR_MESSAGE_SURFACE = LARGE_FONT.render(CLEAR_MESSAGE, True, COLOR_CYAN)
GAMEOVER_MESSAGE_SURFACE = LARGE_FONT.render(GAMEOVER_MESSAGE, True, COLOR_CYAN)
TITLE_MESSAGE_SURFACE = LARGE_FONT.render(TITLE_MESSAGE, True, COLOR_YELLOW)
START_MESSAGE_SURFACE = SMALL_FONT.render(START_MESSAGE, True, COLOR_WHITE)
RETRY_MESSAGE_SURFACE = SMALL_FONT.render(RETRY_MESSAGE, True, COLOR_WHITE)
LEVEL_UP_MESSAGE_SURFACE = LARGE_FONT.render(LEVEL_UP_MESSAGE, True, COLOR_YELLOW)
DASH_MESSAGE_SURFACE = SMALL_FONT.render(DASH_MESSAGE, True, COLOR_YELLOW)
# ゲーム状態
GAME_STATE_TITLE = "TITLE"
GAME_STATE_PLAY = "PLAY"
GAME_STATE_GAMEOVER = "GAMEOVER"
GAME_STATE_CLEAR = "CLEAR"

# -----ゲーム内処理（ゲーム性に直結する定数）-----
# エイリアン配置
ALIEN_ROW = 4
ALIEN_COL = 10
ALIEN_SPRITE_OFFSET_TOP = 96  # 上段2行の画像オフセット
ALIEN_SPRITE_OFFSET_BOTTOM = 144  # 下段2行の画像オフセット
ALIEN_SPRITE_SIZE = 24
ALIEN_SPACING_X = 50
ALIEN_SPACING_Y = 50
ALIEN_START_X = 100
ALIEN_START_Y = 50
ALIEN_TOP_ROWS = 2  # 上段の行数
ALIEN_SCORE_BASE = 10  # スコア計算用
ALIEN_SCORE_ROW_MULTIPLIER = 4  # スコア計算用
# エイリアン移動
ALIEN_BASE_SPEED = 5
ALIEN_MULTIPLIER_SPEED = 0.75
ALIEN_DOWN_MOVE = 24
ALIEN_MOVE_INTERVAL_INITIAL = 20
ALIEN_MOVE_INTERVAL_MIN = 10
ALIEN_MOVE_INTERVAL_DECREASE = 2
ALIEN_MOVE_INTERVAL_BASE = 20
# エイリアンビーム
ALIEN_TOTAL_BEAM = 8
ALIEN_BEAM_BASE_SPEED = 10
ALIEN_BEAM_MULTIPLIER = 2
ALIEN_BEAM_FIRE_DELAY_MIN = 20
ALIEN_BEAM_FIRE_DELAY_MAX = 200
# 自機とショット
SHIP_MOVE_SPEED = 8
SHOT_MOVE_SPEED = 25
# UI配置
SCORE_POSITION_X = 500
SCORE_POSITION_Y = 10
LEVEL_POSITION_X = 25
LEVEL_POSITION_Y = 10
DASH_GAUGE_OFFSET_Y = 20
DASH_TEXT_OFFSET_Y = 30
RETRY_MESSAGE_OFFSET_Y = 80
MESSAGE_BLINK_INTERVAL = 500  # ミリ秒
LEVELUP_DISPLAY_FRAMES = 12
# ゲーム設定
GAME_FPS = 20
# 3点バースト
BURST_COUNT = 3  # 1回のバーストで発射する弾数
BURST_DELAY = 3  # バースト間の発射間隔（フレーム数）
BURST_COOLDOWN = 15  # 次のバースト開始までのクールダウン
# 緊急回避機能
DASH_GUAGE_WIDTH = 100
DASH_GUAGE_HEIGHT = 10
DASH_SPEED = 40  # ダッシュ時の移動速度
DASH_DURATION = 3  # ダッシュの持続フレーム数
DASH_COOLDOWN_TIME = 30  # ダッシュのクールダウン（フレーム数）


def initialize_game():
    # ゲーム変数の初期化
    keymap = []  # キーマップリセット（押しっぱなし防止など）
    is_gameover = False
    is_left_move = True
    is_down_move = False
    move_interval = ALIEN_MOVE_INTERVAL_INITIAL
    loop_count = 0
    level = 1
    score = 0
    aliens = []
    beams = []
    levelup_timer = 0  # レベルアップ表示用タイマー

    # 自機・ショット・敵の生成
    ship = Ship()
    # 【変更】shots をリストで管理（3点バースト対応）
    shots = []
    burst_remaining = 0
    burst_interval = 0

    # 【追加】緊急回避用変数の初期化
    dash_cooldown = 0
    is_dashing = False
    dash_direction = 0
    dash_timer = 0

    # エイリアンの初期配置
    for ypos in range(ALIEN_ROW):
        offset = (
            ALIEN_SPRITE_OFFSET_TOP
            if ypos < ALIEN_TOP_ROWS
            else ALIEN_SPRITE_OFFSET_BOTTOM
        )
        for xpos in range(ALIEN_COL):
            x = xpos * ALIEN_SPACING_X + ALIEN_START_X
            y = ypos * ALIEN_SPACING_Y + ALIEN_START_Y
            rect = Rect(x, y, ALIEN_SPRITE_SIZE, ALIEN_SPRITE_SIZE)
            score_value = (ALIEN_SCORE_ROW_MULTIPLIER - ypos) * ALIEN_SCORE_BASE
            alien = Alien(rect, offset, score_value)
            aliens.append(alien)

    # エイリアンのビーム初期化
    for _ in range(ALIEN_TOTAL_BEAM):
        beams.append(Beam())

    return {
        "keymap": keymap,
        "is_gameover": is_gameover,
        "is_left_move": is_left_move,
        "is_down_move": is_down_move,
        "move_interval": move_interval,
        "loop_count": loop_count,
        "level": level,
        "score": score,
        "aliens": aliens,
        "beams": beams,
        "levelup_timer": levelup_timer,
        "ship": ship,
        "shots": shots,
        "burst_remaining": burst_remaining,
        "burst_interval": burst_interval,
        "dash_cooldown": dash_cooldown,
        "is_dashing": is_dashing,
        "dash_direction": dash_direction,
        "dash_timer": dash_timer,
    }


def handle_input(
    keymap,
    ship,
    shots,
    burst_remaining,
    burst_interval,
    dash_cooldown,
    is_dashing,
    dash_direction,
    dash_timer,
):
    # 自機の移動距離は毎回０に初期化する
    ship_move_x = 0

    # 左右キーの場合、自機の移動距離を設定
    if K_LEFT in keymap or K_a in keymap:
        ship_move_x = -SHIP_MOVE_SPEED
    if K_RIGHT in keymap or K_d in keymap:
        ship_move_x = SHIP_MOVE_SPEED

        # ===== 緊急回避（ダッシュ）処理 =====
    # ダッシュクールダウンを減らす
    if dash_cooldown > 0:
        dash_cooldown -= 1

    # 【追加】Shiftキー + 方向キーでダッシュ開始
    if K_LSHIFT in keymap and dash_cooldown == 0 and not is_dashing:
        # 左右どちらかのキーが押されている場合のみダッシュ発動
        if K_LEFT in keymap or K_a in keymap:
            is_dashing = True
            dash_direction = -1  # 左方向
            dash_timer = DASH_DURATION
            dash_cooldown = DASH_COOLDOWN_TIME
        elif K_RIGHT in keymap or K_d in keymap:
            is_dashing = True
            dash_direction = 1  # 右方向
            dash_timer = DASH_DURATION
            dash_cooldown = DASH_COOLDOWN_TIME

    # 【追加】ダッシュ中の移動処理
    if is_dashing:
        ship_move_x = DASH_SPEED * dash_direction  # 高速移動
        dash_timer -= 1
        if dash_timer <= 0:
            is_dashing = False  # ダッシュ終了

    # ===== 3点バースト発射処理 =====
    # 【変更】スペースキーでバースト開始（バースト中でなければ）
    if K_SPACE in keymap and burst_remaining == 0 and burst_interval == 0:
        burst_remaining = BURST_COUNT  # バースト残数をセット

    # 【追加】バースト間隔タイマーを減らす
    if burst_interval > 0:
        burst_interval -= 1

    # 【追加】バースト残数があり、間隔タイマーが0なら弾を発射
    if burst_remaining > 0 and burst_interval == 0:
        new_shot = Shot()
        new_shot.rect.center = ship.rect.center
        new_shot.on_draw = True
        shots.append(new_shot)
        burst_remaining -= 1  # 残り発射数を減らす
        # 最後の弾ならクールダウン、途中ならバースト間隔をセット
        if burst_remaining == 0:
            burst_interval = BURST_COOLDOWN  # 次のバーストまでのクールダウン
        else:
            burst_interval = BURST_DELAY  # 次の弾までの間隔

    return {
        "ship_move_x": ship_move_x,
        "shots": shots,
        "burst_remaining": burst_remaining,
        "burst_interval": burst_interval,
        "dash_cooldown": dash_cooldown,
        "is_dashing": is_dashing,
        "dash_direction": dash_direction,
        "dash_timer": dash_timer,
    }


# ======= メイン処理 =======
def main():
    # ゲームの初期状態設定
    game_state = GAME_STATE_TITLE
    keymap = []  # キーマップ

    # ======= メインループ =======
    while True:
        # イベント処理（全状態共通）
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key not in keymap:
                    keymap.append(event.key)
            elif event.type == KEYUP:
                if event.key in keymap:
                    keymap.remove(event.key)

        # ------------------------------------------------
        # 状態1: タイトル画面
        # ------------------------------------------------
        if game_state == GAME_STATE_TITLE:
            # 画面クリア
            surface.fill(COLOR_BLACK)

            # タイトル描画
            title_rect = TITLE_MESSAGE_SURFACE.get_rect()
            title_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
            surface.blit(TITLE_MESSAGE_SURFACE, title_rect.topleft)

            # スタートメッセージ描画
            start_rect = START_MESSAGE_SURFACE.get_rect()
            start_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
            # 点滅演出
            if (pygame.time.get_ticks() // MESSAGE_BLINK_INTERVAL) % 2 == 0:
                surface.blit(START_MESSAGE_SURFACE, start_rect.topleft)

            # スペースキーでゲーム開始（初期化処理）
            if K_SPACE in keymap:
                game_vars = initialize_game()
                # 辞書から各変数を取り出す
                keymap = game_vars["keymap"]
                is_gameover = game_vars["is_gameover"]
                is_left_move = game_vars["is_left_move"]
                is_down_move = game_vars["is_down_move"]
                move_interval = game_vars["move_interval"]
                loop_count = game_vars["loop_count"]
                level = game_vars["level"]
                score = game_vars["score"]
                aliens = game_vars["aliens"]
                beams = game_vars["beams"]
                levelup_timer = game_vars["levelup_timer"]
                ship = game_vars["ship"]
                shots = game_vars["shots"]
                burst_remaining = game_vars["burst_remaining"]
                burst_interval = game_vars["burst_interval"]
                dash_cooldown = game_vars["dash_cooldown"]
                is_dashing = game_vars["is_dashing"]
                dash_direction = game_vars["dash_direction"]
                dash_timer = game_vars["dash_timer"]
                game_state = GAME_STATE_PLAY

        # ------------------------------------------------
        # 状態2: ゲームプレイ中
        # ------------------------------------------------
        elif game_state == GAME_STATE_PLAY:
            # ======= 入力処理 =======
            game_handle = handle_input(
                keymap,
                ship,
                shots,
                burst_remaining,
                burst_interval,
                dash_cooldown,
                is_dashing,
                dash_direction,
                dash_timer,
            )
            
            ship_move_x = game_handle["ship_move_x"]
            shots = game_handle["shots"]
            burst_remaining = game_handle["burst_remaining"]
            burst_interval = game_handle["burst_interval"]
            dash_cooldown = game_handle["dash_cooldown"]
            is_dashing = game_handle["is_dashing"]
            dash_direction = game_handle["dash_direction"]
            dash_timer = game_handle["dash_timer"]
            
            
            # ======= ゲーム内処理 =======
            if not is_gameover:
                loop_count += 1
                ship.move(ship_move_x, 0)

                # 【変更】自機ショットを移動する（リスト内の全弾を処理）
                for s in shots[:]:
                    s.move(0, -SHOT_MOVE_SPEED)
                    # 自機ショットが画面外に行った場合、リストから削除
                    if s.rect.bottom < 0:
                        shots.remove(s)

                # ======= エイリアン軍団を移動する =======
                # ループカウンタが、移動するタイミングの場合
                if loop_count % move_interval == 0:
                    # エイリアンの範囲取得処理
                    if len(aliens) > 0:
                        area = aliens[0].rect.copy()
                        for alien in aliens:
                            area.union_ip(alien.rect)

                        # 左移動フラグに応じて、移動方向（左右移動距離）を決める
                        move_x = (
                            -level * ALIEN_BASE_SPEED * ALIEN_MULTIPLIER_SPEED
                            if is_left_move
                            else level * ALIEN_BASE_SPEED * ALIEN_MULTIPLIER_SPEED
                        )
                        move_y = 0

                        # 「エリア」が左端または右端に当達して、下段移動していない場合
                        if (
                            area.left < SCREEN_LEFT_BOUNDARY
                            or area.right > SCREEN_RIGHT_BOUNDARY
                        ) and not is_down_move:
                            is_left_move = not is_left_move
                            move_x, move_y = 0, ALIEN_DOWN_MOVE
                            move_interval = max(1, move_interval - 2)
                            is_down_move = True
                        else:
                            is_down_move = False

                        # 設定した移動距離に応じて、エイリアンを移動する
                        for alien in aliens:
                            alien.move(move_x, move_y)

                        # エイリアンが最下段まで来たら、ゲームオーバー
                        if area.bottom > ALIEN_GAMEOVER_LINE:
                            is_gameover = True
                            game_state = GAME_STATE_GAMEOVER

                # 敵ビームを移動
                for beam in beams:
                    # 敵ビームが画面上にある場合
                    if beam.on_draw:
                        # 下方向に移動する
                        beam.move(
                            0, ALIEN_BEAM_BASE_SPEED + level * ALIEN_BEAM_MULTIPLIER
                        )
                        # 画面の一番下に到達した場合
                        if beam.rect.top > WINDOW_HEIGHT:
                            # 次の発射タイミングを、ループカウンタ＋αにする
                            beam.fire_timing = loop_count + randint(
                                ALIEN_BEAM_FIRE_DELAY_MIN, ALIEN_BEAM_FIRE_DELAY_MAX
                            )
                            # 敵ビームの描画フラグをFalseにする
                            beam.on_draw = False

                    # ビームが画面上にない場合で、発射タイミング以降となった場合
                    elif beam.fire_timing < loop_count and len(aliens) > 0:
                        # 現在のエイリアン軍団からランダムで１体を選ぶ
                        t_alien = aliens[randint(0, len(aliens) - 1)]
                        # ビームの位置をそのエイリアンに合わせる
                        beam.rect.center = t_alien.rect.center
                        # 敵ビームの描画フラグをTrueにする
                        beam.on_draw = True

                    # 自機の四角が敵ビームの中心と重なった場合
                    if ship.rect.collidepoint(beam.rect.center):
                        is_gameover = True
                        game_state = GAME_STATE_GAMEOVER

                    # ショットとエイリアンの衝突判定（リスト対応）
                    for s in shots[:]:
                        hit = False
                        temp_aliens = []
                        for alien in aliens:
                            # 弾がエイリアンに当たった場合
                            if alien.rect.collidepoint(s.rect.center) and not hit:
                                score += alien.score
                                hit = True  # 1発の弾で1体のみ倒す
                            else:
                                temp_aliens.append(alien)
                        aliens = temp_aliens
                        # 当たった弾はリストから削除
                        if hit:
                            shots.remove(s)

                # 全エイリアンと倒した場合次のレベルへ（リセット）
                if len(aliens) == 0:
                    move_interval = max(
                        ALIEN_MOVE_INTERVAL_MIN,
                        ALIEN_MOVE_INTERVAL_BASE
                        - (level - 1) * ALIEN_MOVE_INTERVAL_DECREASE,
                    )
                    is_left_move = True
                    is_down_move = False
                    aliens = []
                    beams = []
                    for ypos in range(ALIEN_ROW):
                        offset = (
                            ALIEN_SPRITE_OFFSET_TOP
                            if ypos < ALIEN_TOP_ROWS
                            else ALIEN_SPRITE_OFFSET_BOTTOM
                        )
                        for xpos in range(ALIEN_COL):
                            x = xpos * ALIEN_SPACING_X + ALIEN_START_X
                            y = ypos * ALIEN_SPACING_Y + ALIEN_START_Y
                            rect = Rect(x, y, ALIEN_SPRITE_SIZE, ALIEN_SPRITE_SIZE)
                            score_value = (
                                ALIEN_SCORE_ROW_MULTIPLIER - ypos
                            ) * ALIEN_SCORE_BASE
                            alien = Alien(rect, offset, score_value)
                            aliens.append(alien)
                    # 敵ビーム生成
                    for _ in range(ALIEN_TOTAL_BEAM):
                        beams.append(Beam())
                    level += 1
                    levelup_timer = LEVELUP_DISPLAY_FRAMES

            # ======= 描画処理 =======
            surface.fill(COLOR_BLACK)
            ship.draw()
            # 全てのショットを描画（リスト対応）
            for s in shots:
                s.draw()
            for alien in aliens:
                alien.draw()
            for beam in beams:
                beam.draw()

            # スコアの描画
            score_str = str(score).zfill(5)
            score_image = SMALL_FONT.render(score_str, True, COLOR_GREEN)
            surface.blit(score_image, (SCORE_POSITION_X, SCORE_POSITION_Y))

            # レベルの描画
            level_str = f"Level {level}"
            level_image = SMALL_FONT.render(level_str, True, COLOR_GREEN)
            surface.blit(level_image, (LEVEL_POSITION_X, LEVEL_POSITION_Y))

            # ダッシュゲージの描画（画面下部）
            dash_gauge_x = WINDOW_WIDTH // 2 - DASH_GUAGE_WIDTH // 2
            dash_gauge_y = WINDOW_HEIGHT - DASH_GAUGE_OFFSET_Y
            # ゲージ背景
            pygame.draw.rect(
                surface,
                COLOR_GRAY,
                (dash_gauge_x, dash_gauge_y, DASH_GUAGE_WIDTH, DASH_GUAGE_HEIGHT),
            )
            # ゲージ本体（クールダウン残量に応じて増減） 本体の上に重ねて描画
            if dash_cooldown == 0:
                gauge_color = COLOR_CYAN
                gauge_fill = DASH_GUAGE_WIDTH
            else:
                gauge_color = COLOR_ORANGE
                gauge_fill = int(
                    DASH_GUAGE_WIDTH * (1 - dash_cooldown / DASH_COOLDOWN_TIME)
                )
            pygame.draw.rect(
                surface,
                gauge_color,
                (dash_gauge_x, dash_gauge_y, gauge_fill, DASH_GUAGE_HEIGHT),
            )
            # ダッシュ中は点滅表示
            if is_dashing and loop_count % 2 == 0:
                dash_rect = DASH_MESSAGE_SURFACE.get_rect()
                dash_rect.center = (
                    WINDOW_WIDTH // 2,
                    WINDOW_HEIGHT - DASH_TEXT_OFFSET_Y,
                )
                surface.blit(DASH_MESSAGE_SURFACE, dash_rect.topleft)

            # レベルアップ表示
            if levelup_timer > 0:
                levelup_rect = LEVEL_UP_MESSAGE_SURFACE.get_rect()
                levelup_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                surface.blit(LEVEL_UP_MESSAGE_SURFACE, levelup_rect.topleft)
                levelup_timer -= 1
        # ------------------------------------------------
        # 状態3: ゲームオーバー / クリア
        # ------------------------------------------------
        elif game_state in (GAME_STATE_GAMEOVER, GAME_STATE_CLEAR):
            surface.fill(COLOR_BLACK)
            if ship:
                ship.draw()
            for alien in aliens:
                alien.draw()
            for beam in beams:
                beam.draw()

            # スコア描画
            score_str = str(score).zfill(5)
            score_image = SMALL_FONT.render(score_str, True, COLOR_GREEN)
            surface.blit(score_image, (SCORE_POSITION_X, SCORE_POSITION_Y))

            # レベルの描画
            level_str = f"Level {level}"
            level_image = SMALL_FONT.render(level_str, True, COLOR_GREEN)
            surface.blit(level_image, (LEVEL_POSITION_X, LEVEL_POSITION_Y))

            # メッセージ表示
            if game_state == GAME_STATE_CLEAR:
                msg_rect = CLEAR_MESSAGE_SURFACE.get_rect()
                msg_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                surface.blit(CLEAR_MESSAGE_SURFACE, msg_rect.topleft)
            else:
                msg_rect = GAMEOVER_MESSAGE_SURFACE.get_rect()
                msg_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                surface.blit(GAMEOVER_MESSAGE_SURFACE, msg_rect.topleft)

            # リトライメッセージ
            retry_msg = RETRY_MESSAGE_SURFACE
            retry_rect = retry_msg.get_rect()
            retry_rect.center = (
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 + RETRY_MESSAGE_OFFSET_Y,
            )
            if (pygame.time.get_ticks() // MESSAGE_BLINK_INTERVAL) % 2 == 0:
                surface.blit(retry_msg, retry_rect.topleft)

            # スペースキーでリスタート
            # 「GAMEOVER」時にSPACEキーが入力されているとタイトル画面へ、改めて入力されると即リスタートになる
            # ゲーム性にそこまで影響がないので放置する
            if K_SPACE in keymap:
                game_state = GAME_STATE_TITLE
                # キー入力を一度クリアしておかないと、タイトル画面で即スタートしてしまうのを防ぐ
                if K_SPACE in keymap:
                    keymap.remove(K_SPACE)

        # 画面更新
        pygame.display.update()
        # 一定間隔の処理
        clock.tick(GAME_FPS)


if __name__ == "__main__":
    main()
