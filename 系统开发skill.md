# 家庭管理 App - 项目进度文档

> 生成时间：2026-09-17
> 用途：新对话上下文恢复，请在新对话开头先读取本文件。

---

## 一、项目架构

```
family_app/
├── backend/              # FastAPI 后端（所有 API + 管理接口）
│   ├── app/
│   │   ├── main.py           # 入口，路由挂载
│   │   ├── config.py         # 配置（数据库、Redis、密钥）
│   │   ├── database.py       # SQLAlchemy 异步引擎
│   │   ├── redis_client.py   # Redis 客户端
│   │   ├── security.py       # 密码哈希、token 工具
│   │   ├── deps.py           # 依赖注入（get_current_user、require_admin）
│   │   ├── models.py         # SQLAlchemy ORM 模型（5张表）
│   │   ├── schemas/          # Pydantic schemas（已替代旧 schemas.py）
│   │   ├── routers/
│   │   │   ├── auth.py           # 登录/登出
│   │   │   ├── user.py           # 用户侧：我的菜单、记录点击
│   │   │   └── admin/            # 管理侧：用户/家庭/分类/菜单/权限/会话
│   │   └── services/
│   │       └── user_service.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── mobile_app/           # Vue3 + Vite + Vant + Capacitor 混合 App
│   ├── src/
│   │   ├── main.js           # 入口
│   │   ├── App.vue           # TabBar 控制（登录页隐藏 tab）
│   │   ├── router/index.js    # 路由：login / home / me / webview
│   │   ├── store/index.js    # 简易 store（user / categories / menus / familyName）
│   │   ├── api/user.js       # API：login / logout / getMyMenus / recordMenuClick
│   │   ├── config/domain.js  # 域名配置（写死默认域名，localStorage 可改）
│   │   ├── utils/storage.js  # localStorage 封装（KEY.sessionId 等）
│   │   └── views/
│   │       ├── Login.vue         # 登录页 + 域名配置弹窗
│   │       ├── Home.vue          # 首页（分类 tab + 菜单网格 + 拖拽切换）
│   │       ├── Me.vue           # 我的页面（用户卡片 + 信息列表 + 域名设置）
│   │       └── WebView.vue       # iframe 内嵌（PC 预览时用）
│   └── capacitor.config.ts   # Capacitor 配置（Android 壳）
│
└── admin_web/            # 后台管理前端（待开发，Vue3 + Element Plus）

--- admin 是路由 namespace，admin_web 是独立前端项目
```

---

## 二、混合架构说明（核心设计）

App 壳（Capacitor）只包含：登录 + 首页 + 我的。
功能模块通过以下两种方式打开：
1. **原生壳内**：通过 Capacitor Browser 插件全屏打开 URL（真机）
2. **PC 预览**：router.push 到 WebView.vue，iframe 加载 URL

URL 拼接逻辑（`domain.js`）：
- external=1（外链）：直接用菜单表存的 http 开头的完整 URL
- external=0（内部）：菜单表只存路径（如 `/tasks`），自动拼接配置的域名

---

## 三、数据库表结构（PostgreSQL，全部 UUID 主键，t_ 前缀）

### t_user（用户表）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID PK | 主键 |
| username | VARCHAR UNIQUE | 登录账号 |
| password_hash | VARCHAR | bcrypt 密码 |
| nickname | VARCHAR | 昵称 |
| gender | SMALLINT NOT NULL | 0女 1男 |
| family_id | UUID FK → t_family | 所属家庭 |
| admin_flag | BOOLEAN | 是否管理员 |
| disabled | BOOLEAN | 是否禁用 |
| last_login_time | DATETIME | 最后登录 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### t_family（家庭表）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID PK | |
| name | VARCHAR | 家庭名称 |
| created_at | DATETIME | |

### t_fam_menu_category（菜单分类表）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID PK | |
| name | VARCHAR | 分类名（家务/财务/生活...） |
| sort | INT | 排序 |
| created_at | DATETIME | |

### t_fam_menu（菜单表）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID PK | |
| name | VARCHAR | 菜单名 |
| icon | VARCHAR | emoji 图标 |
| category_id | UUID FK | 所属分类 |
| url | VARCHAR | 功能模块地址（内部存路径，外链存完整 URL） |
| external | SMALLINT | 0=内部模块（自动拼域名+加 token） 1=外链（直接访问） |
| start_time | DATETIME | 菜单有效期开始 |
| end_time | DATETIME | 菜单有效期结束 |
| sort | INT | 排序 |
| created_at | DATETIME | |

### t_fam_user_menu（用户-菜单关联表 = 权限表）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK | 用户 |
| menu_id | UUID FK | 菜单 |
| click_count | INT | 点击次数（用于统计常用功能） |
| last_click_time | DATETIME | 最后点击时间 |
| created_at | DATETIME | |

**权限模型说明**：没有角色表，直接 user-menu 多对多关联。admin_flag 字段区分管理员/普通用户。菜单是否显示 = 用户-菜单表里有记录 + 菜单在有效期内。

---

## 四、后端 API 列表

### 用户侧（需 session 验证）
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/auth/login | 登录（返回 session_id） |
| POST | /api/auth/logout | 登出 |
| GET | /api/auth/server-config | 返回默认域名（前端首次加载时获取） |
| GET | /api/user/info | 当前用户信息 |
| GET | /api/user/my-menus | 当前用户可见菜单（含分类+常用功能 top6） |
| POST | /api/user/menu/{id}/click | 记录菜单点击（用于常用功能统计） |

### 管理侧（需 admin_flag）
| 方法 | 路径 | 说明 |
|---|---|---|
| 多 | /api/admin/users | 用户 CRUD |
| 多 | /api/admin/families | 家庭 CRUD |
| 多 | /api/admin/categories | 菜单分类 CRUD |
| 多 | /api/admin/menus | 菜单 CRUD |
| 多 | /api/admin/permissions | 用户-菜单权限管理 |
| 多 | /api/admin/sessions | 会话管理（踢人下线等） |

### 认证机制
- Redis 存储 session（key=session_id，value=user_id + expire）
- App 端：localStorage 存 `sessionId`，API 请求 header 带 `Authorization: Bearer <session_id>`
- WebView 内部模块：URL 追加 `?session_id=xxx`（后端可从 URL 参数取）
- 外链模块：不追加 token，纯外部访问

---

## 五、前端页面说明

### Login.vue
- 网格背景 + 径向遮罩
- Hero 区：问候语 + 日期 + 家庭名
- 自研搜索框（聚焦蓝色边框+光晕）
- 登录/注册切换 tab
- 域名配置弹窗（首次进入自动弹出，localStorage 里没有域名时触发）

### Home.vue（首页，登录后进入）
- 网格背景
- Hero 区：问候语 + 日期 + 家庭名
- 自研搜索框（实时过滤所有菜单，搜索状态下隐藏分类）
- 分类 tab 行（家务/财务/生活/...，自研 tab-btn）
- 菜单网格（4 列 grid）
- 拖拽切换效果：
  - touchstart/move/end 跟手移动
  - swipe-track 横向并排渲染 [prev, current, next] 3 个面板
  - 边缘阻尼 0.3
  - 阈值 25% 屏宽决定切换/回弹
  - tab 点击直接切（不走动画，避免跨 tab 滑空）
- **已删除**：常用功能区域（frequentMenus）

### Me.vue（我的）
- 大标题 "我的"（跟 Home hero 标题一致风格）
- 用户卡片：圆角头像 + 昵称 + admin 徽章 + 账号
- 信息列表：所属家庭 / 账号
- 设置列表：域名配置（自研弹窗）
- 退出登录：白底红字按钮
- TabBar：只有 login 页隐藏 tab

### WebView.vue
- iframe 容器，PC 预览用
- 真机上不用（直接 Capacitor Browser 全屏打开）

---

## 六、设计规范（Login.vue 样式为基准）

| 元素 | 规范 |
|---|---|
| 背景色 | #f5f5f4 暖灰白 |
| 网格背景 | 28px 网格 + 径向遮罩（top 20%→transparent 70%）|
| 主色 | #0ea5e9 天蓝 |
| 深色主 | #0284c7 按下态 |
| 卡片 | 白色 + 1px solid #e7e5e4 + 圆角 16px |
| 输入框 | 聚焦天蓝边框 + 4px 淡蓝光晕 |
| 圆角 | 10px 输入 / 12px 按钮 / 14px 图标 / 16px 卡片 / 20px 弹窗 |
| 间距 | 页面外边距 20-28px |
| 点击反馈 | scale(0.96) 微缩 |
| 文字 | 主 #1c1c1e · 次 #8a8a8e · 辅 #b8b5b0 |

---

## 七、启动方式

### 后端
```bat
:: 根目录 backend 下
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
已封装为 `backend/start.bat`

### 前端 App（开发预览）
```bat
:: 根目录 mobile_app 下
npm run dev
```
已封装为 `mobile_app/start.bat`

### 数据库连接
配置文件：`backend/app/config.py` 或 `.env`
默认：PostgreSQL，注意表名全部 t_ 前缀

### 首条管理员数据
```sql
INSERT INTO t_user (id, username, password_hash, nickname, gender, family_id, admin_flag)
VALUES (gen_random_uuid(), 'admin', '<bcrypt哈希>', '管理员', 1, NULL, true);
-- 密码用 backend/create_admin.py 生成 bcrypt hash
```

---

## 八、已解决的历史问题（备查）

1. **表名统一 t_ 前缀**：废弃 sys_user 等旧名，全部改为 t_user / t_family / t_fam_menu_category / t_fam_menu / t_fam_user_menu
2. **schemas.py → schemas/ 目录**：删除旧单文件 schemas.py，改为目录多文件结构，__init__.py 统一导出
3. **admin_flag 保留**：无角色表，admin_flag 用于区分管理员和普通用户
4. **external 字段保留**：菜单表 external 字段判断是否内部模块，自动决定是否拼域名+加 token
5. **session 机制**：UUID session_id 存 Redis，App 存 localStorage，WebView 拼 URL query
6. **域名配置**：写死 `http://192.168.0.6:8000` 为默认值，自动加载到 localStorage，可在 Me 页面自定义
7. **菜单有效期**：start_time / end_time，后端自动过滤过期菜单
8. **常用功能**：后端返回 top6（按 click_count + last_click_time），前端已删除展示区域

---

## 九、待开发/待办

- [ ] **后台管理前端** admin_web（Vue3 + Element Plus）
  - 用户管理：增删改查、设置 admin_flag、分配家庭
  - 家庭管理：增删改查
  - 菜单分类管理：增删改查 + 排序
  - 菜单管理：增删改查 + icon/emoji + url + external + 有效期
  - 权限管理：用户-菜单勾选分配
  - 会话管理：查看在线用户、强制下线
- [ ] 域名配置：后端可返回默认/备用域名（当前写死）
- [ ] 飞牛部署：后端 Docker 部署文档
- [ ] Android 打包：apk 签名、release 构建
- [ ] 真机测试：所有功能模块联调

---

## 十、关键决策记录

| 决策 | 选择 | 理由 |
|---|---|---|
| 权限模型 | 无角色，user-menu 直接关联 | 用户少，简化，够用 |
| token | 单 session_id（UUID）存 Redis | 简单，可踢人下线 |
| 菜单有效期 | start_time + end_time | 临时功能模块可自动过期 |
| 内部/外链区分 | external 字段（0/1） | 自动决定是否拼域名+加 token |
| 默认域名 | 写死在 domain.js + localStorage | 先跑通，后面改可配置 |
| TabBar 位置 | App.vue 统一控制 | 登录页隐藏，其他页显示 |
| WebView 策略 | 真机 Capacitor Browser，PC iframe | 真机全屏体验，开发方便 |
| 常用功能展示 | 已删除前端区域，后端保留 | 用户要求暂不展示，但保留统计能力 |
| 主题切换 | 已删除白天/黑夜切换 | 用户要求先删除 |
| iOS | 暂不考虑 | 无法越狱安装非商店 App |