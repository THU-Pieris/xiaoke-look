# xiaoke-look · Claude娘 午后主题

给 Claude 桌面端 Code 标签用的主题 mod：暖奶白纸色配色、深褐文字、橙色强调色，对话背后是一张 Claude 娘在窗边读书的插画。插画贴在窗口右上角，向左、向下渐变淡出成留白，空白处有几片花瓣很慢地飘落。

A Claude Code mod that gives the desktop app's Code tab a warm paper palette and an illustration of Claude-chan reading by a sunny window, fading into blank paper toward the left and the bottom.

![xiaoke-look in the Claude desktop app (conversation text blurred)](docs/screenshot.png)

## 安装 / Install

在终端里的 Claude Code 会话输入（At the prompt of a terminal session）:

```
/plugin install xiaoke-look --marketplace bananaeat/xiaoke-look
```

先回答 `y` 添加 marketplace，再选 user scope。装好后，之后新开的会话（包括桌面端 Code 标签的本地会话）都会加载它。

From a shell:

```
claude plugin install xiaoke-look --marketplace bananaeat/xiaoke-look
```

桌面端里 `/plugin` 不能用：点输入框旁的 **+** → Plugins → Add marketplace，填 `bananaeat/xiaoke-look`，再 Add plugin。
In the desktop app, where `/plugin` does not run: click **+** next to the prompt box, then Plugins, Add marketplace with `bananaeat/xiaoke-look`, then Add plugin.

需要能显示 mod 主题的 Claude 桌面端（在 Claude Code 2.1.326 上测试过）。终端和编辑器里不显示主题。
Needs a Claude desktop app that draws mod looks (tested with Claude Code 2.1.326); terminals and editors draw no look.

## 说明 / Notes

- **只有浅色模式。** 插画是为亮的房间画的，所以主题固定为浅色。Light mode only.
- **背景是纯矢量。** 桌面端的背景只接受纯矢量 SVG（不能嵌位图，最多 131072 字符），所以原画（`docs/painting.png`）被描摹成了约 10.9 万字符的平涂色块 SVG。The backdrop is pure vector: the painting was traced into ~109K characters of flat-ink paths.
- 开启"减少动态"时花瓣静止。Petals rest in place under reduced motion.

## 自己重新描摹 / Rebuilding the scene

`tools/` 里是描摹流程（Python 3，需要 numpy、opencv-python、resvg-py）:

```
python tools/trace.py docs/painting.png vec.json --scale 1.0 --colors 20 --eps 1.0 --minarea 9 --crop 0,0,1024,1150
python tools/build_scene.py vec.json hooks/scene.ts preview.svg
python tools/render.py preview.svg preview.png 1600
```

思路：先把人物剪影整个铺成描线色，再把各色块盖上去，线稿就是色块之间留下的缝；色块会向外扩半个像素来补缝，但不会盖住线稿像素。`tools/painting_prompt.txt` 是生成原画用的提示词。

## 致谢与授权 / Credits & license

- Claude 娘的角色设计来自 **ZipZipPipe** 的同人设定。这是粉丝自制作品，与 Anthropic 无关。Character design after ZipZipPipe's fan design of Claude-chan; fan work, not affiliated with Anthropic.
- 代码以 MIT 协议发布（见 `LICENSE`）。插画（`docs/*.png`、`hooks/scene.ts` 里的图形）请仅作非商业用途。Code is MIT; please keep the artwork non-commercial.
- `hooks/make-colors.js` 来自 Claude Code 的 plugin-authoring 工具，用来生成设计系统的配色。
