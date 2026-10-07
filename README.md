# 室友正在优化

原创二维轻喜剧系列。程序员阿程与他创造的 AI 室友积木，在同一间公寓里做小项目、过日子。

[▶ 直接观看第1集 · 完整62秒](https://yydshly.github.io/selected-works/#shorts)

## 当前作品
- 第1集《先别承诺》：已完成双角色配音试播，62.083秒，1280×720，24fps。播放 `films/episode-01-voiced.mp4`
- 第2集《大一点》：完整剧本与分镜草案，目标78秒，尚未制作
- 第3至6集：故事提案，尚未制作。见 `docs/SERIES_ROADMAP.md`

每集关注具体的小问题与两位角色的关系变化。人物和情节均为虚构，不对应真实个人经历。后续集的提案不代表已经制作或承诺发布日期。

## 制作内容
- `source/`：原版画面、声音与故事脚本，保留为当前制作的基础
- `v2/source/`：配音版渲染、机器人音色处理、真实语速重剪与混音
- `v2/voices/`：原始语音素材、机器人处理后语音、嘴形及声音时序
- `docs/`：系列规划、第二集分镜、可编辑策划文档和验证记录
- `films/`：当前完整作品与字幕

阿程使用青年男声；积木使用温暖、平直的电子音色。`v2/voices/processed/` 中是机器人最终音轨，未经处理的机器人语音仅是制作底音。两名角色使用 MiniMax 系统预设语音，不是名人或特定真实人物克隆。角色、场景、剧本、配乐与音效为本项目原创制作。

## 本地重建
依赖：Python 3、Pillow、NumPy、SciPy、带 rubberband 滤镜的 FFmpeg、Noto Sans CJK 字体。字体二进制不包含在仓库中。

从仓库根目录运行：

```
python v2/source/prepare_voiced_edit.py
python v2/source/render.py 62.08226757369614 pilot-voiced
```

第一步会更新 `v2/source/timing-revision.json`；如修改对白素材，以其中的 `new_duration` 替换第二步的时长。输出在 `v2/site/dist/pilot-voiced.mp4`。

仓库包含所需对白音频。重建过程不需要 API Key，不发起语音服务请求。没有配置文件中的账户密钥或付费接口客户端。

## 质量与范围
这是风格化二维角色动画试播。人物有表情、肢体动作，嘴形由语音强弱驱动。整片媒体解码、11段对白时序与关键画面检查记录见 `docs/production-verification.json`。数值检查不能代替主观听感与表演评价。
