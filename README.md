# 我的 Rime 配置备份

包含声笔自然、中日英混输、拼音日语等方案，以及鼠须管外观配置。备份针对 macOS 鼠须管；需要安装带 `librime-lua` 的鼠须管发行版。本机验证所用 Rime 版本为 1.16.0。

## 新电脑恢复

1. 安装鼠须管（Squirrel），在系统设置中添加输入源。安装 Git 和 Python 3.10+。Python 脚本只使用标准库，不需要 pip 安装依赖。
2. 将仓库克隆到 `~/Library/Rime`。该路径必须不存在；如果已经有配置，先退出输入法或切换到其他输入源，将旧目录另行备份，不要直接删除。

   ```bash
   git clone <你的远程仓库地址> "$HOME/Library/Rime"
   cd "$HOME/Library/Rime"
   python3 scripts/prepare.py
   ```

   准备脚本下载约 85 MiB 的日语词库，锁定上游提交并校验 SHA-256。首次准备需要网络连接；已有文件通过校验时会跳过下载。若已有词库被手动修改，脚本会报错并保留文件，请先备份再处理。

3. 点击鼠须管菜单中的「重新部署」。也可以在 macOS 上运行：

   ```bash
   "/Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer" --build \
     "$HOME/Library/Rime" \
     "/Library/Input Methods/Squirrel.app/Contents/SharedSupport"
   "/Library/Input Methods/Squirrel.app/Contents/MacOS/Squirrel" --reload
   ```

4. 用 `Ctrl + \`` 或 `F4` 打开方案菜单，选择需要的方案；较多的菜单项可能需要翻页。中日英混输的用法见 [lua/README.md](lua/README.md)。

鼠须管自带的 `luna_pinyin`、`default.yaml`、标点配置等公共资源由安装包提供，因此不复制进本仓库。其他系统需要对应的 Rime 前端、公共词库和 Lua 支持，本文不保证其安装路径与 macOS 相同。

## 更新和日常备份

新电脑首次用 `clone`，已有仓库更新时用：

```bash
git pull --ff-only
python3 scripts/prepare.py
```

随后重新部署。修改配置后，用 Git 记录并上传：

```bash
git status --short
git add .
git commit -m "Update Rime configuration"
git push
```

远程仓库尚未设置时，在自己的 Git 服务上创建空仓库，然后运行：

```bash
git remote add origin <你的远程仓库地址>
git push -u origin HEAD
```

## 备份范围

- **保留**：方案配置、定制配置、Lua 模块、OpenCC 文件、英文词库、自定义日语词条，以及不能从现有脚本精确还原的中文词库。`sbzr.rimeice.12字.dict.yaml` 被主方案直接引用，必须保留。
- **下载恢复**：五个日语外部词库，路径和校验值见 [scripts/dictionaries.lock.json](scripts/dictionaries.lock.json)。上游固定版本不可用时需更新清单；校验失败会阻止部署准备。
- **忽略**：`build/`、用户数据库、tabledb 学习数据、设备信息、同步目录、生成报告及回滚记录、未被当前方案使用的三字/四字/长句生成词库和 `lua/sbzr_dict_data.lua` 索引。

原始词库工程是 `iamcheyan/rime`，另有 `tumuyan/rime-pinyin-jap` 的方案。本仓库保存当前实际使用的配置，不引入原工程中的浏览器扩展、分析报告或旧清理流程。现有原工程脚本并不能完整复现已安装的中文词库，所以不把必要词库一概忽略；以后有完整可验证的生成流程时再调整规则。

**个人学习记录不会通过 Git 迁移。** 如果需要保留学习词频，请另行使用 Rime 的用户词典管理或原生同步功能备份；定制短语等静态源文件仍在 Git 中。

检查词库准备情况：

```bash
python3 scripts/prepare.py --check
```

只在确认不会丢失个人学习数据后，才考虑清理被 Git 忽略的文件；不要直接使用 `git clean -fdx`。
