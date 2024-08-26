from app_tools_zxw.SDK_微信.SDK_微信支付 import minipay

'''
注意设置minipay/config.py文件，配置正确的密匙。
'''

'''方法一'''
# 统一下单
# 必传参数
# out_trade_no
# openid
# body
# total_fee
unified = minipay.UnifiedOrder(
    out_trade_no=123123132,
    openid='mock openid',
    body='商品描述',
    total_fee=100
)
# 发起请求
response = unified.request()
# 根据 is_fail 或 is_success 判断业务是否成功
# unified.request()会返回一个响应
# if is fail,返回的是unified.error
# if is success,返回的是unified.response_data
# 不管是unified.error 还是unified.response_data
# 都是一个dict类型,其中unified.response_data包含了微信小程序返回的所有参数

if unified.is_fail:
    print('1', unified.error['code'], unified.error['desc'])
    print('2', response.get('code'), response.get('desc'))
elif unified.is_success:
    print('3', unified.response_data)
    print('4', response)

'''方法二'''

data = dict(out_trade_no=123123132, openid='mock openid', body='商品描述', total_fee=100)

unified = minipay.UnifiedOrder(**data)
unified.request()
if unified.is_fail:
    print('5', unified.error['code'], unified.error['desc'])
else:
    print('6', unified.response_data)
