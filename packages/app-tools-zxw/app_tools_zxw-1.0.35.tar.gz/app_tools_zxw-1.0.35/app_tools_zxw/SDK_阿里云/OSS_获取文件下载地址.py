from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest  # pip install aliyun-python-sdk-sts
import json
import oss2
import time
import calendar

'''
***************高级功能***************
###
### 使用STS进行临时授权
STS应用完整的示例代码请参见GitHub。
您可以通过STS（Security Token Service）进行临时授权访问。更多有关STS的内容请参见访问控制API参考（STS）中的简介。
关于账号及授权的详细信息请参见最佳实践中的STS临时授权访问。
首先您需要安装官方的Python STS客户端：pip install aliyun-python-sdk-sts
'''

accessKeyID = ''
accessKeySecret = ''


# 单条获取 - 仅用于方便理解思路
# # 假设你的Bucket处于杭州区域
def get_Url(bucket名='commodity-image',
            region_id='cn-hangzhou',
            endpoint='oss-cn-shanghai.aliyuncs.com',
            method='GET',
            fileName='',
            失效时间_秒=20):
    t1 = time.time()

    # role_arn是角色的资源名称。
    RoleArn = 'acs:ram::1314717226629429:role/aliyunosstokengeneratorrole'

    # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。
    # 强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    clt = client.AcsClient(accessKeyID, accessKeySecret, region_id)
    req = AssumeRoleRequest.AssumeRoleRequest()

    t2 = time.time() - t1
    print('t2：', t2)

    # 设置返回值格式为JSON。
    req.set_accept_format('json')
    req.set_RoleArn(RoleArn)
    req.set_RoleSessionName('session-name')
    body = clt.do_action_with_exception(req)
    # print(body)
    # 使用RAM账号的AccessKeyId和AccessKeySecret向STS申请临时token。
    token = json.loads(body.decode('utf-8'))

    t3 = time.time() - t1 - t2
    print('t3：', t3)

    # 使用临时token中的认证信息初始化StsAuth实例。
    auth = oss2.StsAuth(token['Credentials']['AccessKeyId'],
                        token['Credentials']['AccessKeySecret'],
                        token['Credentials']['SecurityToken'])
    # print(__auth.__auth())

    # t4 = time.time() - t1-t2-t3
    # print('t4：',t4)

    # 使用StsAuth实例初始化存储空间。
    bucket = oss2.Bucket(auth, endpoint, bucket名)

    '''  
    #######  使用签名Url上传文件  #######  
    '''
    # 生成请求Url
    url = bucket.sign_url(method=method, key=fileName, expires=失效时间_秒)

    t6 = time.time() - t1 - t2 - t3
    print('t6：', t6)
    t1 = 0
    t2 = 0
    t3 = 0
    t4 = 0
    t5 = 0
    t6 = 0

    return url


# 批量获取 - 性能优化
class 获取文件下载地址:
    def __init__(self, bucket名='commodity-image',
                 region_id='cn-hangzhou',
                 endpoint='oss-cn-shanghai.aliyuncs.com'):
        # 关键信息存为公共变量
        self.bucket名 = bucket名
        self.region_id = region_id
        self.endpoint = endpoint

        # role_arn是角色的资源名称。
        RoleArn = 'acs:ram::1314717226629429:role/aliyunosstokengeneratorrole'

        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。
        # 强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        clt = client.AcsClient(accessKeyID,
                               accessKeySecret,
                               region_id)
        req = AssumeRoleRequest.AssumeRoleRequest()

        # 设置返回值格式为JSON。
        req.set_accept_format('json')
        req.set_RoleArn(RoleArn)
        req.set_RoleSessionName('session-name')
        req.set_DurationSeconds(60 * 60)  # 设置权限过期时间，最小值15*60，最大值3600（秒）
        body = clt.do_action_with_exception(req)
        # 使用RAM账号的AccessKeyId和AccessKeySecret向STS申请临时token。
        self.token = json.loads(body.decode('utf-8'))

        # 使用临时token中的认证信息初始化StsAuth实例。
        auth = oss2.StsAuth(self.token['Credentials']['AccessKeyId'],
                            self.token['Credentials']['AccessKeySecret'],
                            self.token['Credentials']['SecurityToken'])
        # print(__auth.__auth())
        # 使用StsAuth实例初始化存储空间。
        self.bucket = oss2.Bucket(auth, endpoint, bucket名)

    def get_Url(self, method='GET', fileName='', 失效时间_秒=20):
        # 将格式字符串转换为时间戳
        过期时间 = self.token['Credentials']['Expiration']  # "2019-12-04T02:19:59Z"
        expireTime = calendar.timegm(time.strptime(过期时间, "%Y-%m-%dT%H:%M:%SZ"))

        # 授权过期，重新申请STS授权
        if expireTime < time.time():
            self.__init__(bucket名=self.bucket名, region_id=self.region_id, endpoint=self.endpoint)
        # else:
        # print(过期时间,time.asctime(time.gmtime(expireTime)))

        # 生成请求Url
        url = self.bucket.sign_url(method=method, key=fileName, expires=失效时间_秒)
        return url


if __name__ == '__main__':
    # 测试性能
    fileobj = 获取文件下载地址()
    for i in range(1000):
        if i % 10 == 0: print(i)
        fileobj.get_Url()
