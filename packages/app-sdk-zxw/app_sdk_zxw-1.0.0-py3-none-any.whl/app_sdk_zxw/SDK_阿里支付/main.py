from alipay import AliPay, DCAliPay, ISVAliPay
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status, Request
from typing import List
from starlette.datastructures import FormData
from app_sdk_zxw.SDK_阿里支付.config import App1


class Alipay二次开发:
    alipay: AliPay
    _rootUrl = "http://0.0.0.0"  # 根地址
    _支付状态回调地址 = "/callback/alipay"

    def init(self, rootUrl, app: FastAPI, 支付成功func):
        self._rootUrl = rootUrl
        # 参数初始化
        self.alipay = AliPay(
            appid=App1.appid,
            app_private_key_string=App1.key应用私钥,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=App1.key支付宝公钥,
            app_notify_url=None,  # 默认回调url
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False  # 默认False
        )
        # 支付回调
        self._注册回调接口(app, 支付成功func)

    def 下单(self, orderID="订单号", price=0.01, 商品名称=""):
        # App支付，将order_string返回给app即可
        order_string = self.alipay.api_alipay_trade_app_pay(
            out_trade_no=orderID,
            total_amount=price,
            subject=商品名称,
            notify_url=self._rootUrl + self._支付状态回调地址
        )
        return order_string

    def 订阅(self):
        self.alipay.api_alipay_trade_app_pay()

    def 退款查询(self, orderID="商户订单号") -> bool:
        res = self.alipay.api_alipay_trade_fastpay_refund_query(orderID, out_trade_no=orderID)
        result = 退款查询返回结果pydantic(**res)
        if result.code == "10000":
            if result.msg == "Success":
                return True
        return False

    def 历史订单查询(self, 商户订单号):
        res = self.alipay.api_alipay_trade_query(out_trade_no=商户订单号)
        result = 订单查询pydantic(**res)
        # 订单存在
        if result.msg == "Success":
            # 付款成功
            if result.trade_status == "TRADE_SUCCESS":
                return True
            # 付款失败
            else:
                return result.trade_status
        # 订单不存在
        return result.sub_msg

    def _注册回调接口(self, app: FastAPI, 支付成功func):
        支付状态回调地址 = self._支付状态回调地址
        alipay = self.alipay

        @app.get(支付状态回调地址)
        async def 获取(request):
            print("支付回调get请求：", request)
            return "ok"

        @app.post(支付状态回调地址)
        async def 回调(postBody: Request):
            # 整理数据
            formData: FormData = await postBody.form()
            dataItemsList = formData.items()
            dataDict = {item[0]: item[1] for item in dataItemsList}
            # 校验数据
            dataPydantic = callback支付结果pydantic(**dataDict)
            data = dataPydantic.dict()
            #
            signature = data.pop("sign")
            # verify
            success = alipay.verify(data, signature)
            if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
                return await 支付成功func(dataPydantic)
            else:
                raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="支付失败")


#
# 定义 pydantic 数据结构
#

class callback支付结果pydantic(BaseModel):
    subject: str = "测试订单"
    gmt_payment: str = "2016-11-16 11:42:19"
    charset: str = "utf-8"
    seller_id: str = "xxxx"
    trade_status: str = "TRADE_SUCCESS"
    buyer_id: str = "xxxx"
    auth_app_id: str = "xxxx"
    buyer_pay_amount: str = "0.01"
    version: str = "1.0"
    gmt_create: str = "2016-11-16 11:42:18"
    trade_no: str = "xxxx"
    fund_bill_list: str = "[{\"amount\":\"0.01\",\"fundChannel\":\"ALIPAYACCOUNT\"}]"
    app_id: str = "xxxx"
    notify_time: str = "2016-11-16 11:42:19"
    point_amount: str = "0.00"
    total_amount: str = "0.01"
    notify_type: str = "trade_status_sync"
    out_trade_no: str = "xxxx"
    buyer_logon_id: str = "xxxx"
    notify_id: str = "xxxx"
    seller_email: str = "xxxx"
    receipt_amount: str = "0.01"
    invoice_amount: str = "0.01"
    sign: str = "xxx"


class 退款查询返回结果pydantic(BaseModel):
    code: str = '10000'
    msg: str = 'Success'
    out_request_no: str = '20171120'
    out_trade_no: str = '20171120'
    refund_amount: str = '20.00'
    total_amount: str = '20.00'
    trade_no: str = '2017112021001004070200297107'


class _订单查询_fund_bill_list(BaseModel):
    amount: str = "20.00"
    fund_channel: str = "ALIPAYACCOUNT"


class _订单查询_alipay_trade_query_response(BaseModel):
    trade_no: str = "2017032121001004070200176844"
    code: str = "10000"
    invoice_amount: str = "20.00"
    open_id: str = "20880072506750308812798160715407"
    fund_bill_list: List[_订单查询_fund_bill_list]
    buyer_logon_id: str = "csq***@sandbox.com"
    send_pay_date: str = "2017-03-21 13:29:17"
    receipt_amount: str = "20.00"
    out_trade_no: str = "out_trade_no15"
    buyer_pay_amount: str = "20.00"
    buyer_user_id: str = "2088102169481075"
    msg: str = "Success"
    point_amount: str = "0.00"
    trade_status: str = "TRADE_SUCCESS"
    total_amount: str = "20.00"


class 订单查询返回值pydantic(BaseModel):
    alipay_trade_query_response: _订单查询_alipay_trade_query_response
    sign: str


class 订单查询pydantic(BaseModel):
    code: str = '40004'
    msg: str = 'Business Failed'
    sub_code: str = 'ACQ.TRADE_NOT_EXIST'
    sub_msg: str = '交易不存在'
    buyer_pay_amount: str = '0.00'
    invoice_amount: str = '0.00'
    out_trade_no: str = '23131312'
    point_amount: str = '0.00'
    receipt_amount: str = '0.00'
    # success params
    buyer_logon_id: str = 'zxw***@gmail.com'
    buyer_user_id: str = '2088002912153711'
    send_pay_date: str = '2020-07-09 07:07:53'
    total_amount: str = '0.01'
    trade_no: str = '2020070922001453711429208912'
    trade_status: str = 'TRADE_SUCCESS'
