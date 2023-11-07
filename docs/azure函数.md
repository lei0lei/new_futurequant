---
layout: default
title: azure函数
permalink: /azure_func
has_children: false
has_toc: true
---
<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

azure函数位于azure_api文件夹下，包含已部署的azure云函数。




# 邮件发送

发送邮件功能，默认邮件发送人13091171683@163.com

```
endpoint: https://futurequant.azurewebsites.net/api/SendEmail
```

```
POST:

{
  # "recipient": "lei.lei.fan.meng@gmail.com",
  # "subject": "This is a test email from lei",
  # "messages": "aa"
}
```

json中必须包含接受方，主题和消息。



# 每日期货价格

获取每日期货价格数据。

```
endpoint: https://getdailyfutureprice.azurewebsites.net/api/GetDailyFuturePrice
```
```
POST:

{
  "code":"CU2311",
  "start_date":"2023-08-01",
  "end_date":"2023-09-11"
}
```

json中必须包含期货代码和起止日期。


# 每日现货价格

```
endpoint: https://getdailycommodityprice.azurewebsites.net/api/GetDailyCommodityPrice
```

```
POST

{
  "code":"CU",
  "start_date":"2023-08-01",
  "end_date":"2023-09-11"
}
```
json中必须包含现货代码和起止日期

# 所有期货代码获取

```
endpoint: https://getfuturecode.azurewebsites.net/api/GetFutureCode
```

```
GET
```