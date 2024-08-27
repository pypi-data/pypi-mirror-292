from setuptools import setup, find_packages

setup(
    name='zyjj_client_sdk',
    version='0.1.16',
    description='智游剪辑客户端sdk包',
    url='https://github.com/zyjj-cc/zyjj-client-sdk',
    author='zyjj',
    author_email='zyjj.cc@foxmail.com',
    license='MIT',
    long_description="智游剪辑客户端sdk包",
    packages=find_packages(),
    install_requires=[
        'requests~=2.31.0',
        'paho-mqtt~=1.6.1',
        'cos-python-sdk-v5~=1.9.26',  # 腾讯云cos
        'tencentcloud-sdk-python~=3.0.1090',  # 腾讯云SDK
        'graphviz~=0.20.3',  # 绘图
        'tenacity~=9.0.0',  # 重试框架
        'AudioSegment~=0.23.0',  # 音频分割
    ]
)
