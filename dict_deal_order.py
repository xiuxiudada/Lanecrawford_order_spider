import parsel
import pandas as pd
import requests as req

ck = ""


def load_net_css_file():
    url = "https://www.lanecrawford.com.hk/account/include/orderHistory/orderHistoryList.jsp"
    order_date = str(input("请输入要查询过去的几个月的订单(默认为3个月):"))
    if order_date.strip() == "":
        order_date = "3"
    headers = {
        "Cookie": ck,
        "orderDate": order_date,
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome",
        "orderState": "ALL"
    }
    content = req.get(url, headers=headers).content.decode()
    # with open("/Users/hugh/Desktop/test.css", "r", encoding="utf-8") as f:
    #     content = f.read()
    selector = parsel.Selector(content)
    order_status = selector.css(".details-block__list dd:nth-child(4) span::text").getall()
    order_id = format_order_id(selector.css(".details-block__list dt:nth-child(1)::text").getall())
    order_time = format_time(selector.css(".details-block__list>:first-child+dd>time::attr(datetime)").getall())
    order_price = format_order_price(selector.css(".details-block__list dd:nth-child(2)::text").getall())
    deal_data(order_status, order_id, order_time, order_price)


def deal_data(order_status, order_id, order_time, order_price):
    order_list = []
    order_dict = {
        "order_time": "",
        "order_price": "",
        "order_id": "",
        "order_status": ""
    }
    for i in range(0, len(order_status)):
        order_dict["order_time"] = order_time[i]
        order_dict["order_price"] = order_price[i]
        order_dict["order_id"] = order_id[i]
        order_dict["order_status"] = order_status[i]
        order_list.append(order_dict)
        order_dict = {}
    print(order_list)

    pd_data_frame = pd.DataFrame(order_list)
    columns_map = {
        "order_time": "订单时间",
        "order_price": "订单金额",
        "order_id": "订单号",
        "order_status": "订单状态"
    }
    pd_data_frame.rename(columns=columns_map, inplace=True)
    pd_data_frame.to_excel("/Users/hugh/Desktop/订单.xlsx", index=False)


def format_order_id(order):
    order_id = []
    for o in order:
        order_id.append(o.replace("Order number ", ""))
    return order_id


def format_time(time):
    order_time = []
    for t in time:
        t = t.replace("T", " ").replace("+08:00", "")
        # order_time.append(datetime.strptime(t, "%Y-%m-%d %H:%M:%S"))
        order_time.append(t)
    return order_time


def format_order_price(price):
    new_order_price = []
    for o in price:
        if "HK$" in o:
            # 删除o里面的\n\t\t\t\t\t\tHK$9,500
            o = o.strip().replace("\\n\\t\\t\\t\\t\\t\\t", "")
            new_order_price.append(o)
    return new_order_price


if __name__ == '__main__':
    load_net_css_file()
