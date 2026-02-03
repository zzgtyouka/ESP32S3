from machine import SPI, Pin
import time
from ST7735 import atk_tft, BLACK, WHITE, RED, GREEN, BLUE
from framebuf import FrameBuffer, RGB565

# ====================== 硬件配置 ======================
# 1. SPI和LCD配置
spi = SPI(1, baudrate=10000000, polarity=0, phase=0, 
          sck=Pin(12), mosi=Pin(11))
DC_PIN = 40
RST_PIN = 38
CS_PIN = 39
BL_PIN = 41
ROTATE = 1  # 顺时针旋转90°（横屏160*80）

# 2. LED配置
LED_PIN = 1
led = Pin(LED_PIN, Pin.OUT)
led_state = 0
last_led_time = 0
LED_INTERVAL = 500

# ====================== 初始化 ======================
# 初始化LCD（旋转90°）
tft = atk_tft(spi, DC_PIN, RST_PIN, CS_PIN, BL_PIN, ROTATE)
tft.clear(WHITE)

# 初始化LED
led.value(0)

# ====================== 适配旋转后的参数 ======================
# 旋转90°后，屏幕实际分辨率：宽160，高80
WIDTH = 160  
HEIGHT = 80
# 创建帧缓冲区（适配横屏分辨率）
buf = bytearray(WIDTH * HEIGHT * 2)
fb = FrameBuffer(buf, WIDTH, HEIGHT, RGB565)

# 小球参数（极致提速）
size = 10
x, y = WIDTH//2, HEIGHT//2
vx, vy = 8, 8  # 步长8，速度最快
# 颜色定义（RGB565格式）
TEXT_COLOR = 0xF800  # 红色
BALL_COLOR = 0xFFFF  # 白色
BG_COLOR = 0x0000    # 黑色

# ====================== 主循环 ======================
print("屏幕旋转90°，小球已极致提速，字符串绘制修复")
while True:
    # 1. LED 500ms闪烁（非阻塞）
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_led_time) >= LED_INTERVAL:
        led_state = not led_state
        led.value(led_state)
        last_led_time = current_time

    # 2. 清空帧缓冲区（黑色背景）
    fb.fill(BG_COLOR)

    # 3. 绘制小球（适配横屏分辨率）
    fb.ellipse(x, y, size, size, BALL_COLOR, True)

    # 4. 绘制字符串（用framebuf原生方法，无下标越界）
    # 字符串1：固定文本（红色）
    fb.text("TFT LCD 90° Rotate", 10, 10, TEXT_COLOR)
    # 字符串2：LED状态（红色）
    led_text = "LED: ON" if led_state else "LED: OFF"
    fb.text(led_text, 10, 25, TEXT_COLOR)
    # 字符串3：小球速度（红色）
    fb.text(f"Speed: {vx}px/frame", 10, 40, TEXT_COLOR)

    # 5. 更新小球位置（适配横屏边界）
    x += vx
    if x <= size or x >= WIDTH - size:
        vx = -vx
    y += vy
    if y <= size or y >= HEIGHT - size:
        vy = -vy

    # 6. 同步帧缓冲区到LCD（无延时，极致速度）
    tft.draw_bmp(0, 0, WIDTH, HEIGHT, buf)
    # 可选：若屏幕闪烁，添加极短延时
    # time.sleep(0.001)