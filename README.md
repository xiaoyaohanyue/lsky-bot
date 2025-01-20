## 介绍
这是一个是用于兰空图床的TG机器人。

## 功能
- 上传或转发图片到兰空图床
- 邀请tg用户获取临时上传权限

## 准备
- git
- docker
- TG BOT Token
- TG APP ID
- TG APP HASH

## 如何使用

- Docker部署
```shell
mkdir -p /opt/lsky_bot
cd /opt/lsky_bot
git clone https://github.com/xiaoyaohanyue/lsky_tgbot.git .
cp conf/.env.example conf/.env
##修改.env文件
docker compose up -d
```

## 配置.env文件
参考项目路径conf下的.env.example文件，配置好相关参数

## 可用命令
```
/start - 开始使用
/bind - 绑定账号
/unbind - 解绑账号
/my - 查看图床信息
/profile - 查看上传默认策略
/setprofile - 设置上传默认策略
/album - 查看相册列表
/getadmins - 查看管理员列表
/addadmin - 添加管理员
/deladmin - 删除管理员
/invite - 邀请用户
/join - 使用邀请码
/list_invited - 查看被邀请列表
```

---

文档写的比较仓促，后面我找时间好好写一下文档
