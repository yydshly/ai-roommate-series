# 第二集 大一点

## 当前状态
- 24秒动作与时序样段已实现，含三次拉大按钮、内容挤出、角色反应、两次点偏、扩大点击范围后的成功点击
- 12镜头完整画面实现已写入，目标78秒，包含椅腿缠线与抬椅解线结尾
- 新对白尚未生成，当前可播放样段只有原创音乐、音效和台词字幕，不是完成配音的第二集

## 文件
- `source/render_action_sample.py`：动作样段渲染器
- `source/render_episode.py`：整集画面与声音接入
- `source/storyboard.json`：本集12镜头
- `source/robot_dsp.py`：与第一集一致的机器人音色处理
- `source/mix_dialogue.py`：读取本地配音素材、处理机器人声、背景避让和嘴形时序
- `output/episode-02-action-sample.mp4`：已验证的24秒样段
- `output/verification.json`：样段验证记录

## 复现
从项目根目录运行：

```
python episode-02/source/render_action_sample.py
python episode-02/source/render_episode.py
```

角色骨骼复用仓库的 `source/render.py`。配音到位后读取 `episode-02/voices/e02-line-XX.mp3`（XX为镜头号），先运行 `mix_dialogue.py`，再运行整集渲染器。脚本不含API调用或凭据；缺少素材会停止混音，不生成替代对白。

第二集的新故事重点是确认需求，不重复第一集的过度承诺笑点。角色、场景、已确定的男声与机器人电子音色保持连续。
