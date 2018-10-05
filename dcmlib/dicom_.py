# coding=utf-8
import bisect
import copy
import re
import time
import warnings

from dicom._dicom_dict import DicomDictionary
from dicom.datadict import dictionaryVR

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=UserWarning)
    import dicom.filebase
    from dicom import read_file
    from dicom.dataset import Dataset, FileDataset

KNOWN_TAGS = set(DicomDictionary.keys())
DICOM_TAGS_MAP = {v[-1]: k for k, v in DicomDictionary.iteritems()}


def get_tag_value(ds, tag_a, tag_b, default=None):
    """
    获取dataset
    :param ds: Dataset 待获取对象dataset
    :param tag_a: int 第一级tag十六进制数
    :param tag_b: int 第二级tag十六进制数
    :param default: object 缺省返回
    :return: object
    """
    val = ds.get((tag_a, tag_b), default=default)
    if hasattr(val, 'value'):
        return val.value
    else:
        return val


def get_named_tag_value(ds, tagname, default=None):
    """
    获取命名标签的值
    :param ds: Dataset dicom对象
    :param tagname: str 标签名
    :param default: 缺省返回
    :return 内置类型
    """
    loc = tag_name2locator(tagname)
    return get_tag_value(ds, loc[0], loc[1], default=default)


def get_unknown_tags(ds):
    """
    获取dataset中的未知标签
    
    如果dicom中有这种标签, 保存会报错, 所以需要抹掉
    :param ds: Dataset
    :return: tuple 此dataset中的未知标签
    """
    mask_keys = set(ds.keys()) - KNOWN_TAGS
    unknown_tags = []
    for tag in mask_keys:
        try:
            dictionaryVR(tag)
        except KeyError:
            if not tag.is_private and not tag.element == 0:
                bisect.insort(unknown_tags, tag)
    return tuple(unknown_tags)


def monkey_patch_dicom():
    """
    修正dicom中DicomFileLike对象不释放内存问题
    """
    if hasattr(dicom.filebase.DicomIO, '__del__'):
        del dicom.filebase.DicomIO.__del__


def dcm2array(ds, reverse=False):
    """
    dcm文件转为二维数组
    :param ds: DataSet dicom对象
    :param reverse: bool 是否翻颜色
    :return : array 二维数组
    """
    import numpy as np
    center = ds.WindowCenter
    width = ds.WindowWidth
    low = center - width / 2
    pixel_data = ds.pixel_array
    shape = pixel_data.shape
    pixel_data = np.fromstring(pixel_data, dtype=np.uint16)
    pixel_data = pixel_data.reshape(shape)
    pixel_data = (pixel_data - low) / width * 256
    if reverse:
        pixel_data = 256 - pixel_data
    pixel_data[pixel_data < 0] = 0
    pixel_data[pixel_data > 256] = 256
    return pixel_data


def dcm_file2jpeg_file(dicom_path, out_path, reverse=False):
    """
    dcm 转化 jpeg
    :param dicom_path: str dicom路径
    :param out_path: str 输出jepg路径
    :param reverse: bool 是否翻颜色
    """
    ds = read_file(dicom_path, force=True)
    pixel_data = dcm2array(ds, reverse=reverse)
    from cv2.cv2 import imwrite
    imwrite(out_path, pixel_data)


def make_up_file_dataset(filename, ds,
                         implement_instance_uid='1.2.826.0.1.3680043.9.6991'):
    """
    把裸Dataset对象ds装载为可以存储的FileDataSet对象.
    :param filename: str 文件名
    :param ds: Dataset dicom对象
    :param implement_instance_uid: str icoom 中的 file_meta部分的实例实现的前缀, 需自行申请的前缀, 随意写也不会影响使用
    :return: FileDataset 可保存的dataset对象
    """
    meta = Dataset()
    meta.MediaStorageSOPClassUID = ds.SOPClassUID
    meta.MediaStorageSOPInstanceUID = ds[0x0008, 0x0018].value
    meta.ImplementationClassUID = implement_instance_uid
    fds = FileDataset(filename, {}, file_meta=meta, preamble=b"\0" * 128)
    fds.update(ds)

    fds.is_little_endian = True
    fds.is_implicit_VR = True
    return fds


def eval_filter(expression):
    """
    读取filter表达式, 对
    :param expression: str 过滤表达式
    :return: func, [str]
    """
    ds_attrs = list(set(re.findall(r'(\$\(.*?\))', expression)))
    attr_exps = []
    tag_names = []
    for ds_attr in ds_attrs:
        tag_name = ds_attr[2:-1]
        loc = tag_name2locator(tag_name)
        tag_names.append(tag_name)
        attr_exps.append('get_tag_value(ds, %s, %s, "")' % loc)
    eval_exp = 'lambda ds: ' + copy.copy(expression)
    for i in range(len(ds_attrs)):
        eval_exp = eval_exp.replace(ds_attrs[i], attr_exps[i])
    _f = eval(eval_exp, {'get_tag_value': get_tag_value}, {})

    def ds_filter(ds):
        rtn = bool(_f(ds))
        return rtn

    return ds_filter, tag_names


def tag_name2locator(tag_name):
    """
    标签名转tag定位符
    :param tag_name: str
    :return: tuple(int, int)
    """
    loc = DICOM_TAGS_MAP.get(tag_name)
    if not loc:
        raise ValueError('%s is not a valid tag' % tag_name)
    loc = loc >> 16, loc & 0xffff
    return loc


def tag_name2tag_getter(tag_name, default=None):
    """
    获取根据标签名获取属性值的函数的函数
    :param tag_name: str 标签名
    :return: func
    """
    loc = tag_name2locator(tag_name)

    def tag_getter(ds):
        return get_tag_value(ds, loc[0], loc[1], default)

    return tag_getter


def make_uid(seed=None):
    if not seed:
        seed = time.stam
    return '1.2.199.3.2.26.%s.1' % hash(seed)


def fix_dicom(ds, pat_seed, study_seed, series_seed):
    """
    修正dicom
    :param ds:
    :param pat_seed:
    :param study_seed:
    :param series_seed:
    :return:
    """
    if not get_named_tag_value(ds, "PatientID"):
        ds.PatientID = str(pat_seed)
    if not get_named_tag_value(ds, "StudyInstanceUID"):
        ds.StudyInstanceUID = make_uid(study_seed)
    if not get_named_tag_value(ds, "SeriesInstanceUID"):
        ds.SeriesInstanceUID = make_uid(series_seed)
    for tag in get_unknown_tags(ds):
        del ds[tag.group, tag.element]
    # 为pydicom修复
    if (get_tag_value(ds, 0x28, 0x101) != get_tag_value(ds, 0x28, 0x100)
            and get_tag_value(ds, 0x28, 0x103, 0) == 1):
        pixel_array_transformed = (ds.pixel_array |
                                   (ds.pixel_array >> (int(ds.BitsStored) - 1))
                                   * ((1 << (int(ds.BitsAllocated)
                                             - int(ds.BitsStored))) - 1)
                                   << (int(ds.BitsStored)))
        ds.PixelData = pixel_array_transformed.tostring()
        ds.BitsStored = ds.BitsAllocated
        ds.HighBit = int(ds.BitsAllocated) - 1
    return ds
