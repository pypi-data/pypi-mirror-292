import os
import datetime
import hashlib
import base64
import hmac
import httpx
from requests_toolbelt import MultipartEncoder
from pydantic import BaseModel
import oss2
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo

# OSS账号密码
myAccessKeyID = ''
myAccessKeySecret = ''
myBucket名称 = "auto-weight-system-data-backup"
myEndpointUrl = "oss-cn-hangzhou.aliyuncs.com"


class 上传文件:
    __bucket名: str  # 文件夹名称
    __endpointUrl: str  # OSS服务地址
    __auth: oss2.Auth  # 权限class
    __bucket: oss2.Bucket  # 获取权限的文件夹class
    __accessKeyID: str
    __accessKeySecret: str

    # 覆写 - 用于动态获取OSS服务器
    @staticmethod
    def _动态生成endpointUrl(bucket名) -> str:
        pub_endpoint = 'oss-cn-shanghai.aliyuncs.com'
        pri_endpoint = 'oss-cn-hangzhou.aliyuncs.com'
        if bucket名 == "auto-weight-system-data-backup":
            return pri_endpoint
        else:
            return pub_endpoint

    #
    # ---- 以下不用覆写 -----
    #
    def __初始化(self, accessKeyID, accessKeySecret,
              bucket名='commodity-image', endpointUrl='oss-cn-hangzhou.aliyuncs.com'):
        #
        self.__bucket名 = bucket名
        self.__endpointUrl = endpointUrl
        self.__accessKeyID = accessKeyID
        self.__accessKeySecret = accessKeySecret

        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录RAM控制台创建RAM账号。
        self.__auth = oss2.Auth(self.__accessKeyID, self.__accessKeySecret)
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        self.__bucket = oss2.Bucket(self.__auth, endpointUrl, bucket名)

    #
    # 直接上传
    #
    def 直接上传(self, accessKeyID, accessKeySecret,
             bucket名, 云端文件名, 本地文件路径, 动态获取endpointUrl=True, endpointUrl=""):
        """
        __endpointUrl，动态获取endpointUrl 二选一
        """

        # 初始化
        if 动态获取endpointUrl is False and endpointUrl == "":
            raise ValueError("动态获取endpointUrl,endpointUrl必须有一项")
        if 动态获取endpointUrl and endpointUrl != "":
            raise ValueError("动态获取endpointUrl,endpointUrl只能有一项，不可两者兼具")
        if 动态获取endpointUrl:
            endpointUrl = self._动态生成endpointUrl(bucket名)
        self.__初始化(accessKeyID, accessKeySecret, bucket名, endpointUrl)

        #
        total_size = os.path.getsize(本地文件路径)
        # determine_part_size方法用于确定分片大小。
        part_size = determine_part_size(total_size, preferred_size=100 * 1024)

        # 初始化分片。
        # 如需在初始化分片时设置文件存储类型，请在init_multipart_upload中设置相关headers，参考如下。
        # headers = dict()
        # headers["x-oss-storage-class"] = "Standard"
        # upload_id = __bucket.init_multipart_upload(key, headers=headers).upload_id
        upload_id = self.__bucket.init_multipart_upload(云端文件名).upload_id
        parts = []

        # 逐个上传分片。
        with open(本地文件路径, 'rb') as fileobj:
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = self.__bucket.upload_part(云端文件名, upload_id, part_number,
                                                   SizedFileAdapter(fileobj, num_to_upload))
                parts.append(PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1

        # 完成分片上传。
        # 如需在完成分片上传时设置文件访问权限ACL，请在complete_multipart_upload函数中设置相关headers，参考如下。
        # headers = dict()
        # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
        # __bucket.complete_multipart_upload(key, upload_id, parts, headers=headers)
        self.__bucket.complete_multipart_upload(云端文件名, upload_id, parts)

        # 验证分片上传。
        with open(本地文件路径, 'rb') as fileobj:
            上传状态 = self.__bucket.get_object(云端文件名).read() == fileobj.read()
        return 上传状态

    #
    # 表单上传
    #
    class 上传权限model(BaseModel):
        policy: str
        Signature: str
        expiration: str
        OSSAccessKeyId: str
        host: str  # bucket名称.endpointUrl
        dir: str  #

    # 获取上传token : 用于app等上传，先获取权限
    # role_arn是角色的资源名称。
    # RoleArn = 'acs:ram::...:role/aliyunosstokengeneratorrole'
    def 获取上传权限(self, accessKeyID, accessKeySecret,
               bucket名, 动态获取endpointUrl=False, endpointUrl="") -> 上传权限model:
        # 初始化
        if 动态获取endpointUrl is False and endpointUrl == "":
            raise ValueError("动态获取endpointUrl,endpointUrl必须有一项")
        if 动态获取endpointUrl and endpointUrl != "":
            raise ValueError("动态获取endpointUrl,endpointUrl只能有一项，不可两者兼具")
        if 动态获取endpointUrl:
            endpointUrl = self._动态生成endpointUrl(bucket名)
        self.__初始化(accessKeyID, accessKeySecret, bucket名, endpointUrl)

        #
        def get_FormSignature(access_key_secret, expiration, fileMaxSize):
            def convert_base64(inputs):
                return base64.b64encode(inputs.encode('utf-8'))

            def get_sign_policy(key, policy):
                return base64.b64encode(hmac.new(key, policy, hashlib.sha1).digest())

            # 1 构建一个Post Policy
            policy = "{\"expiration\":\"%s\",\"conditions\":[[\"content-length-range\", 0, %i]]}" \
                     % (expiration, fileMaxSize)
            # print("policy: %s" % policy)
            # 2 将Policy字符串进行base64编码
            base64policy = convert_base64(policy)
            # print("base64_encode_policy: %s" % base64policy)
            # 3 用OSS的AccessKeySecret对编码后的Policy进行签名
            signature = get_sign_policy(access_key_secret.encode('utf-8'), base64policy)
            return {'policy': base64policy.decode('utf-8'), 'Signature': signature.decode('utf-8')}

        # 生成token
        expiration = oss2.date_to_iso8601(datetime.datetime.now() + datetime.timedelta(minutes=15))
        fileMaxSize = 100 * 1024 * 1024
        formToken = get_FormSignature(self.__accessKeySecret, expiration, fileMaxSize)
        formToken['expiration'] = expiration
        formToken['OSSAccessKeyId'] = self.__accessKeyID

        # 修改token内容
        if 动态获取endpointUrl:
            endpointUrl = self._动态生成endpointUrl(self.__bucket名)
        else:
            endpointUrl = self.__endpointUrl

        formToken['host'] = self.__bucket名 + '.' + endpointUrl
        formToken['dir'] = ''

        return self.上传权限model(**formToken)

    @staticmethod
    def 表单上传(云端文件名: str, 待上传文件路径: str, 上传权限: 上传权限model) -> str:
        data = 上传权限.dict()
        data["key"] = 云端文件名
        m = MultipartEncoder(
            fields={**data,
                    'filename': 云端文件名,
                    'version': '10001',
                    'file': ('test01.xlsx', open(待上传文件路径, 'rb'),
                             'application/octet-stream')
                    }
        )
        headers = {"Content-Type": m.content_type}
        #
        res = httpx.post(url=f'http://{上传权限.host}', data=m.to_string(), headers=headers)
        #
        if res.text == '':
            return 'true'
        else:
            return res.text


if __name__ == '__main__':
    tmp = 上传文件()
    token = tmp.获取上传权限(myAccessKeyID, myAccessKeySecret, myBucket名称, 动态获取endpointUrl=True)
    res1 = tmp.表单上传("test/hahaha.txt",
                    "/Users/zhangxuewei/Documents/GitHub/CoWork_VueFront_CaiWu/pyAutoWeigh/requirements.txt", token)
