from django.core.files.storage import Storage


class MyStorage(Storage):
    def _open(self, name, mode='rb'):
        """
        用于打开文件
        :param name: 要打开的文件的名字
        :param mode: 打开文件方式
        :return: None
        """
        # 打开文件时使用的，此时不需要，而文档告诉说明必须实现，所以pass
        pass

    def _save(self, name, content):
        """
        用于保存文件
        :param name: 要保存的文件名字
        :param content: 要保存的文件的内容
        :return: None
        """
        # 保存文件时使用的，此时不需要，而文档告诉说明必须实现，所以pass
    def url(self, name):
        return "http://192.168.0.103:8888/" + name
