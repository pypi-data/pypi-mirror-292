## 数据
新增板块：过期上交所、过期深交所
沪港通深港通板块不再显示历史标的

## 功能
期货夜盘显示真实时间功能默认开启
未开启时， 周六凌晨的行情数据时间为周一
开启时，周六凌晨的行情数据时间为周六

撤单接口的市场参数支持字符串格式，如SH、SF
xttrader.cancel_order_stock_sysid()和xttrader.cancel_order_stock_sysid_async()

添加函数xtdata.get_his_option_list_batch()和xtdata.get_his_option_list()
获取历史上某段时间的指定品种期权信息列表
依赖数据'optionhistorycontract'

期权函数支持商品期权品种 xtdata.get_option_undl_data()和xtdata.get_option_list()

郑商所期权标的代码调整为4位 xtdata.get_option_detail_data()

移除郑商所过滤重复tick的逻辑