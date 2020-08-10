# scrapy_selneium_amazon
- 使用 scrapy + selenium 获取亚马逊的数据
- 在 middlewares 中创建 middleawre，download 动作的请求会调用 selenium 进行访问；
- 本文同时基于 twisted + mysql 实现了获取数据的异步写入；
