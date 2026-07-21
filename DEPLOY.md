# 部署指南

## 步骤1：创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`task-dashboard`（或任意名称）
4. 选择 "Public" 或 "Private"
5. 点击 "Create repository"

## 步骤2：配置 GitHub Secrets

1. 进入仓库页面
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. Name: `TAPD_API_TOKEN`
5. Value: `b2193e4681b09f09729b99f45886bc4d180cc1db`（你的 TAPD API Token）
6. 点击 "Add secret"

## 步骤3：上传代码到 GitHub

```bash
# 进入项目目录
cd ~/.openclaw/workspace

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 业务二组人力投入看板"

# 关联远程仓库
git remote add origin https://github.com/你的用户名/task-dashboard.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 步骤4：启用 GitHub Pages

1. 进入仓库页面
2. 点击 "Settings" → "Pages"
3. Source: 选择 "Deploy from a branch"
4. Branch: 选择 "main" → "/ (root)"
5. 点击 "Save"
6. 等待几分钟，页面会显示访问地址

## 步骤5：验证自动更新

1. 进入仓库页面
2. 点击 "Actions" 标签
3. 查看 "Update TAPD Data" 工作流
4. 可以手动点击 "Run workflow" 测试

## 访问地址

GitHub Pages 部署完成后，访问地址为：
```
https://你的用户名.github.io/task-dashboard/task-dashboard.html
```

## 团队成员访问

将上述链接分享给团队成员，即可随时查看看板。

## 注意事项

1. **数据更新频率**：每小时自动更新一次
2. **首次部署**：需要等待几分钟 GitHub Pages 部署完成
3. **API Token 安全**：已存储在 GitHub Secrets，不会泄露
4. **私有仓库**：如果选择 Private，需要团队成员有 GitHub 账号并授权访问

## 常见问题

### Q: 页面显示 404？
A: 等待几分钟 GitHub Pages 部署完成，或检查文件路径是否正确。

### Q: 数据没有更新？
A: 检查 Actions 标签，查看工作流是否运行成功。

### Q: 如何手动触发更新？
A: 进入 Actions → Update TAPD Data → Run workflow。
